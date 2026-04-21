#!/usr/bin/env python3
"""
Check for missing image files referenced in card_cache.json.

Refactored to use centralized utility modules.
"""

from pathlib import Path

# Import utilities from centralized modules
from scripts.utils import load_card_cache


def main():
    base_dir = Path(__file__).parent.parent
    
    # Read card cache using centralized utility
    card_cache = load_card_cache(base_dir / "html_json" / "card_cache.json")
    
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
