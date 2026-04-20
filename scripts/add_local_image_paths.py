#!/usr/bin/env python3
"""Add local image paths to card_cache.json entries."""

import json
import re

def card_name_to_filename(card_name):
    """Convert card name to filename format (lowercase, spaces to hyphens)."""
    # Convert to lowercase and replace spaces with hyphens
    filename = card_name.lower().replace(' ', '-')
    # Remove any special characters except hyphens
    filename = re.sub(r'[^a-z0-9\-]', '', filename)
    return f"../images/cards/{filename}.png"

def main():
    input_file = 'html_json/card_cache.json'
    output_file = 'html_json/card_cache.json'
    
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    # Add local_image_path to each card entry
    updated_count = 0
    for card_name in cards:
        if 'local_image_path' not in cards[card_name]:
            cards[card_name]['local_image_path'] = card_name_to_filename(card_name)
            updated_count += 1
    
    # Write back to the file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)
    
    print(f"Added local_image_path to {updated_count} card entries.")

if __name__ == '__main__':
    main()