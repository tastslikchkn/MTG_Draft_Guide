"""
Color group determination and rarity ordering utilities.
Centralized logic for categorizing MTG cards by color and rarity.
"""

from typing import List, Dict, Any, Tuple


# ============================================================================
# COLOR CONSTANTS AND MAPPINGS
# ============================================================================

# Color letter to name mapping
COLOR_NAMES = {
    'W': 'white',
    'U': 'blue', 
    'B': 'black',
    'R': 'red',
    'G': 'green'
}

# Display names for color groups
COLOR_GROUP_DISPLAY = {
    'mono_white': 'White',
    'mono_blue': 'Blue',
    'mono_black': 'Black',
    'mono_red': 'Red',
    'mono_green': 'Green',
    'multicolor': 'Multicolor',
    'colorless': 'Colorless',
    'lands': 'Lands'
}

# Order for displaying color groups (mono first, then multi, then special)
COLOR_GROUP_ORDER = [
    'mono_white',
    'mono_blue', 
    'mono_black',
    'mono_red',
    'mono_green',
    'multicolor',
    'colorless',
    'lands'
]

# CSS classes for color-coded backgrounds
COLOR_CSS_CLASSES = {
    'colorless': 'bg-gray-200 border-gray-400',
    'mono_white': 'bg-white border-blue-200',
    'mono_blue': 'bg-blue-50 border-blue-300',
    'mono_black': 'bg-gray-100 border-purple-300',
    'mono_red': 'bg-red-50 border-orange-300',
    'mono_green': 'bg-green-50 border-green-300',
    'multicolor': 'bg-yellow-50 border-pink-300',
    'lands': 'bg-purple-50 border-indigo-300'
}

# Section titles for HTML output
COLOR_SECTIONS = {
    'mono_white': ('White Cards', '#E3F2FD'),
    'mono_blue': ('Blue Cards', '#BBDEFB'),
    'mono_black': ('Black Cards', '#F3E5F5'),
    'mono_red': ('Red Cards', '#FFCDD2'),
    'mono_green': ('Green Cards', '#DCEDC8'),
    'multicolor': ('Multicolor Cards', '#FFF9C4'),
    'colorless': ('Colorless Cards', '#EEEEEE'),
    'lands': ('Lands', '#E1BEE7')
}


# ============================================================================
# RARITY CONSTANTS AND MAPPINGS  
# ============================================================================

# Rarity order for sorting (descending - mythic first)
RARITY_ORDER = {
    'mythic': 0,
    'rare': 1,
    'uncommon': 2, 
    'common': 3,
    'special': 4,
    'land': 5
}

# Rarity letter codes
RARITY_LETTERS = {
    'mythic': 'M',
    'rare': 'R',
    'uncommon': 'U',
    'common': 'C',
    'special': 'S',
    'land': 'L'
}

# Rarity display colors (hex)
RARITY_COLORS = {
    'M': '#FFD700',  # Gold for mythic
    'R': '#C41E3A',  # Red for rare
    'U': '#228B22',  # Green for uncommon
    'C': '#696969',  # Gray for common
    'S': '#FF69B4',  # Pink for special
    'L': '#8FBC8F'   # Dark sea green for land
}

# Rarity info for display
RARITY_INFO = {
    'mythic': {'letter': 'M', 'color': '#FFD700', 'name': 'Mythic Rare'},
    'rare': {'letter': 'R', 'color': '#C41E3A', 'name': 'Rare'},
    'uncommon': {'letter': 'U', 'color': '#228B22', 'name': 'Uncommon'},
    'common': {'letter': 'C', 'color': '#696969', 'name': 'Common'}
}


# ============================================================================
# COLOR GROUP DETERMINATION FUNCTIONS
# ============================================================================

def get_color_group(colors: List[str]) -> str:
    """
    Determine color group from actual card colors.
    
    Args:
        colors: List of color letters (e.g., ['W'], ['W', 'U], [])
        
    Returns:
        Color group string: mono_white, mono_blue, etc.
        
    Examples:
        >>> get_color_group(['W'])
        'mono_white'
        >>> get_color_group(['W', 'U'])
        'multicolor'
        >>> get_color_group([])
        'colorless'
    """
    if not colors:
        return 'colorless'
    
    unique_colors = set(colors)
    
    if len(unique_colors) == 1:
        # Mono-colored
        color = list(unique_colors)[0]
        color_name = COLOR_NAMES.get(color, '')
        if color_name:
            return f"mono_{color_name}"
    
    # Multiple colors or unknown
    return 'multicolor'


def get_color_group_for_card(
    card_data: Dict[str, Any]
) -> str:
    """
    Determine color group from full card data dict.
    Handles lands and special cases.
    
    Args:
        card_data: Card dictionary with 'colors' and optionally 'type_line'
        
    Returns:
        Color group string including 'lands' for land cards
    """
    colors = card_data.get('colors', [])
    type_line = card_data.get('type_line', '')
    
    if not colors:
        # Check if it's a land
        if 'Land' in type_line:
            return 'lands'
        return 'colorless'
    
    unique_colors = set(colors)
    
    if len(unique_colors) == 1:
        color = list(unique_colors)[0]
        color_name = COLOR_NAMES.get(color, '')
        if color_name:
            return f"mono_{color_name}"
    
    return 'multicolor'


# ============================================================================
# RARITY HANDLING FUNCTIONS
# ============================================================================

def get_rarity_from_string(rarity_str: str) -> str:
    """
    Normalize rarity string to standard form.
    
    Args:
        rarity_str: Rarity as string (can be 'M', 'mythic', 'Mythic Rare', etc.)
        
    Returns:
        Normalized rarity: 'mythic', 'rare', 'uncommon', or 'common'
    """
    rarity_lower = rarity_str.lower().strip()
    
    # Handle letter codes
    if rarity_lower == 'm':
        return 'mythic'
    elif rarity_lower == 'r':
        return 'rare'
    elif rarity_lower == 'u':
        return 'uncommon'
    elif rarity_lower == 'c':
        return 'common'
    
    # Handle full names
    if 'mythic' in rarity_lower:
        return 'mythic'
    elif 'rare' in rarity_lower:
        return 'rare'
    elif 'uncommon' in rarity_lower:
        return 'uncommon'
    
    return 'common'  # Default


def get_rarity_letter(rarity: str) -> str:
    """
    Get single-letter code for rarity.
    
    Args:
        rarity: Rarity string ('mythic', 'rare', etc.)
        
    Returns:
        Single letter: M, R, U, or C
    """
    normalized = get_rarity_from_string(rarity)
    return RARITY_LETTERS.get(normalized, 'C')


def get_rarity_color(rarity: str) -> str:
    """
    Get hex color for rarity indicator.
    
    Args:
        rarity: Rarity string or letter
        
    Returns:
        Hex color string (e.g., '#FFD700' for mythic)
    """
    letter = get_rarity_letter(rarity)
    return RARITY_COLORS.get(letter, '#696969')


def get_rarity_sort_key(rarity: str) -> int:
    """
    Get numeric sort key for rarity (lower = higher priority).
    
    Args:
        rarity: Rarity string
        
    Returns:
        Integer sort key (0=mythic, 1=rare, etc.)
    """
    normalized = get_rarity_from_string(rarity)
    return RARITY_ORDER.get(normalized, 3)


# ============================================================================
# SORTING HELPERS
# ============================================================================

def sort_cards_by_color_then_rarity(
    cards: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Sort cards by color group order, then rarity, then name.
    
    Args:
        cards: List of card dictionaries
        
    Returns:
        New sorted list (original unchanged)
    """
    def sort_key(card):
        color_group = get_color_group_for_card(card)
        rarity = card.get('rarity', 'common')
        name = card.get('name', '')
        
        return (
            COLOR_GROUP_ORDER.index(color_group) if color_group in COLOR_GROUP_ORDER else 99,
            get_rarity_sort_key(rarity),
            name.lower()
        )
    
    return sorted(cards, key=sort_key)


def group_cards_by_color(
    cards: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group cards into color categories.
    
    Args:
        cards: List of card dictionaries
        
    Returns:
        Dict mapping color groups to lists of cards in that group
    """
    from collections import defaultdict
    
    groups = defaultdict(list)
    
    for card in cards:
        color_group = get_color_group_for_card(card)
        groups[color_group].append(card)
    
    return dict(groups)


def group_cards_by_rarity(
    cards: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group cards into rarity categories.
    
    Args:
        cards: List of card dictionaries
        
    Returns:
        Dict mapping rarities to lists of cards
    """
    from collections import defaultdict
    
    groups = {
        'mythic': [],
        'rare': [],
        'uncommon': [],
        'common': []
    }
    
    for card in cards:
        rarity = get_rarity_from_string(card.get('rarity', 'common'))
        if rarity in groups:
            groups[rarity].append(card)
    
    return groups


# ============================================================================
# PRICE FUNCTIONS (for gallery display)
# ============================================================================

def get_avg_price_7d(prices: Dict[str, Any]) -> float | None:
    """
    Get average price over 7 days from prices dict.
    
    Args:
        prices: Dictionary with 'usd' key containing price
        
    Returns:
        Average USD price or None if not available
    """
    if not prices:
        return None
    usd_price = prices.get('usd')
    if usd_price is not None:
        try:
            return float(usd_price)
        except (ValueError, TypeError):
            pass
    return None


def format_price(price: float | None) -> str:
    """
    Format price for display.
    
    Args:
        price: Price in USD
        
    Returns:
        Formatted price string (e.g., "$0.25") or empty string
    """
    if price is None:
        return ''
    return f"${price:.2f}"
