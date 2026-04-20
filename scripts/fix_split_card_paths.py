#!/usr/bin/env python3
"""
Fix split card paths by replacing -- with - in both card_cache.json and card-gallery.html
Split cards use // in names but files use single hyphen, not double hyphen.
"""

import json
import re
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    
    # Fix card_cache.json first
    cache_file = base_dir / "html_json" / "card_cache.json"
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        card_cache = json.load(f)
    
    fixed_count = 0
    for name, data in card_cache.items():
        if 'local_image_path' in data:
            old_path = data['local_image_path']
            new_path = old_path.replace('--', '-')
            
            if old_path != new_path:
                data['local_image_path'] = new_path
                fixed_count += 1
                print(f"Fixed JSON: {old_path} -> {new_path}")
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(card_cache, f, indent=2, ensure_ascii=False)
    
    print(f"\nFixed {fixed_count} paths in card_cache.json")
    
    # Now fix card-gallery.html
    gallery_file = base_dir / "html_json" / "card-gallery.html"
    
    with open(gallery_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace -- with - in all img src attributes
    old_html = html_content
    html_content = re.sub(r'src="([^"]+)--([^"]+)"', r'src="\1-\2"', html_content)
    
    if old_html != html_content:
        changes = html_content.count('-') - old_html.count('--')
        print(f"Fixed paths in card-gallery.html")
        
        with open(gallery_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    # Verify the fix
    missing_count = 0
    for name, data in card_cache.items():
        if 'local_image_path' in data:
            path = data['local_image_path']
            file_path = (base_dir / "images" / "cards") / Path(path).name
            if not file_path.exists():
                missing_count += 1
                print(f"STILL MISSING: {path}")
    
    print(f"\nVerification: {missing_count} files still missing")

if __name__ == "__main__":
    main()