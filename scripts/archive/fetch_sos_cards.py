#!/usr/bin/env python3
"""
Fetch all cards from Secrets of Strixhaven set using Scryfall API.
Categorizes by rarity and color for analysis.

Refactored to use centralized utility modules.
"""

from collections import defaultdict

# Import utilities from centralized modules
from scripts.utils.api import search_cards
from scripts.utils.color_rarity import get_color_group_for_card


def main():
    # Fetch all SOS cards using centralized search utility
    result = search_cards("e:sos order:set", unique="cards")
    
    print(f"Total cards: {result['total_cards']}")
    print(f"Has more pages: {result.get('has_more', False)}\n")
    
    # Categorize by rarity and color
    categories = defaultdict(lambda: {'mono_white': [], 'mono_blue': [], 'mono_black': [], 
                                       'mono_red': [], 'mono_green': [], 'multicolor': [], 'colorless': []})
    
    for card in result['data']:
        rarity = card.get('rarity')
        if rarity not in ['common', 'uncommon']:
            continue
            
        color_group = get_color_group_for_card(card)
        
        categories[rarity][color_group].append({
            'name': card['name'],
            'mana_cost': card.get('mana_cost', ''),
            'type_line': card.get('type_line', ''),
            'oracle_text': (card.get('oracle_text', '')[:100] + '...' 
                           if len(card.get('oracle_text', '')) > 100 
                           else card.get('oracle_text', ''))
        })
    
    # Print summary
    print("\n=== COMMONS BY COLOR ===")
    for color_group in ['mono_white', 'mono_blue', 'mono_black', 'mono_red', 'mono_green', 'multicolor', 'colorless']:
        count = len(categories['common'][color_group])
        print(f"{color_group}: {count} cards")
    
    print("\n=== UNCOMMONS BY COLOR ===")
    for color_group in ['mono_white', 'mono_blue', 'mono_black', 'mono_red', 'mono_green', 'multicolor', 'colorless']:
        count = len(categories['uncommon'][color_group])
        print(f"{color_group}: {count} cards")
    
    # Print White commons
    print("\n=== WHITE COMMONS ===")
    for card in categories['common']['mono_white'][:15]:
        print(f"  - {card['name']} ({card['mana_cost']})")


if __name__ == "__main__":
    main()
