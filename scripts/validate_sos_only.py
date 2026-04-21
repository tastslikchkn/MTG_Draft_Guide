#!/usr/bin/env python3
"""
Validate that all cards referenced in HTML files are from SOS set only.
Uses existing utility modules for card extraction and API access.
"""

import json
import requests
from pathlib import Path
from typing import Set, Dict, List

# Add scripts directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from utils.card_data import extract_card_names_from_alt_attributes


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
HTML_FILES = [
    PROJECT_ROOT / "html_json" / "strixhaven-draft-guide.html",
    PROJECT_ROOT / "html_json" / "pauper-decks.html",
    PROJECT_ROOT / "html_json" / "card-gallery.html",
]

SOS_SET_CODE = "sos"
CACHE_FILE = PROJECT_ROOT / "cache" / f"{SOS_SET_CODE}_cards.json"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sos_card_list() -> Set[str]:
    """
    Get all valid SOS card names from Scryfall API.
    Uses cache file to avoid repeated API calls.
    Handles pagination (max 175 cards per page).
    
    Returns:
        Set of valid SOS card names
    """
    # Try to load from cache first
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                print(f"✓ Loaded {len(data)} cards from cache")
                return set(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Cache read error: {e}, fetching fresh...")
    
    # Fetch from Scryfall API using requests with pagination
    print(f"📡 Fetching SOS card list from Scryfall API...")
    url = "https://api.scryfall.com/cards/search"
    params = {'q': f'set:{SOS_SET_CODE}', 'unique': 'cards', 'page': 1}
    headers = {'User-Agent': 'MTG_Draft_Guide/1.0 (by tastslikchkn)'}
    
    all_cards = []
    page = 1
    
    while True:
        params['page'] = page
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch SOS cards from Scryfall: {e}")
        
        if not data or 'data' not in data:
            raise ValueError("Invalid response format from Scryfall")
        
        all_cards.extend(data['data'])
        print(f"  Page {page}: fetched {len(data['data'])} cards (total: {len(all_cards)})")
        
        # Check if there are more pages
        if not data.get('has_more', False):
            break
        
        page += 1
    
    card_names = {card['name'] for card in all_cards}
    print(f"✓ Fetched {len(card_names)} unique SOS cards")
    
    # Save to cache
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(sorted(card_names), f, indent=2)
    print(f"✓ Cached to {CACHE_FILE}")
    
    return card_names


def extract_cards_from_html(html_file: Path) -> Set[str]:
    """
    Extract all unique card names from an HTML file.
    
    Args:
        html_file: Path to HTML file
        
    Returns:
        Set of unique card names
    """
    if not html_file.exists():
        print(f"⚠ File not found: {html_file}")
        return set()
    
    cards = extract_card_names_from_alt_attributes(html_file)
    return set(cards)


# ============================================================================
# MAIN VALIDATION LOGIC
# ============================================================================

def validate_html_files(
    html_files: List[Path],
    valid_cards: Set[str]
) -> Dict[str, Dict]:
    """
    Validate each HTML file against the valid card list.
    
    Args:
        html_files: List of HTML files to check
        valid_cards: Set of valid SOS card names
        
    Returns:
        Dict mapping filename → {all_cards, non_sos_cards, count}
    """
    results = {}
    
    for html_file in html_files:
        print(f"\n📄 Checking: {html_file.name}")
        print("-" * 60)
        
        all_cards = extract_cards_from_html(html_file)
        non_sos_cards = all_cards - valid_cards
        
        results[html_file.name] = {
            'all_cards': all_cards,
            'non_sos_cards': non_sos_cards,
            'total_count': len(all_cards),
            'non_sos_count': len(non_sos_cards)
        }
        
        # Print summary
        print(f"  Total unique cards: {len(all_cards)}")
        print(f"  SOS cards: {len(all_cards) - len(non_sos_cards)}")
        print(f"  Non-SOS cards: {len(non_sos_cards)}")
        
        if non_sos_cards:
            print(f"\n  ❌ NON-SOS CARDS FOUND:")
            for card in sorted(non_sos_cards):
                print(f"     • {card}")
        else:
            print(f"\n  ✅ All cards are from SOS set!")
    
    return results


def main():
    """
    Main entry point for validation script.
    """
    print("=" * 60)
    print("SOS-ONLY CARD VALIDATION")
    print("=" * 60)
    
    # Get valid SOS card list
    sos_cards = get_sos_card_list()
    
    # Validate each HTML file
    results = validate_html_files(HTML_FILES, sos_cards)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_non_sos = sum(r['non_sos_count'] for r in results.values())
    
    if total_non_sos == 0:
        print("✅ ALL HTML FILES PASS — Only SOS cards found!")
    else:
        print(f"❌ FOUND {total_non_sos} NON-SOS CARD(S) ACROSS {len([r for r in results.values() if r['non_sos_count'] > 0])} FILE(S)")
        
        # Aggregate all non-SOS cards
        all_non_sos = set()
        for filename, data in results.items():
            all_non_sos.update(data['non_sos_cards'])
        
        print(f"\nUnique non-SOS cards:")
        for card in sorted(all_non_sos):
            # Find which files contain this card
            files_with_card = [f for f, d in results.items() if card in d['non_sos_cards']]
            print(f"  • {card} → {', '.join(files_with_card)}")
    
    return total_non_sos == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
