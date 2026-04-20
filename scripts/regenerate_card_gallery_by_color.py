#!/usr/bin/env python3
"""
Regenerate card-gallery.html with cards grouped by color first, then rarity.
Order: Mono-color (W, U, B, R, G) → Multi-color → Colorless → Lands
Within each group: Rarity M → R → U → C
"""

import json
from pathlib import Path
from collections import defaultdict
from scripts.utils import (
    get_color_group,
    get_rarity_order,
    get_color_group_order,
    get_avg_price_7d,
    format_price,
    hex_to_rgb,
    COLOR_SECTIONS,
    RARITY_INFO
)

def generate_html(card_cache):
    """Generate the HTML content for the card gallery."""
    
    # Group cards by color group and rarity
    groups = defaultdict(lambda: {'M': [], 'R': [], 'U': [], 'C': []})
    
    for name, data in card_cache.items():
        colors = data.get('colors', [])
        rarity = data.get('rarity', '').lower()
        
        # Determine color group
        if not colors:
            # Check if it's a land
            type_line = data.get('type_line', '')
            if 'Land' in type_line:
                color_group = 'lands'
            else:
                color_group = 'colorless'
        elif len(set(colors)) == 1:
            color = colors[0]
            color_names = {'W': 'white', 'U': 'blue', 'B': 'black', 'R': 'red', 'G': 'green'}
            color_group = f"mono_{color_names[color]}"
        else:
            color_group = 'multicolor'
        
        # Determine rarity letter
        if 'mythic' in rarity:
            rarity_letter = 'M'
        elif 'rare' in rarity:
            rarity_letter = 'R'
        elif 'uncommon' in rarity:
            rarity_letter = 'U'
        else:
            rarity_letter = 'C'
        
        groups[color_group][rarity_letter].append(data)
    
    # Sort each rarity group by CMC then name
    for color_group in groups:
        for rarity_letter in groups[color_group]:
            groups[color_group][rarity_letter].sort(key=lambda x: (x.get('cmc', 0), x.get('name', '')))
    
    # HTML template parts
    html_parts = []
    html_parts.append('''<!DOCTYPE html>
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
            grid-template-columns: repeat(auto-fill, minmax(345px, 1fr));
            gap: 30px;
        }
        
        .card-item {
            background: #fff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card-item:hover {
            transform: translateY(-9px);
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
            padding: 20px;
            text-align: center;
        }
        
        .card-name {
            font-size: 1.85rem;
            color: #333;
            margin-bottom: 9px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .card-mana-cost {
            font-size: 1.95rem;
            color: #666;
        }
        
        .card-price {
            font-size: 1.85rem;
            color: #2ECC40;
            font-weight: 500;
            margin-top: 6px;
        }
        
        @media (max-width: 768px) {
            .card-grid {
                grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
                gap: 20px;
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
        <p>Cards grouped by color, then rarity (M → R → U → C)</p>
    </div>
    
    <div class="legend">
        <div class="legend-item"><span class="legend-rarity" style="background: #FFD700;"></span> Mythic Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #C41E3A;"></span> Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #228B22;"></span> Uncommon</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #696969;"></span> Common</div>
    </div>

''')
    
    # Color section definitions with styles
    color_sections = [
        ('mono_white', 'White Cards', '#ffffff'),
        ('mono_blue', 'Blue Cards', '#0074D9'),
        ('mono_black', 'Black Cards', '#111111'),
        ('mono_red', 'Red Cards', '#FF4136'),
        ('mono_green', 'Green Cards', '#2ECC40'),
        ('multicolor', 'Multi-Color Cards', '#B10DC9'),
        ('colorless', 'Colorless Cards', '#AAAAAA'),
        ('lands', 'Lands', '#FF851B'),
    ]
    
    rarity_info = {
        'M': ('Mythic Rare (M)', '#FFD700'),
        'R': ('Rare (R)', '#C41E3A'),
        'U': ('Uncommon (U)', '#228B22'),
        'C': ('Common (C)', '#696969')
    }
    
    # Generate sections in order
    for color_group, title, bg_color in color_sections:
        has_cards = any(len(groups[color_group][r]) > 0 for r in ['M', 'R', 'U', 'C'])
        
        if not has_cards:
            continue
        
        html_parts.append(f'''
    <div class="color-section" style="background: rgba({hex_to_rgb(bg_color)}, 0.1);">
        <h2 class="color-title">{title}</h2>
''')
        
        for rarity_letter in ['M', 'R', 'U', 'C']:
            cards = groups[color_group][rarity_letter]
            if not cards:
                continue
            
            rarity_name, rarity_color = rarity_info[rarity_letter]
            
            html_parts.append(f'''
        <div class="rarity-group">
            <h3 class="rarity-title">
                <span class="rarity-dot" style="background: {rarity_color};"></span>
                {rarity_name} ({len(cards)})
            </h3>
            <div class="card-grid">
''')
            
            for card in cards:
                name = card.get('name', '')
                local_image_path = card.get('local_image_path', f'../images/cards/{name.lower().replace(" ", "-").replace("/", "-").replace("'", "")}.png')
                
                html_parts.append(f'''
                <div class="card-item">
                    <div class="card-image-container">
<img src="{local_image_path}" alt="{name}" class="card-image" loading="lazy">
                    </div>
                </div>
''')
            
            html_parts.append('''
            </div>
        </div>
''')
        
        html_parts.append('''
    </div>
''')
    
    html_parts.append('''
</body>
</html>
''')
    
    return ''.join(html_parts)


def main():
    base_dir = Path(__file__).parent.parent
    
    # Read card cache
    with open(base_dir / "html_json" / "card_cache.json", 'r', encoding='utf-8') as f:
        card_cache = json.load(f)
    
    print(f"Loaded {len(card_cache)} cards")
    
    # Generate HTML
    html_content = generate_html(card_cache)
    
    # Write HTML file
    output_file = base_dir / "html_json" / "card-gallery.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated card gallery at {output_file}")

if __name__ == "__main__":
    main()