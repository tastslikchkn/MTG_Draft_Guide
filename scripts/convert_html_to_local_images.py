#!/usr/bin/env python3
"""
Convert strixhaven-draft-guide.html to use local images instead of Scryfall API URLs.
Preserves card names in alt attributes, replaces src with local paths.
"""

import re
from pathlib import Path
import os
from scripts.utils import slugify

def find_image_file(card_name, available_files):
    """Find the correct image file for a card name.
    
    Handles:
    - Exact matches
    - Split cards (short name -> full split card name)
    - Known typos/mismatches in filenames
    
    Note: available_files contains just filenames without extensions.
    """
    slug = slugify(card_name)
    
    # Try exact match first (without .png since available_files has no extension)
    if slug in available_files:
        return f'images/cards/{slug}.png'
    
    # For split cards, look for longer filename starting with short name + hyphen
    matching_files = [f for f in available_files if f.startswith(slug + '-')]
    if matching_files:
        return f'images/cards/{matching_files[0]}.png'
    
    # Known typos/mismatches - map to correct filenames (without .png)
    typo_map = {
        'rabid-attach': 'rabid-attack',
        'tenured-concoctor': 'tenured-concocter',
    }
    if slug in typo_map:
        return f'images/cards/{typo_map[slug]}.png'
    
    # Return the expected path even if file doesn't exist (for debugging)
    return f'images/cards/{slug}.png'

def main():
    input_file = 'strixhaven-draft-guide.html'
    output_file = 'strixhaven-draft-guide-local.html'
    
    # Load available image files for smart lookup (just filenames without extension)
    available_files = set()
    cards_dir = Path('images/cards')
    if cards_dir.exists():
        available_files = {f.stem for f in cards_dir.glob('*.png')}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all img tags with scryfall URLs - capture the full tag and extract alt name
    pattern = r'<img\s[^>]*src="https://api\.scryfall\.com/cards/named\?fuzzy=([^"&]+)[^"]*"[^>]*alt="([^"]+)"'
    
    def replace_with_local(match):
        src_name = match.group(1)     # Card name from src URL
        alt_name = match.group(2)     # Card name from alt attribute
        
        # Find the correct image file (handles split cards and typos)
        local_path = find_image_file(src_name, available_files)
        
        # Replace the src URL with local path
        new_src = f'src="{local_path}"'
        original_tag = match.group(0)
        new_tag = re.sub(
            r'src="https://api\.scryfall\.com/cards/named\?fuzzy=[^"]+"',
            new_src,
            original_tag
        )
        
        print(f"  {alt_name} -> {local_path}")
        return new_tag
    
    # Replace all card image src attributes
    new_content = re.sub(pattern, replace_with_local, content)
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\nCreated: {output_file}")

if __name__ == "__main__":
    main()