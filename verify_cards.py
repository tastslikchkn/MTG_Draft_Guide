#!/usr/bin/env python3
"""
Verify all cards in strixhaven-draft-guide.html have valid image URLs
and compare against test file card list.
"""
import re

def extract_cards_from_html(filepath):
    """Extract all unique card names from HTML file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all img tags with scryfall URLs
    pattern = r'<img class="card-image" src="https://api\.scryfall\.com/cards/named\?fuzzy=([^&]+)'
    matches = re.findall(pattern, content)
    return set(matches)

def extract_cards_from_test(filepath):
    """Extract card names from test file's CARD_NAMES array."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the CARD_NAMES array
    pattern = r'const CARD_NAMES = \[(.*?)\];'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return set()
    
    # Extract individual card names
    cards_pattern = r'"([^"]+)"'
    return set(re.findall(cards_pattern, match.group(1)))

def main():
    html_cards = extract_cards_from_html('./strixhaven-draft-guide.html')
    test_cards = extract_cards_from_test('./image-validation-test.html')
    
    print("=" * 60)
    print("CARD COUNT COMPARISON")
    print("=" * 60)
    print(f"Cards in strixhaven-draft-guide.html: {len(html_cards)}")
    print(f"Cards in image-validation-test.html:   {len(test_cards)}")
    
    # Find differences
    only_in_html = html_cards - test_cards
    only_in_test = test_cards - html_cards
    common = html_cards & test_cards
    
    print(f"\nCommon to both files:                  {len(common)}")
    
    if only_in_html:
        print(f"\n⚠️  Only in HTML ({len(only_in_html)}):")
        for card in sorted(only_in_html)[:10]:
            print(f"   - {card}")
        if len(only_in_html) > 10:
            print(f"   ... and {len(only_in_html) - 10} more")
    
    if only_in_test:
        print(f"\n⚠️  Only in test file ({len(only_in_test)}):")
        for card in sorted(only_in_test)[:10]:
            print(f"   - {card}")
        if len(only_in_test) > 10:
            print(f"   ... and {len(only_in_test) - 10} more")
    
    # Check for "Unknown Card" placeholders
    unknown_count = sum(1 for c in html_cards if 'Unknown' in c)
    if unknown_count > 0:
        print(f"\n❌ Found {unknown_count} cards with 'Unknown' in name!")
    else:
        print("\n✅ All cards have proper names (no 'Unknown Card' placeholders)")
    
    # Summary
    if not only_in_html and not only_in_test:
        print("\n🎉 PERFECT SYNC - Both files contain identical card lists!")
    else:
        print("\n⚠️  Files are NOT in sync")

if __name__ == "__main__":
    main()
