#!/usr/bin/env python3
import re
from pathlib import Path

html_dir = Path('html_json')
images_dir = Path('images/cards')

actual_images = {f.name.lower(): f.suffix for f in images_dir.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png']}
print(f'Total actual images: {len(actual_images)}')

for html_file in sorted(html_dir.glob('*.html')):
    content = html_file.read_text()
    png_refs = re.findall(r'src="([^"]+\.png)"', content)
    mismatched = []
    for ref in png_refs:
        basename = Path(ref).name
        if basename.lower() not in actual_images:
            jpg_version = basename.rsplit('.', 1)[0] + '.jpg'
            if jpg_version.lower() in actual_images:
                mismatched.append((ref, jpg_version))
    if mismatched:
        print(f'{html_file.name}: {len(mismatched)} .png→.jpg mismatches')
