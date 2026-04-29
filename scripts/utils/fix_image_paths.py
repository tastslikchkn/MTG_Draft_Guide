#!/usr/bin/env python3
"""
Fix card image paths in HTML files to use local cached images.
The cache has mixed naming: some files use underscores (Harsh_Annotation.jpg)
others use hyphens (harsh-annotation.jpg). This script handles both.
"""

import re
from pathlib import Path


def build_image_lookup(images_dir: Path) -> dict:
    """
    Build a lookup table mapping card name variations to actual filenames.
    Handles both underscore and hyphen naming conventions.
    """
    available_images = {}
    
    for img_file in images_dir.glob('*.jpg'):
        filename = img_file.name
        stem = img_file.stem  # Without extension, preserves case and separators
        
        # Create multiple lookup keys for the same file
        # Key format: lowercase with underscores (standardized)
        key1 = stem.lower().replace('-', '_')
        available_images[key1] = filename
        
        # Also keep original lowercase as key
        key2 = stem.lower()
        if key2 not in available_images:
            available_images[key2] = filename
    
    for img_file in images_dir.glob('*.jpeg'):
        filename = img_file.name
        stem = img_file.stem
        key1 = stem.lower().replace('-', '_')
        available_images[key1] = filename
        key2 = stem.lower()
        if key2 not in available_images:
            available_images[key2] = filename
    
    return available_images


def find_matching_image(card_name: str, available_images: dict) -> str | None:
    """
    Find the matching local image for a card name.
    Tries multiple naming conventions and split-card handling.
    """
    # Standardize: lowercase, spaces to underscores
    standardized = card_name.lower().replace(' ', '_')
    
    if standardized in available_images:
        return available_images[standardized]
    
    # Try with hyphens instead of underscores
    hyphenated = card_name.lower().replace(' ', '-')
    if hyphenated in available_images:
        return available_images[hyphenated]
    
    # For split cards (A // B), try just the first part
    if ' //' in card_name:
        first_part = card_name.split(' // ')[0].strip()
        standardized_first = first_part.lower().replace(' ', '_')
        if standardized_first in available_images:
            return available_images[standardized_first]
        
        hyphenated_first = first_part.lower().replace(' ', '-')
        if hyphenated_first in available_images:
            return available_images[hyphenated_first]
    else:
        # Card name might be first part of a split card
        # Look for files that START with this name followed by more text
        for key, filename in available_images.items():
            # Check if key starts with our standardized name + separator
            if (key.startswith(standardized + '_') or 
                key.startswith(hyphenated + '-') or
                key == standardized or key == hyphenated):
                return filename
    
    return None


def fix_html_file(html_path: Path, images_dir: Path):
    """
    Fix all card image paths in an HTML file to use local cache.
    """
    available_images = build_image_lookup(images_dir)
    print(f"Built lookup table with {len(available_images)} entries from {images_dir}")
    
    # Read HTML file
    html_content = html_path.read_text(encoding='utf-8')
    
    # Pattern to match img tags - handles various attribute orders
    img_pattern = re.compile(
        r'<img\s+([^>]*?)src="([^"]+)"([^>]*?)alt="([^"]*)"([^>]*)>',
        re.IGNORECASE | re.DOTALL
    )
    
    fixed_count = 0
    not_found = []
    checked_cards = set()
    
    def replace_img(match):
        nonlocal fixed_count
        before_src = match.group(1)
        old_src = match.group(2)
        between = match.group(3)
        alt = match.group(4)
        after_alt = match.group(5)
        
        if not alt.strip():
            return match.group(0)  # No change if no alt text
        
        card_name = alt.strip()
        
        # Skip if already processed this exact src+alt combo
        cache_key = (old_src, card_name)
        if cache_key in checked_cards:
            return match.group(0)
        checked_cards.add(cache_key)
        
        # Find local image
        local_image = find_matching_image(card_name, available_images)
        
        if local_image:
            # Calculate relative path from HTML file to images directory
            # HTML is in pages/, images are in ../images/cards/
            new_src = f"../images/cards/{local_image}"
            
            # Build Scryfall fallback URL
            scryfall_url = f"https://api.scryfall.com/cards/named?fuzzy={card_name.replace(' ', '%20')}&format=image"
            
            # Check if we need to add onerror handler
            has_onerror = 'onerror=' in between.lower() or 'onerror=' in after_alt.lower()
            
            if not has_onerror:
                # Add onerror fallback after src
                new_tag = f'<img {before_src}src="{new_src}" onerror="this.src=\'{scryfall_url}\'; this.style.opacity=1;" style="opacity:0.9;"{between}alt="{alt}"{after_alt}>'
            else:
                # Just update src, keep existing onerror
                new_tag = f'<img {before_src}src="{new_src}"{between}alt="{alt}"{after_alt}>'
            
            fixed_count += 1
            return new_tag
        else:
            not_found.append(card_name)
            return match.group(0)  # No change
    
    # Apply replacements
    html_content = img_pattern.sub(replace_img, html_content)
    
    # Write back
    html_path.write_text(html_content, encoding='utf-8')
    
    print(f"Fixed {fixed_count} image paths in {html_path.name}")
    
    if not_found:
        unique_not_found = list(set(not_found))
        print(f"Could not find local images for {len(unique_not_found)} unique cards:")
        for name in sorted(unique_not_found)[:15]:
            print(f"  - {name}")
        if len(unique_not_found) > 15:
            print(f"  ... and {len(unique_not_found) - 15} more")
    
    return fixed_count, list(set(not_found))


def main():
    base_dir = Path(__file__).parent.parent
    images_dir = base_dir / "images" / "cards"
    
    html_files = [
        base_dir / "pages" / "strixhaven-draft-guide.html",
        base_dir / "pages" / "card-gallery.html", 
        base_dir / "pages" / "sos_pauper_decks.html",
    ]
    
    total_fixed = 0
    all_not_found = set()
    
    for html_file in html_files:
        if html_file.exists():
            print(f"\n{'='*60}")
            print(f"Processing: {html_file.name}")
            print('='*60)
            fixed, not_found = fix_html_file(html_file, images_dir)
            total_fixed += fixed
            all_not_found.update(not_found)
        else:
            print(f"\nSkipping (not found): {html_file.name}")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: Fixed {total_fixed} image paths across all files")
    if all_not_found:
        print(f"Missing local images for {len(all_not_found)} unique cards")


if __name__ == '__main__':
    main()
