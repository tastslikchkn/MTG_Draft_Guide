"""
Centralized API clients for MTG Draft Guide scripts.
Provides reusable HTTP client wrappers for Scryfall and JustTCG APIs.
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, Dict, Any, List
from pathlib import Path


# ============================================================================
# API CONFIGURATION
# ============================================================================

import os

SCRYFALL_BASE_URL = "https://api.scryfall.com"
JUSTTCG_BASE_URL = "https://api.justtcg.com/v1"
USER_AGENT = "MTG_Draft_Guide/1.0 (by tastslikchkn)"

# Load JustTCG credentials from environment variables
JUSTTCG_API_KEY = os.getenv('JUSTTCG_API_KEY', '')
JUSTTCG_GAME_ID = os.getenv('JUSTTCG_GAME_ID', 'magic-the-gathering')


# ============================================================================
# HTTP CLIENT HELPER
# ============================================================================

def make_request(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Make an HTTP GET request with retry logic and proper error handling.
    
    Args:
        url: The URL to fetch
        headers: Optional custom headers (User-Agent added automatically)
        timeout: Request timeout in seconds
        retries: Number of retry attempts on failure
        
    Returns:
        Parsed JSON response as dict, or None on failure
    """
    # Ensure User-Agent is always set
    if headers is None:
        headers = {}
    if 'User-Agent' not in headers:
        headers['User-Agent'] = USER_AGENT
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # Resource not found - no point retrying
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    
    return None


# ============================================================================
# SCRYFALL API CLIENT
# ============================================================================

def fetch_card_by_name(
    card_name: str,
    format_type: str = "normal"
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single card from Scryfall by name.
    
    Args:
        card_name: The card name to search for
        format_type: Image format (normal, art_crop, etc.)
        
    Returns:
        Card data dict or None if not found
    """
    url = f"{SCRYFALL_BASE_URL}/cards/named?fuzzy={urllib.parse.quote(card_name)}&format={format_type}"
    return make_request(url)


def fetch_card_image_url(
    card_name: str,
    size: str = "normal"
) -> Optional[str]:
    """
    Get the image URL for a card from Scryfall.
    
    Args:
        card_name: The card name
        size: Image size (small, normal, large, art_crop, border_crop)
        
    Returns:
        Image URL or None if card not found
    """
    card_data = fetch_card_by_name(card_name)
    if card_data and 'image_uris' in card_data:
        return card_data['image_uris'].get(size)
    return None


def download_card_image(
    card_name: str,
    output_dir: Path,
    size: str = "normal"
) -> Optional[Path]:
    """
    Download a card image from Scryfall to local storage.
    
    Args:
        card_name: The card name
        output_dir: Directory to save the image
        size: Image size (small, normal, large)
        
    Returns:
        Path to downloaded file, or None on failure
    """
    from .card_data import sanitize_filename
    
    image_url = fetch_card_image_url(card_name, size)
    if not image_url:
        return None
    
    filename = sanitize_filename(card_name) + ".png"
    filepath = output_dir / filename
    
    try:
        urllib.request.urlretrieve(image_url, filepath)
        if filepath.stat().st_size > 0:
            return filepath
    except Exception as e:
        print(f"    ✗ Error downloading {card_name}: {e}")
    
    return None


def search_cards(
    query: str,
    unique: str = "cards",
    order: str = "set"
) -> Optional[Dict[str, Any]]:
    """
    Search Scryfall card database.
    
    Args:
        query: Scryfall search query string
        unique: Filter by cards or spells
        order: Sort order (set, name, etc.)
        
    Returns:
        Search results dict or None on failure
    """
    url = f"{SCRYFALL_BASE_URL}/cards/search?q={urllib.parse.quote(query)}&unique={unique}&order={order}"
    return make_request(url)


# ============================================================================
# JUSTTCG API CLIENT  
# ============================================================================

def fetch_card_by_name_justtcg(
    card_name: str,
    timeout: int = 15
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single card by name from JustTCG API.
    
    Args:
        card_name: The card name to search for
        timeout: Request timeout in seconds
        
    Returns:
        Card data dict or None if not found/error
    """
    if not JUSTTCG_API_KEY:
        print("Warning: JustTCG API key not configured")
        return None
    
    url = f"{JUSTTCG_BASE_URL}/cards?game={JUSTTCG_GAME_ID}&q={urllib.parse.quote(card_name)}"
    
    headers = {
        'X-API-Key': JUSTTCG_API_KEY,
        'Accept': 'application/json',
        'User-Agent': USER_AGENT
    }
    
    return make_request(url, headers=headers, timeout=timeout)


def extract_price_data(api_response: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Extract price data from JustTCG API response.
    
    Args:
        api_response: Raw JSON response from JustTCG
        
    Returns:
        Dict with avg_price_7d, min_price, max_price or None if no prices found
    """
    if not api_response or 'data' not in api_response:
        return None
    
    cards = api_response.get('data', [])
    if not cards:
        return None
    
    # Get first matching card's price data
    card = cards[0]
    prices = card.get('prices', {})
    
    if not prices:
        return None
    
    return {
        'avg_price_7d': prices.get('avg_price_7d'),
        'min_price': prices.get('min_price'),
        'max_price': prices.get('max_price'),
        'source': 'justtcg'
    }


# ============================================================================
# BATCH OPERATIONS WITH RATE LIMITING
# ============================================================================

def batch_download_images(
    card_names: List[str],
    output_dir: Path,
    rate_limit: float = 1.0,
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Download multiple card images with rate limiting.
    
    Args:
        card_names: List of card names to download
        output_dir: Directory to save images
        rate_limit: Seconds between requests (default 1.0 for Scryfall)
        show_progress: Whether to print progress updates
        
    Returns:
        Dict with success_count, failed_cards, total_time
    """
    import time as time_module
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    failed_cards = []
    start_time = time_module.time()
    
    if show_progress:
        print(f"\n⬇️  Starting downloads ({len(card_names)} cards)...")
        print("-" * 50)
    
    for i, card_name in enumerate(card_names, 1):
        if show_progress:
            print(f"[{i}/{len(card_names)}] {card_name}")
        
        result = download_card_image(card_name, output_dir)
        
        if result:
            success_count += 1
            if show_progress:
                size_kb = result.stat().st_size / 1024
                print(f"    ✓ Saved: {result.name} ({size_kb:.1f} KB)")
        else:
            failed_cards.append(card_name)
            if show_progress:
                print(f"    ✗ Failed to download")
        
        # Rate limiting
        time_module.sleep(rate_limit)
    
    elapsed = time_module.time() - start_time
    
    return {
        'success_count': success_count,
        'failed_cards': failed_cards,
        'total_time': elapsed
    }
