#!/usr/bin/env python3
"""
Card Image Downloader for Strixhaven Draft Guide
Downloads all unique card images from Scryfall and caches them locally.
Handles rate limiting (1 req/sec) and creates fallback-friendly structure.

Refactored to use centralized utility modules.
"""

from pathlib import Path

# Import utilities from centralized modules
from scripts.utils import (
    extract_card_names_from_html,
)
from scripts.utils.api import batch_download_images


def main():
    # Configuration
    html_file = Path("./strixhaven-draft-guide.html")
    output_dir = Path("./images/cards")
    
    print(f"📚 Strixhaven Draft Guide - Image Downloader")
    print(f"=" * 50)
    
    # Check if HTML file exists
    if not html_file.exists():
        print(f"❌ Error: {html_file} not found!")
        return
    
    # Extract unique card names from HTML using utility
    print(f"\n📖 Parsing {html_file} for card names...")
    card_names = extract_card_names_from_html(html_file)
    
    if not card_names:
        print(f"❌ Error: No card names found in {html_file}")
        return
    
    print(f"   Found {len(card_names)} unique cards")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"   Output directory: {output_dir}")
    
    # Download all images using centralized batch utility
    result = batch_download_images(
        card_names=card_names,
        output_dir=output_dir,
        rate_limit=1.0,  # Scryfall rate limit
        show_progress=True
    )
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"📊 DOWNLOAD COMPLETE")
    print(f"   Total cards:     {len(card_names)}")
    print(f"   Successfully:    {result['success_count']}")
    print(f"   Failed:          {len(result['failed_cards'])}")
    print(f"   Time elapsed:    {result['total_time']:.1f}s")
    
    if result['failed_cards']:
        print(f"\n❌ Failed cards:")
        for card in result['failed_cards'][:10]:  # Show first 10
            print(f"   - {card}")
        if len(result['failed_cards']) > 10:
            print(f"   ... and {len(result['failed_cards']) - 10} more")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in output_dir.glob("*.png"))
    print(f"\n💾 Total cache size: {total_size / 1024 / 1024:.2f} MB")
    
    # Update HTML to use local images
    print(f"\n🔄 Updating HTML to reference local images...")
    update_html_to_use_local(html_file)
    print(f"   ✓ HTML updated!")


def update_html_to_use_local(html_file: Path) -> None:
    """
    Update the HTML file to use local cached images as primary source.
    Modifies the JavaScript fallback chain to check local files first.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Simple approach: add local path as first fallback option
    html_content = html_content.replace(
        "const fallbacks = [",
        "const fallbacks = [" +
        "                    './images/cards/' + cardName.replace(/\\s+/g, '_') + '.png', // LOCAL CACHE FIRST!"
    )
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    main()
