#!/usr/bin/env python3
"""
Regenerate card-gallery.html using image paths from card_cache.json.

Refactored to use centralized utility modules.
"""

from pathlib import Path

# Import utilities from centralized modules
from scripts.utils import (
    load_card_cache,
    get_rarity_letter,
    get_rarity_color,
)
from scripts.utils.html_templates import (
    generate_card_item_html,
    save_gallery_html,
)


def main():
    # Load card cache using utility
    cards = load_card_cache(Path('html_json/card_cache.json'))
    
    # Group cards by rarity
    rarities = {'mythic': [], 'rare': [], 'uncommon': [], 'common': []}
    
    for card_name, card_data in cards.items():
        rarity = card_data.get('rarity', 'common').lower()
        if rarity in rarities:
            rarities[rarity].append(card_data)
    
    # Sort each rarity group by name
    for rarity in rarities:
        rarities[rarity].sort(key=lambda x: x['name'])
    
    # Build HTML manually (simplified version using card_item_html utility)
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strixhaven Card Gallery</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; padding: 20px;
        }
        .header { text-align: center; padding: 40px 20px; color: white; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { color: #a0a0a0; font-size: 1.1rem; }
        .legend { display: flex; justify-content: center; gap: 20px; padding: 20px; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 8px; color: white; font-size: 0.9rem; }
        .legend-rarity { width: 20px; height: 20px; border-radius: 50%; display: inline-block; }
        .color-section { margin-bottom: 40px; padding: 20px; border-radius: 12px; }
        .color-title { font-size: 1.5rem; color: white; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid rgba(255,255,255,0.2); }
        .rarity-group { margin-bottom: 25px; }
        .rarity-title { font-size: 1rem; color: #a0a0a0; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
        .rarity-dot { width: 12px; height: 12px; border-radius: 50%; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
        .card-item { background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: transform 0.2s, box-shadow 0.2s; }
        .card-item:hover { transform: translateY(-4px); box-shadow: 0 6px 16px rgba(0,0,0,0.4); }
        .card-image-container { position: relative; padding-top: 157%; background: #f0f0f0; }
        .card-image { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
        .card-info { padding: 8px; text-align: center; }
        .card-name { font-size: 0.75rem; color: #333; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .card-mana-cost { font-size: 0.8rem; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Strixhaven Card Gallery</h1>
        <p>All cards grouped by rarity (M → R → U → C)</p>
    </div>
    
    <div class="legend">
        <div class="legend-item"><span class="legend-rarity" style="background: #FFD700;"></span> Mythic Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #C41E3A;"></span> Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #228B22;"></span> Uncommon</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #696969;"></span> Common</div>
    </div>

    <div class="color-section">
        <h2 class="color-title">All Cards</h2>
'''
    
    # Add rarity groups in order: M, R, U, C
    rarity_order = ['mythic', 'rare', 'uncommon', 'common']
    
    for rarity_key in rarity_order:
        cards_in_rarity = rarities[rarity_key]
        if not cards_in_rarity:
            continue
            
        rarity_letter = get_rarity_letter(rarity_key)
        rarity_color = get_rarity_color(rarity_key)
        
        html += f'''
        <div class="rarity-group">
            <h3 class="rarity-title">
                <span class="rarity-dot" style="background: {rarity_color};"></span>
                {rarity_letter} ({len(cards_in_rarity)})
            </h3>
            <div class="card-grid">
'''
        
        for card in cards_in_rarity:
            name = card.get('name', 'Unknown')
            mana_cost = card.get('mana_cost', '')
            local_image_path = card.get('local_image_path', f'../images/cards/{name.lower().replace(" ", "-")}.png')
            
            html += generate_card_item_html(
                name=name,
                image_path=local_image_path,
                mana_cost=mana_cost
            )
        
        html += '''
            </div>
        </div>
'''
    
    html += '''
    </div>

</body>
</html>
'''
    
    # Save using utility
    save_gallery_html(html, Path('html_json/card-gallery.html'))
    
    total_cards = sum(len(c) for c in rarities.values())
    print(f"Generated card-gallery.html with {total_cards} cards")


if __name__ == '__main__':
    main()
