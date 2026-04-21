#!/usr/bin/env python3
"""
Fix broken image links in card-gallery.html by using local_image_path from card_cache.json
Refactored to use centralized utility modules.
"""

import re
from pathlib import Path

# Import utilities from centralized modules
from scripts.utils import load_card_cache


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    cache_file = base_dir / "html_json" / "card_cache.json"
    gallery_file = base_dir / "html_json" / "card-gallery.html"
    
    # Read card cache JSON using centralized utility
    card_cache = load_card_cache(cache_file)
    
    # Build a mapping of card name -> local_image_path
    card_name_to_path = {}
    for card_name, card_data in card_cache.items():
        if 'local_image_path' in card_data:
            card_name_to_path[card_name] = card_data['local_image_path']
    
    print(f"Loaded {len(card_name_to_path)} cards with local image paths")
    
    # Read the HTML file
    with open(gallery_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find all img tags and extract card names from alt attributes
    img_pattern = r'<img\s+src="[^"]+"\s+alt="([^"]+)"\s+class="card-image"\s+loading="lazy">'
    
    matches = list(re.finditer(img_pattern, html_content))
    print(f"Found {len(matches)} image tags in HTML")
    
    # Track changes
    fixed_count = 0
    missing_count = 0
    
    for match in matches:
        card_name = match.group(1)
        
        if card_name in card_name_to_path:
            correct_path = card_name_to_path[card_name]
            
            # Extract current src value
            img_tag = match.group(0)
            current_src_match = re.search(r'src="([^"]+)"', img_tag)
            
            if current_src_match:
                current_src = current_src_match.group(1)
                
                # Check if the path is incorrect (not using local_image_path)
                if current_src != correct_path:
                    # Replace with correct path
                    new_img_tag = f'<img src="{correct_path}" alt="{card_name}" class="card-image" loading="lazy">'
                    html_content = html_content.replace(img_tag, new_img_tag)
                    fixed_count += 1
        else:
            missing_count += 1
    
    # Write the updated HTML
    with open(gallery_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nFixed {fixed_count} broken image links")
    if missing_count > 0:
        print(f"Warning: {missing_count} cards not found in card_cache.json")


if __name__ == "__main__":
    main()
