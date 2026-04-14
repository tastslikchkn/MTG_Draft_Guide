#!/usr/bin/env python3
"""
Card Image Downloader for Strixhaven Draft Guide
Downloads all unique card images from Scryfall and caches them locally.
Handles rate limiting (1 req/sec) and creates fallback-friendly structure.
"""

import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from html.parser import HTMLParser


class CardNameExtractor(HTMLParser):
    """Extract all unique card names from the HTML file."""
    
    def __init__(self):
        super().__init__()
        self.card_names = set()
        self.current_name = []
        self.in_card_name = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and any('card-name' in str(attr) for attr in attrs):
            self.in_card_name = True
            self.current_name = []
            
    def handle_endtag(self, tag):
        if tag == 'div' and self.in_card_name:
            card_name = ''.join(self.current_name).strip()
            # Remove color badges and tags from name
            card_name = re.sub(r'<[^>]+>', '', card_name)
            card_name = re.sub(r'\s+', ' ', card_name).strip()
            # Remove CT, MF, MV, CS suffixes for cleaner filenames
            card_name = re.sub(r'\s*\(CT\)\s*$', '', card_name)
            card_name = re.sub(r'\s*\(MF\)\s*$', '', card_name)
            card_name = re.sub(r'\s*\(MV\)\s*$', '', card_name)
            card_name = re.sub(r'\s*\(CS\)\s*$', '', card_name)
            if card_name and len(card_name) > 1:
                self.card_names.add(card_name)
            self.in_card_name = False
            
    def handle_data(self, data):
        if self.in_card_name:
            self.current_name.append(data)


def sanitize_filename(name):
    """Convert card name to safe filename."""
    # Replace spaces with underscores
    filename = name.replace(' ', '_')
    # Remove/replace special characters
    filename = re.sub(r'[^a-zA-Z0-9_]', '', filename)
    return filename


def download_card_image(card_name, output_dir):
    """
    Download a single card image from Scryfall.
    Returns True on success, False on failure.
    """
    # Scryfall API URL for card images
    url = f"https://api.scryfall.com/cards/named?fuzzy={urllib.parse.quote(card_name)}&format=normal"
    
    filename = sanitize_filename(card_name) + ".png"
    filepath = output_dir / filename
    
    try:
        print(f"  Downloading: {card_name}...")
        urllib.request.urlretrieve(url, filepath)
        
        # Verify file was downloaded and is valid
        if filepath.stat().st_size > 0:
            print(f"    ✓ Saved: {filename} ({filepath.stat().st_size / 1024:.1f} KB)")
            return True
        else:
            print(f"    ✗ Empty file for {card_name}")
            return False
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"    ✗ Not found: {card_name} (404)")
        else:
            print(f"    ✗ HTTP Error {e.code}: {card_name}")
        return False
    except Exception as e:
        print(f"    ✗ Error downloading {card_name}: {e}")
        return False


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
    
    # Extract unique card names from HTML
    print(f"\n📖 Parsing {html_file} for card names...")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    parser = CardNameExtractor()
    parser.feed(html_content)
    card_names = sorted(parser.card_names)
    
    print(f"   Found {len(card_names)} unique cards")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"   Output directory: {output_dir}")
    
    # Download each card with rate limiting
    print(f"\n⬇️  Starting downloads (1 req/sec for rate limiting)...")
    print("-" * 50)
    
    success_count = 0
    failed_cards = []
    
    for i, card_name in enumerate(card_names, 1):
        print(f"[{i}/{len(card_names)}] {card_name}")
        
        if download_card_image(card_name, output_dir):
            success_count += 1
        else:
            failed_cards.append(card_name)
        
        # Rate limiting - wait 1 second between requests
        time.sleep(1.0)
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"📊 DOWNLOAD COMPLETE")
    print(f"   Total cards:     {len(card_names)}")
    print(f"   Successfully:    {success_count}")
    print(f"   Failed:          {len(failed_cards)}")
    
    if failed_cards:
        print(f"\n❌ Failed cards:")
        for card in failed_cards:
            print(f"   - {card}")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in output_dir.glob("*.png"))
    print(f"\n💾 Total cache size: {total_size / 1024 / 1024:.2f} MB")
    
    # Update HTML to use local images
    print(f"\n🔄 Updating HTML to reference local images...")
    update_html_to_use_local(html_file, card_names)
    print(f"   ✓ HTML updated!")


def update_html_to_use_local(html_file, card_names):
    """
    Update the HTML file to use local cached images as primary source.
    Modifies the JavaScript fallback chain to check local files first.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find and replace the image error handler to include local path
    old_onerror = 'img.onerror = function() {'
    new_onerror = '''img.onerror = function() {
                // Try local cached image first!
                const cardName = this.alt || '';
                const localPath = './images/cards/' + cardName.replace(/\s+/g, '_') + '.png';
                console.log(`Trying local cache: ${localPath}`);
                this.src = localPath;
                return; // Don't continue to other fallbacks
            };
            // Original Scryfall error handler below:
            const originalErrorHandler = '''
    
    # This is a simplified approach - just add local path to fallback chain
    # Find the fallbacks array and add local path as first option
    old_fallbacks = "const fallbacks = [" 
    new_fallbacks = '''// Try local cached image FIRST!
                const cardName = this.alt || '';
                const localPath = './images/cards/' + cardName.replace(/\s+/g, '_') + '.png';
                console.log(`Trying local cache: ${localPath}`);
                this.src = localPath;
                return; // Stop here - don't try other fallbacks
            };
            // If we get here, original Scryfall load failed:
            const originalErrorHandler = '''
    
    # Actually, let's do a simpler replacement - modify the onerror completely
    # Find the entire image setup script and replace it
    old_script_start = "document.querySelectorAll('.card-image').forEach(img => {"
    new_script_start = '''// Enhanced image loading with LOCAL cache priority!
document.querySelectorAll('.card-image').forEach(img => {
            // Extract card name from alt attribute or adjacent text
            const cardName = img.alt || '';
            
            // Convert to local path format
            const localPath = './images/cards/' + cardName.replace(/\s+/g, '_') + '.png';
            
            // Check if local file exists by attempting to load it
            const testImg = new Image();
            testImg.onload = function() {
                console.log(`Using local cache: ${localPath}`);
                img.src = localPath;
                img.style.opacity = '1';
            };
            testImg.onerror = function() {
                // Local doesn't exist, use original Scryfall URL
                console.log(`Local not found, using Scryfall: ${cardName}`);
                // Keep original Scryfall URL
                img.style.opacity = '0';
            };
            testImg.src = localPath;
            
            // Fallback if Scryfall also fails
            img.onerror = function() {'''
    
    # This is getting complex - let's just patch the fallback chain instead
    # Simple approach: add local path as first fallback option
    html_content = html_content.replace(
        "const fallbacks = [",
        "const fallbacks = [" +
        "                    './images/cards/' + cardName.replace(/\\s+/g, '_') + '.png', // LOCAL CACHE FIRST!"
    )
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    import urllib.parse  # Import here to avoid issues
    main()
