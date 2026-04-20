#!/usr/bin/env python3
"""
Download all card images from the Secrets of Strixhaven set to local cache.
Fetches all cards from Scryfall API and downloads PNG images.
"""

import re
import os
import urllib.request
import urllib.parse
import time
import json
from pathlib import Path
from scripts.utils import slugify

def fetch_secrets_of_strixhaven_cards():
    """Fetch all card names from the Secrets of Strixhaven set using Scryfall API."""
    # Secrets of Strixhaven set code is "sos"
    set_code = "sos"
    
    seen_names = set()
    page = 1
    
    while True:
        # Use Scryfall search endpoint with set filter (e:sos means "set equals sos")
        url = f"https://api.scryfall.com/cards/search?q=e%3A{set_code}+order%3Aset&page={page}&unique=cards"
        
        try:
            # Scryfall API requires Accept header for JSON responses
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            # Add cards from this page (avoiding duplicates for reprints in the same set)
            new_cards_count = 0
            for card in data.get('data', []):
                if card['name'] not in seen_names:
                    seen_names.add(card['name'])
                    new_cards_count += 1
            
            print(f"  Page {page}: fetched {new_cards_count} unique cards (total: {len(seen_names)})")
            
            # Check if there are more pages
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


def download_card_image(card_name, output_dir):
    """Download a single card image from multiple MTG APIs."""
    import json
    
    # Try multiple search strategies across different APIs
    strategies = [
        # Strategy 1: Scryfall - Exact name match (any set)
        ('scryfall_search', lambda name: f"https://api.scryfall.com/cards/search?q=name%3D%22{urllib.parse.quote(name)}%22&unique=cards&page=1&per_page=1"),
        # Strategy 2: Scryfall - Named endpoint (exact match)
        ('scryfall_named', lambda name: f"https://api.scryfall.com/cards/named?exact={urllib.parse.quote(name)}"),
        # Strategy 3: Magic The Gathering API v1 - Search by name
        ('mtg_api_v1', lambda name: f"https://api.magicthegathering.io/v1/cards?q.name={urllib.parse.quote(name)}"),
    ]
    
    for strategy_name, strategy in strategies:
        try:
            api_url = strategy(card_name)
            
            # Scryfall API requires Accept header for JSON responses
            req = urllib.request.Request(api_url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            card_data = None
            
            # Parse Scryfall search endpoint (returns {"data": [...], "total_cards": N})
            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                card_data = data['data'][0]
            # Parse Scryfall named endpoint (returns single card object or error)
            elif isinstance(data, dict) and 'name' in data and data.get('name') == card_name:
                card_data = data
            # Parse Magic The Gathering API v1 response (returns array of cards)
            elif isinstance(data, list) and len(data) > 0:
                card_data = data[0]
            else:
                continue
            
            if not card_data:
                continue
            
            # Extract image URL based on API source
            image_url = None
            
            # Try Scryfall format first (image_uris.normal, image_uris.png, art_crop_uri)
            image_uris = card_data.get('image_uris', {})
            image_url = (image_uris.get('normal') or 
                       image_uris.get('png') or 
                       card_data.get('art_crop_uri'))
            
            # Try Magic The Gathering API v1 format (imageUrl field)
            if not image_url:
                image_url = card_data.get('imageUrl')
            
            if not image_url:
                continue
                
            filename = slugify(card_name) + '.png'
            filepath = os.path.join(output_dir, filename)
            
            print(f"Downloading: {card_name} -> {filename} (via {strategy_name})")
            
            urllib.request.urlretrieve(image_url, filepath)
            
            if os.path.getsize(filepath) > 0:
                return True, f"Saved to {filepath}"
                
        except Exception as e:
            continue
    
    return False, "Card not found in any database"

def main():
    # Configuration
    output_dir = 'images/cards'
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Fetching all cards from Secrets of Strixhaven set...")
    cards = fetch_secrets_of_strixhaven_cards()
    print(f"Found {len(cards)} unique cards to download.\n")
    
    # Download each card with rate limiting (Scryfall recommends 1 req/sec)
    success_count = 0
    fail_count = 0
    
    for i, card_name in enumerate(cards, 1):
        print(f"[{i}/{len(cards)}] Processing: {card_name}")
        
        success, message = download_card_image(card_name, output_dir)
        
        if success:
            success_count += 1
            print(f"   [OK] {message}\n")
        else:
            fail_count += 1
            print(f"   [FAIL] {message}\n")
        
        # Rate limiting - wait 1 second between requests
        time.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)
    print(f"Total cards: {len(cards)}")
    print(f"Successful:  {success_count}")
    print(f"Failed:      {fail_count}")
    print(f"\nImages saved to: {output_dir}/")

if __name__ == "__main__":
    main()