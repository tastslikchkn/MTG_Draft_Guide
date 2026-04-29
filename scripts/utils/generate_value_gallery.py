#!/usr/bin/env python3
"""
Value Gallery Generator - Creates a gallery showing cards sorted by value score.
Uses the updated algorithm with card advantage framework (Reid Duke, WotC 2014).
"""

import json
from pathlib import Path
import sys
import re

# Import from sibling modules within utils package
from .html_templates import generate_card_item_html
from .color_rarity import group_cards_by_color, COLOR_GROUP_ORDER, COLOR_GROUP_DISPLAY
from .api import calculate_value_score, identify_bomb, classify_card_value


def extract_image_mapping(html_path: Path) -> dict:
    """
    Extract card name -> image path mapping from card-gallery.html.
    This ensures we use the same paths that work in the card gallery.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]+)"'
    mapping = {}
    for src, alt in re.findall(pattern, content):
        mapping[alt] = src
    return mapping


def ensure_evaluations(cards: list) -> list:
    """
    Ensure all cards have value evaluations. Recalculate if missing.
    """
    updated_count = 0
    for card in cards:
        needs_update = False
        
        # Check if card has required evaluation fields
        if 'value_score' not in card:
            needs_update = True
        if 'is_bomb' not in card:
            needs_update = True
        if 'value_category' not in card:
            needs_update = True
        
        if needs_update:
            # Recalculate evaluations
            calculate_value_score(card)
            identify_bomb(card)
            classify_card_value(card)
            updated_count += 1
    
    if updated_count > 0:
        print(f"Recalculated evaluations for {updated_count} cards")
    
    return cards


def main():
    # Load evaluated cards
    input_path = Path('data/evaluated_sos.json')
    if not input_path.exists():
        print(f"Error: {input_path} not found. Run evaluate_cards.py first.")
        sys.exit(1)
    
    with open(input_path) as f:
        cards = json.load(f)
    
    print(f"Loaded {len(cards)} evaluated cards")
    
    # Ensure all cards have evaluations
    cards = ensure_evaluations(cards)
    
    # Extract image path mapping from card-gallery.html
    gallery_path = Path('pages/card-gallery.html')
    if gallery_path.exists():
        image_mapping = extract_image_mapping(gallery_path)
        print(f"Extracted {len(image_mapping)} image paths from card-gallery.html")
        
        # Add image_path to each card based on mapping
        for card in cards:
            name = card.get('name', '')
            if name in image_mapping:
                card['image_path'] = image_mapping[name]
    else:
        print(f"Warning: {gallery_path} not found. Using auto-generated paths.")
    
    # Group by color (now includes separate multicolor groupings)
    groups = group_cards_by_color(cards)
    
    # Build HTML manually to avoid template issues
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>MTG Value Gallery - Updated Algorithm</title>',
        '    <style>',
        '        * { margin: 0; padding: 0; box-sizing: border-box; }',
        '        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #1a1a2e; min-height: 100vh; padding: 20px; color: white; }',
        '        .header { text-align: center; padding: 40px 20px; }',
        '        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }',
        '        .header p { color: #aaa; margin-bottom: 20px; }',
        '        .algorithm-note { background: rgba(102, 127, 204, 0.2); padding: 15px; border-radius: 8px; max-width: 600px; margin: 0 auto 20px; font-size: 0.9rem; }',
        '        .color-section { margin-bottom: 40px; padding: 20px; border-radius: 12px; background: rgba(255,255,255,0.05); }',
        '        .color-title { font-size: 1.5rem; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }',
        '        .card-count { font-size: 0.9rem; color: #888; font-weight: normal; }',
        '        .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }',
    ]
    
    # Add card item styles
    html_parts.extend([
        '        .card-item { background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: transform 0.2s; position: relative; }',
        '        .card-item:hover { transform: translateY(-4px); box-shadow: 0 6px 16px rgba(0,0,0,0.4); }',
        '        .card-image-container { position: relative; padding-top: 157%; background: #f0f0f0; }',
        '        .card-image { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }',
        '        .card-info { padding: 8px; text-align: center; }',
        '        .card-name { font-size: 0.75rem; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 4px; }',
        '        .rarity-badge { position: absolute; top: 5px; right: 5px; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; color: white; }',
        '        .value-badge { position: absolute; top: 5px; left: 5px; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; }',
        # Value formula styles
        '        .card-value-formula { background: rgba(0,0,0,0.03); border-radius: 4px; padding: 4px; margin-top: 4px; }',
        '        .value-row { display: flex; justify-content: space-between; font-size: 0.65rem; align-items: center; }',
        '        .value-label { color: #666; }',
        '        .value-number { font-weight: bold; color: #333; }',
        '        .score-row { border-top: 1px solid rgba(0,0,0,0.1); padding-top: 2px; margin-top: 2px; }',
        '        .score-row .value-label { color: #444; font-weight: bold; }',
        '        .ca-bonus { font-size: 0.6rem; color: #667eea; font-style: italic; text-align: center; margin-top: 2px; }',
    ])
    
    html_parts.extend([
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="header">',
        '        <h1>🎴 MTG Value Gallery</h1>',
        '        <p>Cards sorted by value score - highest first!</p>',
        '        <div class="algorithm-note">',
        '            📊 <strong>Updated Algorithm:</strong> Uses Reid Duke\'s card advantage framework (WotC 2014). ',
        '            Spell values based on damage (0.75×), draw (1.5× per card), and removal (~2.5). ',
        '            Card advantage provides +10% bonus per point.',
        '        </div>',
        '    </div>',
    ])
    
    # Generate color sections
    total_cards_shown = 0
    for color_group in COLOR_GROUP_ORDER:
        if color_group in groups and groups[color_group]:
            color_cards = groups[color_group]
            # Sort by value score (descending)
            sorted_cards = sorted(color_cards, key=lambda c: c.get('value_score', 0), reverse=True)
            
            display_name = COLOR_GROUP_DISPLAY.get(color_group, color_group.replace('_', ' ').title())
            html_parts.append(f'    <div class="color-section">')
            html_parts.append(f'        <h2 class="color-title">{display_name} <span class="card-count">({len(sorted_cards)} cards)</span></h2>')
            html_parts.append('        <div class="card-grid">')
            
            # Show ALL cards in this color group
            for card in sorted_cards:
                card_html = generate_card_item_html(card, show_rarity_badge=True, show_price=False)
                html_parts.append(card_html.strip())
                total_cards_shown += 1
            
            html_parts.append('        </div>')
            html_parts.append('    </div>')
    
    html_parts.extend([
        '    <script>',
        '})();',
        '</script>',
        '</body>',
        '</html>'
    ])
    
    # Write HTML
    output_path = Path('pages/gallery_value.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    
    print(f"\nGallery saved to: {output_path}")
    print(f"Total cards shown: {total_cards_shown}")
    print("\nFeatures demonstrated:")
    print("  ✓ Cards sorted by value score (highest first)")
    print("  💣 Bomb badges on powerful cards")
    print("  🔍 Hidden gem badges on undervalued cards")
    print("  📊 Updated algorithm with card advantage framework")
    print("  🎨 Separate multicolor groupings (W/U, B/R, etc.)")


if __name__ == '__main__':
    main()
