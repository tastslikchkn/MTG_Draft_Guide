"""
Centralized API clients for MTG Draft Guide scripts.
Provides reusable HTTP client wrappers for Scryfall and JustTCG APIs.
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Any
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
    headers: dict[str, str] | None = None,
    timeout: int = 15,
    retries: int = 3
) -> dict[str, Any] | None:
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
) -> dict[str, Any] | None:
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
) -> str | None:
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
) -> Path | None:
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
) -> dict[str, Any] | None:
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
) -> dict[str, Any] | None:
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


# ============================================================================
# PRICE EXTRACTION (Unified)
# ============================================================================

def extract_price_data(api_response: dict[str, Any] | None) -> dict[str, Any] | None:
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


def get_avg_price_from_cache(card_data: dict[str, Any]) -> float | None:
    """
    Extract average price from cached card data.
    
    Handles both JustTCG nested structure and flat USD format.
    
    Args:
        card_data: Card dictionary with optional 'prices' key
        
    Returns:
        Average price as float, or None if not available
    """
    prices = card_data.get('prices', {})
    if not prices:
        return None
    
    # Try JustTCG nested structure first: prices['prices'][key]['avg_price_7d']
    if 'prices' in prices and isinstance(prices['prices'], dict):
        for key in ['near_mint_normal', 'near_mint_foil']:
            price_data = prices['prices'].get(key, {})
            avg_price = price_data.get('avg_price_7d')
            if avg_price is not None:
                try:
                    return float(avg_price)
                except (ValueError, TypeError):
                    pass
        # Fallback to any available price in nested structure
        for key, price_data in prices['prices'].items():
            avg_price = price_data.get('avg_price_7d')
            if avg_price is not None:
                try:
                    return float(avg_price)
                except (ValueError, TypeError):
                    pass
    
    # Try flat USD format: prices['usd']
    usd_price = prices.get('usd')
    if usd_price is not None:
        try:
            return float(usd_price)
        except (ValueError, TypeError):
            pass
    
    # Try direct avg_price_7d at top level
    avg_price = prices.get('avg_price_7d')
    if avg_price is not None:
        try:
            return float(avg_price)
        except (ValueError, TypeError):
            pass
    
    return None


# ============================================================================
# BATCH OPERATIONS WITH RATE LIMITING
# ============================================================================

def batch_download_images(
    card_names: list[str],
    output_dir: Path,
    rate_limit: float = 1.0,
    show_progress: bool = True
) -> dict[str, Any]:
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


def fetch_set_cards(
    set_code: str,
    unique: str = 'cards',
    order: str = 'set'
) -> dict[str, Any]:
    """
    Fetch all cards from a Magic: The Gathering set via Scryfall API.
    
    Handles pagination automatically and deduplicates by card name.
    
    Args:
        set_code: The set code (e.g., 'mkm' for Murders at Castle Whispers)
        unique: Scryfall unique parameter ('cards', 'prints', etc.)
        order: Sort order ('set', 'name', etc.)
        
    Returns:
        Dict with:
            - data: List of card dictionaries
            - total_cards: Total number of unique cards found
            - has_more: Whether more pages exist (should be False)
            
    Example:
        >>> result = fetch_set_cards('mkm')
        >>> print(f"Found {result['total_cards']} cards")
        Found 307 cards
    """
    seen_names = set()
    all_cards = []
    page = 1
    
    while True:
        url = f"https://api.scryfall.com/cards/search?q=e%3A{set_code}+order%3A{order}&page={page}&unique={unique}"
        
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            new_cards_count = 0
            for card in data.get('data', []):
                if card['name'] not in seen_names:
                    seen_names.add(card['name'])
                    all_cards.append(card)
                    new_cards_count += 1
            
            has_more = data.get('has_more', False)
            if not has_more or len(data.get('data', [])) == 0:
                break
            
            page += 1
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
            raise
    
    return {
        'data': all_cards,
        'total_cards': len(all_cards),
        'has_more': False
    }

"""
Card Evaluation Module
=====================
Calculates power levels and draft priority scores for MTG cards in Limited formats.
Based on the fundamental formula: Power + Toughness ≈ 2 × CMC
"""

# Keyword ability values (CMC reduction equivalents)
KEYWORD_VALUES = {
    # Offensive keywords
    'flying': 0.75,
    'haste': 0.5,
    'trample': 0.75,
    'first_strike': 0.5,
    'double_strike': 2.25,
    
    # Defensive keywords
    'vigilance': 0.75,
    'indestructible': 2.5,
    'hexproof': 0.75,
    'shroud': 0.75,
    'protection': 0.5,
    
    # Combo keywords
    'lifelink': 0.75,
    'deathtouch': 0.75,
    'reach': 0.4,
    
    # Other valuable abilities
    'menace': 1.0,  # Flying + Trample combo
    'shadow': 0.5,  # Can only be blocked by shadow creatures
}

# Expected power level ranges by rarity (Limited formats)
# Cards exceeding these are "value" picks; cards below are "flops"
RARITY_POWER_BASELINES = {
    'common': {'min': -1.5, 'max': 0.5, 'bomb_threshold': 1.2},
    'uncommon': {'min': -0.5, 'max': 1.2, 'bomb_threshold': 1.8},
    'rare': {'min': 0.2, 'max': 2.0, 'bomb_threshold': 2.5},
    'mythic': {'min': 0.8, 'max': 3.0, 'bomb_threshold': 3.0},
}

# Bomb indicators - cards with these traits often win games single-handedly
BOMB_INDICATORS = {
    'low_cmc_high_pt': {'max_cmc': 2, 'min_power_level': 1.5},  # Efficient threats
    'game_ending_keywords': ['indestructible', 'double_strike', 'menace'],
    'evasive_strikers': {'has_flying_or_reach': True, 'has_haste': True, 'max_cmc': 3},
}

def get_card_keywords(card: dict) -> list[str]:
    """
    Extract keyword abilities from a card's Oracle text.
    
    Args:
        card: Card dictionary with 'oracle_text' field
        
    Returns:
        List of recognized keyword ability strings (lowercase)
    """
    oracle_text = card.get('oracle_text', '').lower()
    found_keywords = []
    
    for keyword in KEYWORD_VALUES.keys():
        if keyword in oracle_text:
            found_keywords.append(keyword)
    
    return found_keywords


def calculate_creature_power_level(card: dict) -> float:
    """
    Calculate power level for a creature card.
    
    Uses the fundamental formula: Power + Toughness ≈ 2 × CMC
    Then adds keyword ability values.
    
    Args:
        card: Card dictionary with 'cmc', 'power', 'toughness', and 'oracle_text'
        
    Returns:
        Float representing power level (higher = stronger)
        - Positive values indicate overpowered cards
        - Negative values indicate underpowered cards  
        - Values near 0 indicate fair value
        - Returns None if power/toughness not available in card data
        
    Example:
        >>> card = {'cmc': 3, 'power': 4, 'toughness': 4, 'oracle_text': 'Flying'}
        >>> calculate_creature_power_level(card)
        2.75  # 8 P/T vs expected 6 (+2) + Flying (0.75) = 2.75
    """
    cmc = card.get('cmc', 0)
    power_str = card.get('power')
    
    try:
        power = float(power_str) if power_str is not None else 0.0
    except ValueError:
        power = 0.0
        
    try:
        toughness_str = card.get('toughness')
        toughness = float(toughness_str) if toughness_str is not None else 0.0
    except ValueError:
        toughness = 0.0

    if power is None or toughness is None: # This check won't be hit due to defaults, but kept for safety
         return None

    base_power = (power + toughness) - (2 * cmc)
    keyword_bonus = sum(KEYWORD_VALUES.get(kw, 0) for kw in get_card_keywords(card))
    
    return base_power + keyword_bonus


def calculate_spell_power_level(card: dict) -> float:
    """
    Calculate power level for a spell card (non-creature).
    
    Spell power is primarily driven by CMC and immediate impact.
    
    Args:
        card: Card dictionary with 'cmc' and 'oracle_text'
        
    Returns:
        Float representing utility value
    """
    cmc = card.get('cmc', 0)
    if cmc == 0: return 1.0 # Free spells are highly valued
    
    base_value = 1.0 / cmc
    keyword_bonus = sum(KEYWORD_VALUES.get(kw, 0) for kw in get_card_keywords(card))
    
    return base_value + keyword_bonus


def get_power_level_tier(power_level: float) -> str:
    """
    Categorize power level into a readable tier.
    """
    if power_level > 2.0: return 'Legendary/Bomb'
    if power_level > 1.0: return 'Strong/High Impact'
    if power_level >= 0: return 'Fair/Playable'
    return 'Weak/Low Impact'


def calculate_draft_priority_score(card: dict) -> float:
    """
    Calculate a composite draft priority score for any card.
    Combines power level and rarity influence.
    """
    if 'power' not in card and 'toughness' not in card:
        # It's likely a spell or land
        p_level = calculate_spell_power_level(card)
    else:
        p_level = calculate_creature_power_level(card)
        
    rarity_mod = {
        'mythic': 1.5,
        'rare': 1.2,
        'uncommon': 1.0,
        'common': 0.8,
        'special': 1.3,
        'land': 0.9
    }.get(card.get('rarity', 'common'), 0.8)
    
    return p_level * rarity_mod


def calculate_power_level(card: dict) -> float:
    """
    Calculate power level for any card (dispatcher function).
    
    Automatically detects whether the card is a creature or spell
    and calls the appropriate evaluation function.
    
    Args:
        card: Card dictionary with 'cmc' field, plus either:
              - 'power' and 'toughness' for creatures
              - or just 'oracle_text' for spells/lands
              
    Returns:
        Float representing power level (higher = stronger)
        
    Example:
        >>> creature = {'cmc': 3, 'power': 4, 'toughness': 4, 'oracle_text': 'Flying'}
        >>> calculate_power_level(creature)
        2.75
        
        >>> spell = {'cmc': 1, 'oracle_text': 'Deal 3 damage'}
        >>> calculate_power_level(spell)
        1.0
    """
    if card.get('power') is not None or card.get('toughness') is not None:
        return calculate_creature_power_level(card)
    else:
        return calculate_spell_power_level(card)


def add_card_evaluations(card_list: list[dict]) -> list[dict]:
    """
    Attach calculated power levels and tiers to a list of card dictionaries.
    """
    for card in card_list:
        p_level = calculate_draft_priority_score(card)
        card['power_level'] = p_level
        card['tier'] = get_power_level_tier(p_level)
    return card_list


def calculate_value_score(card: dict) -> float:
    """
    Calculate how much a card exceeds (or falls short of) its rarity's expected power level.
    
    A positive value score means the card is a "value pick" - it outperforms expectations.
    A negative value score means the card underperforms its rarity tier.
    
    Formula: Value Score = Power Level - Expected Max for Rarity
    
    Args:
        card: Card dictionary with 'power_level' and 'rarity' fields
        
    Returns:
        Float representing value over/under performance
        - High positive (>1.0): Hidden gem, steal at this rarity
        - Slightly positive (0-1.0): Solid pick for rarity
        - Near zero (-0.5 to 0): Fair value, meets expectations  
        - Negative (<-0.5): Underperforms rarity, potential flop
        
    Example:
        >>> # A common with power_level of 2.0 (rare territory)
        >>> card = {'rarity': 'common', 'power_level': 2.0}
        >>> calculate_value_score(card)
        1.5  # Exceeds common max (0.5) by 1.5 - hidden gem!
    """
    rarity = card.get('rarity', 'common').lower()
    power_level = card.get('power_level', 0)
    
    baseline = RARITY_POWER_BASELINES.get(rarity, RARITY_POWER_BASELINES['common'])
    expected_max = baseline['max']
    
    # Value score: how much does this card exceed rarity expectations?
    value_score = power_level - expected_max
    
    return round(value_score, 2)


def identify_bomb(card: dict) -> tuple[bool, str]:
    """
    Determine if a card qualifies as a "bomb" - a game-winning threat.
    
    Bombs are characterized by:
    1. High power level relative to their CMC (efficiency)
    2. Game-ending keywords or abilities
    3. Low mana cost with high impact
    
    Args:
        card: Card dictionary with evaluation fields
        
    Returns:
        Tuple of (is_bomb: bool, reason: str)
        
    Bomb Categories:
        - "efficient_threat": Low CMC (≤2) with high power level (≥1.5)
        - "game_ending_keyword": Has indestructible, double strike, or menace
        - "evasive_striker": Flying/Reach + Haste at low CMC (≤3)
        - "raw_power": Exceeds rarity's bomb threshold
    """
    cmc = card.get('cmc', 4)
    power_level = card.get('power_level', 0)
    rarity = card.get('rarity', 'common').lower()
    oracle_text = card.get('oracle_text', '').lower()
    
    # Check 1: Efficient threat (low CMC, high P/T ratio)
    if cmc <= 2 and power_level >= 1.5:
        return True, "efficient_threat"
    
    # Check 2: Game-ending keywords
    for keyword in BOMB_INDICATORS['game_ending_keywords']:
        if keyword in oracle_text:
            return True, f"game_ending_keyword_{keyword}"
    
    # Check 3: Evasive striker (flying/reach + haste at low CMC)
    has_evasion = 'flying' in oracle_text or 'reach' in oracle_text
    has_haste = 'haste' in oracle_text
    if has_evasion and has_haste and cmc <= 3:
        return True, "evasive_striker"
    
    # Check 4: Exceeds rarity bomb threshold
    baseline = RARITY_POWER_BASELINES.get(rarity, RARITY_POWER_BASELINES['common'])
    if power_level >= baseline['bomb_threshold']:
        return True, "raw_power"
    
    return False, ""


def classify_card_value(card: dict) -> tuple[str, str]:
    """
    Classify a card into value categories for draft guide display.
    
    Categories:
        - "HIDDEN_GEM": Common/uncommon exceeding expectations (value_score >= 0.4)
        - "BOMB": Game-winning threat identified by identify_bomb()
        - "STAPLE": Reliable pick within expected rarity range (value_score 0.2 to 0.4)
        - "SOLID": Slightly above average (value_score 0 to 0.2)
        - "FAIR": Meets basic expectations for rarity (value_score -0.3 to 0)
        - "FLOP": Rare/mythic underperforming expectations (value_score < -1.0)
        - "JUNK": Significantly underpowered (power_level < -2.0)
    
    Args:
        card: Card dictionary with evaluation fields
        
    Returns:
        Tuple of (category: str, description: str)
    """
    value_score = calculate_value_score(card)
    power_level = card.get('power_level', 0)
    rarity = card.get('rarity', 'common').lower()
    is_bomb, bomb_reason = identify_bomb(card)
    
    # Bombs take priority
    if is_bomb:
        return "BOMB", f"Game-winning threat ({bomb_reason})"
    
    # Hidden gems: commons/uncommons exceeding expectations (value_score >= 0.4)
    if rarity in ['common', 'uncommon'] and value_score >= 0.4:
        return "HIDDEN_GEM", f"{rarity.title()} with rare/mythic power (value: +{value_score})"
    
    # Flops: rares/mythics underperforming badly
    if rarity in ['rare', 'mythic'] and value_score < -1.0:
        return "FLOP", f"{rarity.title()} underperforming (value: {value_score})"
    
    # Junk: severely underpowered regardless of rarity
    if power_level < -2.0:
        return "JUNK", "Severely underpowered"
    
    # Staples: reliable picks exceeding expectations
    if value_score >= 0.2:
        return "STAPLE", "Reliable pick for rarity"
    
    # Solid: slightly above average
    if value_score >= 0:
        return "SOLID", "Playable within archetype"
    
    # Fair: meets basic expectations
    if value_score >= -0.3:
        return "FAIR", "Fair value for rarity"
    
    # Default: marginal
    return "MARGINAL", "Situational playability"


def add_value_evaluations(card_list: list[dict]) -> list[dict]:
    """
    Attach value-based evaluations to cards.
    
    Adds the following fields to each card:
        - value_score: How much card exceeds rarity expectations
        - is_bomb: Boolean indicating if card is a bomb
        - bomb_reason: Reason why card qualifies as bomb (if applicable)
        - value_category: Classification (HIDDEN_GEM, BOMB, STAPLE, etc.)
        - value_description: Human-readable description
    
    Args:
        card_list: List of card dictionaries with basic evaluations
        
    Returns:
        Same list with value fields added
    """
    for card in card_list:
        # Calculate value score
        card['value_score'] = calculate_value_score(card)
        
        # Identify bombs
        is_bomb, bomb_reason = identify_bomb(card)
        card['is_bomb'] = is_bomb
        card['bomb_reason'] = bomb_reason
        
        # Classify value category
        category, description = classify_card_value(card)
        card['value_category'] = category
        card['value_description'] = description
    
    return card_list


# ============================================================================
# COMBO DETECTION MODULE
# ============================================================================
"""
Combo Detection System
=====================
Identifies synergies and combos between cards for draft guide archetypes.
"""

import re
from collections import defaultdict

# Synergy patterns - keywords that indicate potential combos
SYNERGY_PATTERNS = {
    'ramp': [
        r'add.*mana',
        r'tap.*mana',
        r'mana.*creature',
        r'enter.*mana',
        r'land.*card',
    ],
    'token': [
        r'create.*token',
        r'token.*creature',
        r'split.*into',
        r'breeding',
    ],
    'buff': [
        r'get bigger',
        r'enchant creature',
        r'equipped',
        r'equip',
        r'\+\d+/\+\d+',
        r'power.*toughness',
    ],
    'graveyard': [
        r'return.*graveyard',
        r'put.*graveyard',
        r'reanimate',
        r'sacrifice',
        r'discard',
    ],
    'draw': [
        r'draw.*card',
        r'search',
        r'reveal',
    ],
    'mill': [
        r'put.*library',
        r'mill',
    ],
    'life_gain': [
        r'gain.*life',
        r'lifelink',
    ],
    'haste': ['haste'],
    'flying': ['flying'],
    'trample': ['trample'],
}

# Archetype definitions - color pairs and their typical strategies
ARCHETYPES = {
    'white_blue': {
        'name': 'Azorius Control',
        'focus': ['control', 'draw', 'buff'],
        'keywords': ['flying', 'vigilance', 'first_strike']
    },
    'blue_black': {
        'name': 'Dimir Discard',
        'focus': ['discard', 'graveyard', 'mill'],
        'keywords': ['shadow', 'discarding']
    },
    'black_red': {
        'name': 'Rakdos Aggro',
        'focus': ['haste', 'life_drain'],
        'keywords': ['haste', 'deathtouch']
    },
    'red_green': {
        'name': 'Gruul Beatdown',
        'focus': ['ramp', 'buff', 'haste'],
        'keywords': ['trample', 'haste']
    },
    'green_white': {
        'name': 'Selesnya Tokens',
        'focus': ['token', 'buff', 'life_gain'],
        'keywords': ['lifelink', 'vigilance']
    },
}


def extract_synergy_tags(card: dict) -> list[str]:
    """
    Extract synergy tags from a card's oracle text.
    
    Args:
        card: Card dictionary with 'oracle_text'
        
    Returns:
        List of synergy tag strings (e.g., ['ramp', 'token'])
    """
    oracle_text = card.get('oracle_text', '').lower()
    tags = []
    
    for tag, patterns in SYNERGY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, oracle_text):
                if tag not in tags:
                    tags.append(tag)
                break
    
    return tags


def find_combos_for_card(card: dict, all_cards: list[dict]) -> list[dict]:
    """
    Find potential combos for a single card with other cards in the set.
    
    Args:
        card: The card to find combos for
        all_cards: List of all cards in the set
        
    Returns:
        List of combo dictionaries, each containing:
            - 'with': Card name(s) it combos with
            - 'text': Description of the combo
            - 'synergy_type': Type of synergy
    """
    card_tags = extract_synergy_tags(card)
    card_name = card.get('name', '')
    combos = []
    
    # Find cards with complementary tags
    for other_card in all_cards:
        if other_card.get('name') == card_name:
            continue
            
        other_tags = extract_synergy_tags(other_card)
        
        # Check for tag overlaps that create combos
        common_tags = set(card_tags) & set(other_tags)
        
        if common_tags:
            # Same-type synergy (e.g., both ramp cards)
            tag = list(common_tags)[0]
            combo_text = f"Both provide {tag} synergy"
            combos.append({
                'with': other_card.get('name'),
                'text': combo_text,
                'synergy_type': tag
            })
    
    # Limit to top 5 most relevant combos
    return combos[:5]


def detect_archetype_combos(cards: list[dict], color_pair: str = None) -> dict:
    """
    Detect all combos within an archetype (color pair or mono).
    
    Args:
        cards: List of cards in the archetype
        color_pair: Optional color pair filter (e.g., 'white_blue')
        
    Returns:
        Dictionary mapping card names to their combos
    """
    # Filter by color pair if specified
    if color_pair:
        from .color_rarity import get_color_group_for_card
        cards = [c for c in cards if color_pair in get_color_group_for_card(c).lower()]
    
    # Find combos for each card
    combo_map = {}
    for card in cards:
        combos = find_combos_for_card(card, cards)
        if combos:
            combo_map[card.get('name')] = combos
    
    return combo_map


def add_combo_evaluations(cards: list[dict]) -> list[dict]:
    """
    Attach combo information to each card.
    
    Args:
        cards: List of card dictionaries
        
    Returns:
        Same list with 'combos' field added to each card
    """
    # Find combos for each card
    for card in cards:
        card['combos'] = find_combos_for_card(card, cards)
    
    return cards
