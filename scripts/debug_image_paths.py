#!/usr/bin/env python3
"""
Debug script to find image path mismatches between HTML and JSON
"""

import json
import re
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    cache_file = base_dir / "html_json" / "card_cache.json"
    gallery_file = base_dir / "html_json" / "card-gallery.html"
    
    # Read card cache JSON
    with open(cache_file, 'r', encoding='utf-8') as f:
        card_cache = json.load(f)
    
    # Build a mapping of card name -> local_image_path
    card_name_to_path = {}
    for card_name, card_data in card_cache.items():
        if 'local_image_path' in card_data:
            card_name_to_path[card_name] = card_data['local_image_path']
    
    # Read the HTML file
    with open(gallery_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find all img tags
    img_pattern = r'<img\s+src="([^"]+)"\s+alt="([^"]+)"'
    
    mismatches = []
    found_in_html = set()
    
    for match in re.finditer(img_pattern, html_content):
        current_src = match.group(1)
        card_name = match.group(2)
        
        # Check if this card exists in JSON
        if card_name in card_name_to_path:
            expected_src = card_name_to_path[card_name]
            
            # Compare paths (normalize them first)
            current_normalized = current_src.strip()
            expected_normalized = expected_src.strip()
            
            if current_normalized != expected_normalized:
                mismatches.append({
                    'card_name': card_name,
                    'current_src': current_src,
                    'expected_src': expected_src
                })
        
        found_in_html.add(card_name)
    
    # Check for cards in JSON but not in HTML
    missing_from_html = set(card_name_to_path.keys()) - found_in_html
    
    print(f"Total cards in JSON: {len(card_name_to_path)}")
    print(f"Total img tags in HTML: {len(found_in_html)}")
    print(f"Mismatches found: {len(mismatches)}")
    print(f"Cards missing from HTML: {len(missing_from_html)}")
    
    if mismatches:
        print("\n=== MISMATCHES ===")
        for m in mismatches[:20]:  # Show first 20
            print(f"\nCard: {m['card_name']}")
            print(f"  Current: {m['current_src']}")
            print(f"  Expected: {m['expected_src']}")
    
    if missing_from_html:
        print("\n=== MISSING FROM HTML ===")
        for card in list(missing_from_html)[:20]:
            print(f"  {card}")

if __name__ == "__main__":
    main()