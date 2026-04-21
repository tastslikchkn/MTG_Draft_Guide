#!/usr/bin/env python3
"""
Download all card images from the Secrets of Strixhaven set to local cache.
Fetches all cards from Scryfall API and downloads PNG images.

Refactored to use centralized utility modules.
"""

from pathlib import Path
import urllib.request
import json

# Import utilities from centralized modules
from scripts.utils.api import batch_download_images, search_cards


def fetch_secrets_of_strixhaven_cards():
    """Fetch all card names from the Secrets of Strixhaven set using Scryfall API."""
    # Secrets of Strixhaven set code is "sos"
    set_code = "sos"
    
    seen_names = set()
    page = 1
    
    while True:
        url = f"https://api.scryfall.com/cards/search?q=e%3A{set_code}+order%3Aset&page={page}&unique=cards"
        
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            new_cards_count = 0
            for card in data.get('data', []):
                if card['name'] not in seen_names:
                    seen_names.add(card['name'])
                    new_cards_count += 1
            
            print(f"  Page {page}: fetched {new_cards_count} unique cards (total: {len(seen_names)})")
            
            has_more = data.get('has_more', False)
            if not has_more or len(data.get('data', [])) == 0:
                break
            
            page += 1
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  No more pages found at page {page}")
                break
            raise
    
    return list(seen_names)


def main():
    output_dir = Path('images/cards')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Fetching all cards from Secrets of Strixhaven set...")
    card_names = fetch_secrets_of_strixhaven_cards()
    print(f"Found {len(card_names)} unique cards to download.\n")
    
    # Use centralized batch download utility
    result = batch_download_images(
        card_names=card_names,
        output_dir=output_dir,
        rate_limit=1.0,  # Scryfall rate limit
        show_progress=True
    )
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)
    print(f"Total cards: {len(card_names)}")
    print(f"Successful:  {result['success_count']}")
    print(f"Failed:      {len(result['failed_cards'])}")
    print(f"Time elapsed: {result['total_time']:.1f}s")
    
    if result['failed_cards']:
        print(f"\nFailed cards:")
        for card in result['failed_cards'][:10]:
            print(f"  - {card}")
        if len(result['failed_cards']) > 10:
            print(f"  ... and {len(result['failed_cards']) - 10} more")
    
    print(f"\nImages saved to: {output_dir}/")


if __name__ == "__main__":
    main()
