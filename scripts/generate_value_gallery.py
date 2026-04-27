#!/usr/bin/env python3
"""
Minimal Value Gallery Generator - Creates a simple gallery showing value features.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    generate_card_item_html,
    group_cards_by_color,
    COLOR_GROUP_ORDER,
)


def main():
    # Load evaluated cards
    input_path = Path('html_json/evaluated_sos.json')
    if not input_path.exists():
        print(f"Error: {input_path} not found. Run evaluate_cards.py first.")
        sys.exit(1)
    
    with open(input_path) as f:
        cards = json.load(f)
    
    print(f"Loaded {len(cards)} evaluated cards")
    
    # Group by color
    groups = group_cards_by_color(cards)
    
    # Build HTML manually to avoid template issues
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>MTG Value Gallery</title>',
        '    <style>',
        '        * { margin: 0; padding: 0; box-sizing: border-box; }',
        '        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #1a1a2e; min-height: 100vh; padding: 20px; color: white; }',
        '        .header { text-align: center; padding: 40px 20px; }',
        '        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }',
        '        .color-section { margin-bottom: 40px; padding: 20px; border-radius: 12px; background: rgba(255,255,255,0.05); }',
        '        .color-title { font-size: 1.5rem; margin-bottom: 20px; }',
        '        .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }',
    ]
    
    # Add card item styles
    html_parts.extend([
        '        .card-item { background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: transform 0.2s; position: relative; }',
        '        .card-item:hover { transform: translateY(-4px); box-shadow: 0 6px 16px rgba(0,0,0,0.4); }',
        '        .card-image-container { position: relative; padding-top: 157%; background: #f0f0f0; }',
        '        .card-image { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }',
        '        .card-info { padding: 8px; text-align: center; }',
        '        .card-name { font-size: 0.75rem; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }',
        '        .rarity-badge { position: absolute; top: 5px; right: 5px; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; color: white; }',
        '        .value-badge { position: absolute; top: 5px; left: 5px; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; }',
    ])
    
    # Add tooltip styles
    html_parts.extend([
        '        .card-item[data-tooltip] { position: relative; }',
        '        .card-item[data-tooltip]:hover::after { content: attr(data-tooltip); position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.95); color: #fff; padding: 12px 16px; border-radius: 8px; font-size: 0.7rem; line-height: 1.4; max-width: 320px; z-index: 1000; margin-bottom: 8px; font-family: monospace; white-space: pre-wrap; }',
        '        .card-item[data-tooltip]:hover::before { content: \'\'; position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); border: 8px solid transparent; border-top-color: rgba(0,0,0,0.95); margin-bottom: -16px; z-index: 999; }',
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="header">',
        '        <h1>🎴 MTG Value Gallery</h1>',
        '        <p>Cards sorted by value score - hover for details!</p>',
        '    </div>',
    ])
    
    # Generate color sections
    for color_group in COLOR_GROUP_ORDER:
        if color_group in groups and groups[color_group]:
            color_cards = groups[color_group]
            # Sort by value score (descending)
            sorted_cards = sorted(color_cards, key=lambda c: c.get('value_score', 0), reverse=True)
            
            display_name = color_group.replace('_', ' ').title()
            html_parts.append(f'    <div class="color-section">')
            html_parts.append(f'        <h2 class="color-title">{display_name}</h2>')
            html_parts.append('        <div class="card-grid">')
            
            # Add top 20 cards by value
            for card in sorted_cards[:20]:
                card_html = generate_card_item_html(card, show_rarity_badge=True, show_price=False)
                html_parts.append(card_html.strip())
            
            html_parts.append('        </div>')
            html_parts.append('    </div>')
    
    html_parts.extend(['</body>', '</html>'])
    
    # Write HTML
    output_path = Path('gallery_value.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    
    print(f"Gallery saved to: {output_path}")
    print("\nFeatures demonstrated:")
    print("  ✓ Cards sorted by value score (highest first)")
    print("  ✓ 💣 Bomb badges on powerful cards")
    print("  ✓ 🔍 Hidden gem badges on undervalued cards")
    print("  ✓ Hover tooltips with value formula and combos")


if __name__ == '__main__':
    main()
