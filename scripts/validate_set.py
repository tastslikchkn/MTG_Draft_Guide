#!/usr/bin/env python3
"""
Validate that all cards referenced in HTML files are from a specific set.
Uses existing utility modules for card extraction and API access.

Usage:
    python validate_set.py --set-code sos
    python validate_set.py -s mkm --html-files index.html draft-guide.html
"""

import argparse
import json
import requests
import sys
from pathlib import Path
from typing import Set, Dict, List

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.card_data import extract_card_names_from_alt_attributes


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_HTML_FILES = [
    PROJECT_ROOT / "html_json" / "draft-guide.html",
    PROJECT_ROOT / "html_json" / "pauper-decks.html",
    PROJECT_ROOT / "html_json" / "card-gallery.html",
]


def get_set_card_list(set_code: str, cache_dir: Path | None = None) -> Set[str]:
    """
    Get all valid card names for a set from Scryfall API.
    Uses cache file to avoid repeated API calls.
    Handles pagination (max 175 cards per page).
    
    Args:
        set_code: The MTG set code (e.g., 'sos', 'mkm')
        cache_dir: Optional directory for cache files
        
    Returns:
        Set of valid card names for the specified set
    """
    # Setup cache path
    if cache_dir is None:
        cache_dir = PROJECT_ROOT / "cache"
    cache_file = cache_dir / f"{set_code}_cards.json"
    
    # Try to load from cache first
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                print(f"✓ Loaded {len(data)} cards from cache")
                return set(data) if isinstance(data, list) else data
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Cache read error: {e}, fetching fresh...")
    
    # Fetch from Scryfall API using requests with pagination
    print(f"📡 Fetching {set_code.upper()} card list from Scryfall API...")
    url = "https://api.scryfall.com/cards/search"
    params = {'q': f'set:{set_code}', 'unique': 'cards', 'page': 1}
    headers = {'User-Agent': 'MTG_Draft_Guide/1.0'}
    
    all_cards = []
    page = 1
    
    while True:
        params['page'] = page
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch {set_code.upper()} cards from Scryfall: {e}")
        
        if not data or 'data' not in data:
            raise ValueError("Invalid response format from Scryfall")
        
        all_cards.extend(data['data'])
        print(f"  Page {page}: fetched {len(data['data'])} cards (total: {len(all_cards)})")
        
        # Check if there are more pages
        if not data.get('has_more', False):
            break
        
        page += 1
    
    card_names = {card['name'] for card in all_cards}
    print(f"✓ Fetched {len(card_names)} unique {set_code.upper()} cards")
    
    # Save to cache
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(sorted(card_names), f, indent=2)
    print(f"✓ Cached to {cache_file}")
    
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


def validate_html_files(
    html_files: List[Path],
    valid_cards: Set[str],
    set_code: str
) -> Dict[str, Dict]:
    """
    Validate each HTML file against the valid card list.
    
    Args:
        html_files: List of HTML files to check
        valid_cards: Set of valid card names for the specified set
        set_code: The set code being validated against
        
    Returns:
        Dict mapping filename → {all_cards, non_set_cards, count}
    """
    results = {}
    
    for html_file in html_files:
        print(f"\n📄 Checking: {html_file.name}")
        print("-" * 60)
        
        all_cards = extract_cards_from_html(html_file)
        non_set_cards = all_cards - valid_cards
        
        results[html_file.name] = {
            'all_cards': all_cards,
            'non_set_cards': non_set_cards,
            'total_count': len(all_cards),
            'non_set_count': len(non_set_cards)
        }
        
        # Print summary
        print(f"  Total unique cards: {len(all_cards)}")
        print(f"  {set_code.upper()} cards: {len(all_cards) - len(non_set_cards)}")
        print(f"  Non-{set_code.upper()} cards: {len(non_set_cards)}")
        
        if non_set_cards:
            print(f"\n  ❌ NON-{set_code.upper()} CARDS FOUND:")
            for card in sorted(non_set_cards):
                print(f"     • {card}")
        else:
            print(f"\n  ✅ All cards are from {set_code.upper()} set!")
    
    return results


def main():
    """
    Main entry point for validation script.
    """
    parser = argparse.ArgumentParser(
        description='Validate that HTML files only contain cards from a specific MTG set.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --set-code sos                    # Validate SOS cards
  %(prog)s -s mkm                            # Validate Murders at Castle Whispers
  %(prog)s -s sos --html-files index.html    # Check specific file(s)
        """
    )
    
    parser.add_argument(
        '--set-code', '-s',
        type=str,
        required=True,
        help='MTG set code to validate against (e.g., sos, mkm, neo)'
    )
    
    parser.add_argument(
        '--html-files',
        type=Path,
        nargs='+',
        default=None,
        help='HTML files to check (default: standard draft guide files)'
    )
    
    parser.add_argument(
        '--cache-dir',
        type=Path,
        default=None,
        help='Directory for cache files (default: project cache/ directory)'
    )
    
    args = parser.parse_args()
    
    # Use default HTML files if none specified
    html_files = args.html_files or DEFAULT_HTML_FILES
    
    print("=" * 60)
    print(f"SET-ONLY CARD VALIDATION: {args.set_code.upper()}")
    print("=" * 60)
    
    # Get valid card list for the specified set
    set_cards = get_set_card_list(args.set_code, args.cache_dir)
    
    # Validate each HTML file
    results = validate_html_files(html_files, set_cards, args.set_code)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_non_set = sum(r['non_set_count'] for r in results.values())
    
    if total_non_set == 0:
        print(f"✅ ALL HTML FILES PASS — Only {args.set_code.upper()} cards found!")
    else:
        files_with_issues = len([r for r in results.values() if r['non_set_count'] > 0])
        print(f"❌ FOUND {total_non_set} NON-{args.set_code.upper()} CARD(S) ACROSS {files_with_issues} FILE(S)")
        
        # Aggregate all non-set cards
        all_non_set = set()
        for filename, data in results.items():
            all_non_set.update(data['non_set_cards'])
        
        print(f"\nUnique non-{args.set_code.upper()} cards:")
        for card in sorted(all_non_set):
            # Find which files contain this card
            files_with_card = [f for f, d in results.items() if card in d['non_set_cards']]
            print(f"  • {card} → {', '.join(files_with_card)}")
    
    return total_non_set == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
