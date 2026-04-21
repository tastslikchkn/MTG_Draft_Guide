#!/usr/bin/env python3
"""
Generate a card gallery webpage grouped by color and rarity (M, R, U, C).
Fetches actual card colors from Scryfall API for accurate categorization.

Refactored to use centralized utility modules.
"""

from pathlib import Path
from collections import defaultdict

# Import utilities from centralized modules
from scripts.utils import (
    extract_card_names_from_html,
    get_color_group_for_card,
    title_case_from_slug,
)
from scripts.utils.api import fetch_card_by_name


def main():
    print("Scanning local card images...")
    
    cards_dir = Path('images/cards')
    if not cards_dir.exists():
        print(f"Error: {cards_dir} does not exist")
        return
    
    # Get all PNG files
    png_files = sorted(cards_dir.glob('*.png'))
    print(f"Found {len(png_files)} card images")
    
    # Extract proper card names from HTML alt attributes using utility
    html_card_names = extract_card_names_from_html(Path('strixhaven-draft-guide.html'))
    print(f"Found {len(html_card_names)} unique card names in HTML")
    
    # Build mapping: slugified filename -> proper card name
    name_mapping = {}
    for stem in [f.stem for f in png_files]:
        title_name = stem.replace('-', ' ').title()
        for html_name in html_card_names:
            html_slug = html_name.lower().replace(' ', '-').replace("'", '')
            if html_slug == stem or stem.startswith(html_slug + '-'):
                name_mapping[stem] = html_name
                break
    
    card_data_list = []
    
    for i, png_file in enumerate(png_files, 1):
        stem = png_file.stem
        display_name = name_mapping.get(stem, title_case_from_slug(stem))
        
        print(f"[{i}/{len(png_files)}] Fetching: {display_name}")
        
        # Fetch card data from Scryfall API using utility
        card_data = fetch_card_by_name(display_name)
        if not card_data:
            continue
        
        colors = card_data.get('colors', [])
        color_group = get_color_group_for_card(card_data)
        rarity = card_data.get('rarity', 'c')
        mana_cost = card_data.get('mana_cost', '')
        
        card_data_list.append({
            'display_name': display_name,
            'image_path': f'images/cards/{png_file.name}',
            'rarity': rarity,
            'rarity_display': rarity.upper(),
            'mana_cost': mana_cost,
            'colors': colors,
            'color_group': color_group,
        })
    
    print(f"\nTotal cards: {len(card_data_list)}")
    
    # Group by color
    cards_by_group = defaultdict(list)
    for card in card_data_list:
        cards_by_group[card['color_group']].append(card)
    
    # Sort each group alphabetically by name
    for color_group in cards_by_group:
        cards_by_group[color_group].sort(key=lambda c: c['display_name'])
    
    print(f"\nCards by color:")
    for color, card_list in cards_by_group.items():
        print(f"  {color}: {len(card_list)}")
    
    # Generate HTML
    html_content = generate_html(cards_by_group)
    
    with open('card-gallery.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nCreated: card-gallery.html")


def generate_html(cards_by_group):
    """Generate HTML content for the gallery."""
    color_names = {
        'colorless': 'Colorless',
        'mono_white': 'White',
        'mono_blue': 'Blue',
        'mono_black': 'Black', 
        'mono_red': 'Red',
        'mono_green': 'Green',
        'multicolor': 'Multicolor',
    }
    
    color_classes = {
        'colorless': 'bg-gray-200 border-gray-400',
        'mono_white': 'bg-white border-blue-200',
        'mono_blue': 'bg-blue-50 border-blue-300',
        'mono_black': 'bg-gray-100 border-purple-300',
        'mono_red': 'bg-red-50 border-orange-300',
        'mono_green': 'bg-green-50 border-green-300',
        'multicolor': 'bg-yellow-50 border-pink-300',
    }
    
    rarity_colors = {
        'M': '#FFD700',  # Gold for mythic
        'R': '#C41E3A',  # Red for rare
        'U': '#228B22',  # Green for uncommon  
        'C': '#696969',  # Gray for common
        'S': '#FF69B4',  # Pink for special
        'L': '#8FBC8F',  # Dark sea green for land
    }
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strixhaven Card Gallery</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 40px 20px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            color: #a0a0a0;
            font-size: 1.1rem;
        }
        
        .legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            font-size: 0.9rem;
        }
        
        .legend-rarity {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .color-section {
            margin-bottom: 40px;
            padding: 20px;
            border-radius: 12px;
        }
        
        .color-title {
            font-size: 1.5rem;
            color: white;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }
        
        .rarity-group {
            margin-bottom: 25px;
        }
        
        .rarity-title {
            font-size: 1rem;
            color: #a0a0a0;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .rarity-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 12px;
        }
        
        .card-item {
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card-item:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }
        
        .card-image-container {
            position: relative;
            padding-top: 157%; /* Card aspect ratio ~1.57 */
            background: #f0f0f0;
        }
        
        .card-image {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .card-info {
            padding: 8px;
            text-align: center;
        }
        
        .card-name {
            font-size: 0.75rem;
            color: #333;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .card-mana-cost {
            font-size: 0.8rem;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .card-grid {
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 8px;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Strixhaven Card Gallery</h1>
        <p>All cards grouped by color and rarity (M → R → U → C)</p>
    </div>
    
    <div class="legend">
        <div class="legend-item"><span class="legend-rarity" style="background: #FFD700;"></span> Mythic Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #C41E3A;"></span> Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #228B22;"></span> Uncommon</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #696969;"></span> Common</div>
    </div>

'''
    
    for color_key in ['mono_white', 'mono_blue', 'mono_black', 'mono_red', 'mono_green', 'multicolor', 'colorless']:
        if color_key not in cards_by_group:
            continue
            
        cards = cards_by_group[color_key]
        color_name = color_names.get(color_key, color_key)
        color_class = color_classes.get(color_key, '')
        
        html += f'''
    <div class="color-section {color_class}">
        <h2 class="color-title">{color_name}</h2>
'''
        
        # Group by rarity
        rarity_groups = defaultdict(list)
        for card in cards:
            rarity_groups[card['rarity_display']].append(card)
        
        for rarity_char in ['M', 'R', 'U', 'C', 'S', 'L']:
            if rarity_char not in rarity_groups:
                continue
                
            rarity_cards = rarity_groups[rarity_char]
            rarity_color = rarity_colors.get(rarity_char, '#999')
            
            html += f'''
        <div class="rarity-group">
            <h3 class="rarity-title">
                <span class="rarity-dot" style="background: {rarity_color};"></span>
                {rarity_char} ({len(rarity_cards)})
            </h3>
            <div class="card-grid">
'''
            
            for card in rarity_cards:
                html += f'''
                <div class="card-item">
                    <div class="card-image-container">
                        <img src="{card['image_path']}" alt="{card['display_name']}" class="card-image" loading="lazy">
                    </div>
                    <div class="card-info">
                        <div class="card-name">{card['display_name']}</div>
                        <div class="card-mana-cost">{card['mana_cost'] or ''}</div>
                    </div>
                </div>
'''
            
            html += '''
            </div>
        </div>
'''
        
        html += '    </div>\n'
    
    html += '''
</body>
</html>
'''
    
    return html


if __name__ == '__main__':
    main()
