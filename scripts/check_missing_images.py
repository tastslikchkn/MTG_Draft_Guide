#!/usr/bin/env python3
"""
Check for missing image files referenced in card_cache.json
"""

import json
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    
    # Read card cache with UTF-8 encoding
    with open(base_dir / "html_json" / "card_cache.json", 'r', encoding='utf-8') as f:
        card_cache = json.load(f)
    
    cards_dir = base_dir / "images" / "cards"
    
    missing_count = 0
    fixed_by_single_hyphen = 0
    
    for name, data in card_cache.items():
        if 'local_image_path' in data:
            path = data['local_image_path']
            file_path = cards_dir / Path(path).name
            
            if not file_path.exists():
                missing_count += 1
                
                # Try single hyphen version for split cards
                alt_name = Path(path).name.replace('--', '-')
                alt_path = cards_dir / alt_name
                
                if alt_path.exists():
                    fixed_by_single_hyphen += 1
                    print(f"FIXABLE: {path} -> {alt_name}")
                else:
                    print(f"MISSING: {path}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total missing files: {missing_count}")
    print(f"Fixable by replacing -- with -: {fixed_by_single_hyphen}")

if __name__ == "__main__":
    main()