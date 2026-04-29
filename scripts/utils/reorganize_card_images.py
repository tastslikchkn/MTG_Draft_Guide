#!/usr/bin/env python3
"""
Reorganize card images into set-based subdirectories and update HTML references.

Moves all SOS card images to images/cards/SOS/ with consistent naming (lowercase hyphens)
and updates all HTML files to reference the new locations.
"""

import re
import shutil
from pathlib import Path
from collections import defaultdict


def slugify(name: str) -> str:
    """Convert card name to lowercase hyphenated slug."""
    # Lowercase everything
    slug = name.lower()
    # Remove commas (split cards have them)
    slug = slug.replace(',', '')
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    # Replace underscores with hyphens (for consistency)
    slug = slug.replace('_', '-')
    # Handle apostrophes (e.g., "Killian's Confidence" → "killians-confidence")
    slug = slug.replace("'", '')
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def main():
    base_dir = Path.home() / "repos/MTG_Draft_Guide"
    card_dir = base_dir / "images" / "cards"
    sos_dir = card_dir / "SOS"
    html_dirs = [base_dir / "pages", base_dir / "html_json"]
    
    # Create SOS directory
    sos_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Card Image Reorganization")
    print("=" * 60)
    print(f"Source: {card_dir}")
    print(f"Target: {sos_dir}")
    print()
    
    # Step 1: Move all images to SOS subdirectory with consistent naming
    moved_count = 0
    name_mapping = {}  # old_name → new_slug
    
    for img_file in card_dir.glob("*.jpg"):
        stem = img_file.stem  # Filename without extension
        new_slug = slugify(stem)
        target_path = sos_dir / f"{new_slug}.jpg"
        
        name_mapping[stem.lower()] = new_slug
        
        if img_file != target_path:
            shutil.copy2(img_file, target_path)
            moved_count += 1
    
    print(f"✓ Moved {moved_count} images to SOS/")
    
    # Step 2: Update HTML references
    updated_refs = 0
    files_updated = set()
    
    for html_dir in html_dirs:
        if not html_dir.exists():
            continue
            
        for html_file in html_dir.glob("*.html"):
            content = html_file.read_text()
            modified = False
            
            # Find all image references and update them
            def replace_image_ref(match):
                nonlocal updated_refs, modified
                old_path = match.group(1)
                
                # Extract card name from path
                if 'images/cards/' in old_path:
                    card_name = Path(old_path).stem
                    new_slug = slugify(card_name)
                    new_ref = f"../images/cards/SOS/{new_slug}.jpg"
                    updated_refs += 1
                    modified = True
                    return f'src="{new_ref}"'
                return match.group(0)
            
            # Match src="...jpg" patterns
            new_content = re.sub(
                r'src="([^"]*\.jpg)"',
                replace_image_ref,
                content,
                flags=re.IGNORECASE
            )
            
            if modified:
                html_file.write_text(new_content)
                files_updated.add(html_file.name)
    
    print(f"✓ Updated {updated_refs} image references in {len(files_updated)} HTML files")
    
    # Step 3: Verify
    sos_images = list(sos_dir.glob("*.jpg"))
    print(f"\n✓ SOS/ now contains {len(sos_images)} images")
    
    # Show sample of new naming
    print("\nSample renamed files:")
    for img in sorted(sos_dir.glob("*.jpg"))[:10]:
        print(f"  - {img.name}")
    
    print("\n✓ Reorganization complete!")


if __name__ == "__main__":
    main()
