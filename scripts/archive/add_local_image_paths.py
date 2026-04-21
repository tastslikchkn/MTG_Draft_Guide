#!/usr/bin/env python3
"""
Add local image paths to card_cache.json entries.

Refactored to use centralized utility modules.
"""

from pathlib import Path

# Import utilities from centralized modules
from scripts.utils import load_card_cache, save_card_cache, slugify


def main():
    cache_file = Path('html_json/card_cache.json')
    
    # Load card cache using centralized utility
    cards = load_card_cache(cache_file)
    
    # Add local_image_path to each card entry using centralized slugify
    updated_count = 0
    for card_name in cards:
        if 'local_image_path' not in cards[card_name]:
            filename = slugify(card_name) + '.png'
            cards[card_name]['local_image_path'] = f"../images/cards/{filename}"
            updated_count += 1
    
    # Save using centralized utility
    save_card_cache(cards, cache_file)
    
    print(f"Added local_image_path to {updated_count} card entries.")


if __name__ == '__main__':
    main()
