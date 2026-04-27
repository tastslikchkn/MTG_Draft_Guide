"""
Card data models and parsing utilities for MTG Draft Guide scripts.
Provides consistent card name handling, slugification, and data extraction.
"""

import re
from html.parser import HTMLParser
from typing import Any
from pathlib import Path


# ============================================================================
# CARD NAME UTILITIES  
# ============================================================================

def sanitize_filename(name: str) -> str:
    """
    Convert card name to safe filename.
    
    Args:
        name: The card name to sanitize
        
    Returns:
        Safe filename with spaces as underscores, special chars removed
        
    Example:
        >>> sanitize_filename("Elite Interceptor // Rejoinder")
        'Elite_Interceptor___Rejoinder'
    """
    # Replace spaces with underscores  
    filename = name.replace(' ', '_')
    # Remove/replace special characters (keep alphanumeric and underscore)
    filename = re.sub(r'[^a-zA-Z0-9_]', '', filename)
    return filename


def slugify(name: str) -> str:
    """
    Convert card name to URL-safe slug.
    
    Args:
        name: The card name to convert
        
    Returns:
        Lowercase slug with hyphens instead of spaces
        
    Example:
        >>> slugify("Elite Interceptor // Rejoinder")
        'elite-interceptor--rejoinder'
    """
    # Replace spaces with hyphens
    slug = name.replace(' ', '-')
    # Remove special characters except hyphens and underscores
    slug = re.sub(r'[^a-zA-Z0-9\-_]', '', slug)
    # Convert to lowercase
    slug = slug.lower()
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug


def title_case_from_slug(slug: str) -> str:
    """
    Convert a slug back to title case.
    
    Args:
        slug: The URL-safe slug
        
    Returns:
        Title-cased string with hyphens replaced by spaces
    """
    return slug.replace('-', ' ').title()


def clean_card_name(name: str) -> str:
    """
    Clean card name by removing suffixes and extra whitespace.
    
    Args:
        name: Raw card name possibly containing (CT), (MF), etc.
        
    Returns:
        Cleaned card name
        
    Example:
        >>> clean_card_name("Spellstutter Sprite (CT)")
        'Spellstutter Sprite'
    """
    # Remove CT, MF, MV, CS suffixes
    name = re.sub(r'\s*\(CT\)\s*$', '', name)
    name = re.sub(r'\s*\(MF\)\s*$', '', name)
    name = re.sub(r'\s*\(MV\)\s*$', '', name)
    name = re.sub(r'\s*\(CS\)\s*$', '', name)
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name


# ============================================================================
# HTML PARSERS FOR CARD EXTRACTION
# ============================================================================

class CardNameExtractor(HTMLParser):
    """
    Extract all unique card names from an HTML file.
    Parses div elements with 'card-name' class.
    """
    
    def __init__(self):
        super().__init__()
        self.card_names: set[str] = set()
        self.current_name: list[str] = []
        self.in_card_name: bool = False
        
    def handle_starttag(self, tag: str, attrs: list[tuple]):
        if tag == 'div' and any('card-name' in str(attr) for attr in attrs):
            self.in_card_name = True
            self.current_name = []
            
    def handle_endtag(self, tag: str):
        if tag == 'div' and self.in_card_name:
            card_name = ''.join(self.current_name).strip()
            # Remove HTML tags from name
            card_name = re.sub(r'<[^>]+>', '', card_name)
            card_name = clean_card_name(card_name)
            if card_name and len(card_name) > 1:
                self.card_names.add(card_name)
            self.in_card_name = False
            
    def handle_data(self, data: str):
        if self.in_card_name:
            self.current_name.append(data)


def extract_card_names_from_html(html_file: Path) -> list[str]:
    """
    Extract unique card names from an HTML draft guide file.
    
    Args:
        html_file: Path to the HTML file
        
    Returns:
        Sorted list of unique card names
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    parser = CardNameExtractor()
    parser.feed(html_content)
    return sorted(parser.card_names)


def extract_card_names_from_alt_attributes(html_file: Path) -> list[str]:
    """
    Extract card names from img alt attributes in HTML.
    
    Args:
        html_file: Path to the HTML file
        
    Returns:
        Sorted list of unique card names from alt attributes
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find all img tags and their alt attributes
    pattern = r'<img[^>]+alt="([^"]+)"'
    matches = re.findall(pattern, html_content)
    
    return sorted(set(matches))


# ============================================================================
# CARD DATA MODELS
# ============================================================================

class CardData:
    """
    Simple data class for holding card information.
    """
    
    def __init__(
        self,
        name: str,
        image_path: str | None = None,
        mana_cost: str = '',
        type_line: str = '',
        oracle_text: str = '',
        colors: list[str] | None = None,
        color_identity: list[str] | None = None,
        rarity: str = 'common',
        prices: dict[str, Any] | None = None
    ):
        self.name = name
        self.image_path = image_path
        self.mana_cost = mana_cost
        self.type_line = type_line
        self.oracle_text = oracle_text
        self.colors = colors or []
        self.color_identity = color_identity or []
        self.rarity = rarity
        self.prices = prices or {}
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'image_path': self.image_path,
            'mana_cost': self.mana_cost,
            'type_line': self.type_line,
            'oracle_text': self.oracle_text,
            'colors': self.colors,
            'color_identity': self.color_identity,
            'rarity': self.rarity,
            'prices': self.prices
        }
    
    @classmethod
    def from_scryfall_response(cls, response: dict[str, Any]) -> 'CardData':
        """
        Create CardData instance from Scryfall API response.
        
        Args:
            response: JSON dict from Scryfall API
            
        Returns:
            CardData instance with parsed fields
        """
        if not response:
            raise ValueError("Empty response")
        
        return cls(
            name=response.get('name', ''),
            mana_cost=response.get('mana_cost', ''),
            type_line=response.get('type_line', ''),
            oracle_text=response.get('oracle_text', ''),
            colors=response.get('colors', []),
            color_identity=response.get('color_identity', []),
            rarity=response.get('rarity', 'common')
        )


# ============================================================================
# FILE OPERATIONS FOR CARD DATA
# ============================================================================

def load_card_cache(cache_file: Path) -> dict[str, Any]:
    """
    Load card cache from JSON file.
    
    Args:
        cache_file: Path to the cache file
        
    Returns:
        Dictionary of card data keyed by name
        
    Raises:
        FileNotFoundError: If cache file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    import json
    
    if not cache_file.exists():
        raise FileNotFoundError(f"Cache file not found: {cache_file}")
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_card_cache(
    card_cache: dict[str, Any],
    cache_file: Path,
    indent: int = 2
) -> None:
    """
    Save card cache to JSON file.
    
    Args:
        card_cache: Dictionary of card data
        cache_file: Output path
        indent: JSON indentation level
    """
    import json
    
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(card_cache, f, indent=indent, ensure_ascii=False)


def get_cached_image_paths(cards_dir: Path, base_path: str = 'images/cards/') -> dict[str, str]:
    """
    Get mapping of card names to local image paths.
    
    Args:
        cards_dir: Directory containing card images
        base_path: The prefix for the relative path (e.g., 'images/cards/')
        
    Returns:
        Dict mapping slugified names to relative image paths
    """
    if not cards_dir.exists():
        return {}
    
    png_files = sorted(cards_dir.glob('*.png'))
    
    return {
        f.stem: f'{base_path}/{f.name}'
        for f in png_files
    }


def find_image_file(
    card_name: str,
    available_files: set | None = None,
    cards_dir: Path | None = None,
    base_path: str = 'images/cards/'
) -> str:
    """
    Find the correct image file path for a card name.
    
    Handles:
    - Exact matches
    - Split cards (short name -> full split card name)
    - Known typos/mismatches in filenames
    
    Args:
        card_name: The display name of the card
        available_files: Optional set of available filenames (without extension) for smart lookup.
                        If None and cards_dir provided, will scan directory.
        cards_dir: Optional path to images/cards directory for scanning available files.
        base_path: Prefix for the relative image path.
        
    Returns:
        Relative image path like 'images/cards/card-name.png'
    """
    slug = slugify(card_name)
    
    # Scan directory if needed
    if available_files is None and cards_dir is not None:
        if cards_dir.exists():
            available_files = {f.stem for f in cards_dir.glob('*.png')}
        else:
            available_files = set()
    
    # Try exact match first
    if available_files and slug in available_files:
        return f'{base_path}/{slug}.png'
    
    # For split cards, look for longer filename starting with short name + hyphen
    if available_files:
        matching_files = [f for f in available_files if f.startswith(slug + '-')]
        if matching_files:
            return f'{base_path}/{matching_files[0]}.png'
    
    # Known typos/mismatches - map to correct filenames
    TYPO_MAP = {
        'rabid-attach': 'rabid-attack',
        'tenured-concoctor': 'tenured-concocter',
    }
    if slug in TYPO_MAP:
        return f'{base_path}/{TYPO_MAP[slug]}.png'
    
    # Return the expected path even if file doesn't exist (for debugging)
    return f'{base_path}/{slug}.png'


def extract_card_name(display_text: str) -> str:
    """
    Extract clean card name from display text, removing parenthetical tags.
    
    Removes tags like (CT), (MF), etc. that may appear at the end of card names.
    
    Args:
        display_text: The raw display text, possibly with tags
        
    Returns:
        Cleaned card name without trailing parenthetical tags
        
    Example:
        >>> extract_card_name("Lightning Bolt (CT)")
        'Lightning Bolt'
        >>> extract_card_name("Mountain (MF)")
        'Mountain'
    """
    # Remove parenthetical tags at end like (CT), (MF)
    match = re.match(r'^(.+?)\s*\([A-Z]+\)\s*$', display_text.strip())
    if match:
        return match.group(1).strip()
    return display_text.strip()
