#!/usr/bin/env python3
import urllib.request
import json

def fetch_sos_cards():
    url = "https://api.scryfall.com/cards/search?q=e%3Asos+order%3Aset&unique=cards"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    return data

def main():
    data = fetch_sos_cards()
    
    print(f"Total cards: {data['total_cards']}")
    print(f"Has more pages: {data.get('has_more', False)}")
    
    # Categorize by rarity and color
    categories = {
        'common': {'W': [], 'U': [], 'B': [], 'R': [], 'G': [], 'C': []},
        'uncommon': {'W': [], 'U': [], 'B': [], 'R': [], 'G': [], 'C': []}
    }
    
    for card in data['data']:
        rarity = card.get('rarity')
        if rarity not in ['common', 'uncommon']:
            continue
            
        colors = card.get('colors', [])
        color_key = ''.join(colors) if len(colors) == 1 else 'C'
        if color_key == '':
            color_key = 'C'  # Colorless
            
        categories[rarity][color_key].append({
            'name': card['name'],
            'mana_cost': card.get('mana_cost', ''),
            'type_line': card.get('type_line', ''),
            'oracle_text': card.get('oracle_text', '')[:100] + '...' if len(card.get('oracle_text', '')) > 100 else card.get('oracle_text', '')
        })
    
    # Print summary
    print("\n=== COMMONS BY COLOR ===")
    for color in ['W', 'U', 'B', 'R', 'G', 'C']:
        count = len(categories['common'][color])
        print(f"{color}: {count} cards")
    
    print("\n=== UNCOMMONS BY COLOR ===")
    for color in ['W', 'U', 'B', 'R', 'G', 'C']:
        count = len(categories['uncommon'][color])
        print(f"{color}: {count} cards")
    
    # Print White commons
    print("\n=== WHITE COMMONS ===")
    for card in categories['common']['W'][:15]:
        print(f"  - {card['name']} ({card['mana_cost']})")
    
if __name__ == "__main__":
    main()
