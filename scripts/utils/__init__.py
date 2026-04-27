"""
Shared utilities for MTG Draft Guide scripts.
Provides common functions and constants used across multiple modules.

This is the main entry point - imports everything from submodules for easy access:
    from scripts.utils import fetch_card_by_name, get_color_group, slugify
"""

import os
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / '.env')
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

import re
from typing import Any # Removed Optional, Dict, List as we use | None and built-ins

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Load from environment variables (set in .env or system)
JUSTTCG_API_KEY = os.getenv('JUSTTCG_API_KEY', '')
JUSTTCG_GAME_ID = os.getenv('JUSTTCG_GAME_ID', 'magic-the-gathering')


# ============================================================================
# IMPORTS FROM SUBMODULES
# ============================================================================
# Import everything from submodules so users can access via scripts.utils.*

from .api import (
    # HTTP client
    make_request,
    
    # Scryfall API
    fetch_card_by_name,
    fetch_card_image_url,
    download_card_image,
    search_cards,
    batch_download_images,
    fetch_set_cards,  # NEW: paginated set fetching
    
    # JustTCG API  
    fetch_card_by_name_justtcg,
    extract_price_data as api_extract_price_data,
    
    # Unified price extraction
    get_avg_price_from_cache,
    
    # Card evaluation (Limited format)
    calculate_power_level,
    calculate_creature_power_level,
    calculate_spell_power_level,
    get_power_level_tier,
    calculate_draft_priority_score,
    add_card_evaluations,
    get_card_keywords,
    
    # Value-based evaluation (NEW)
    calculate_value_score,
    identify_bomb,
    classify_card_value,
    add_value_evaluations,
    RARITY_POWER_BASELINES,  # Export constant for debugging/tuning
    
    # Combo detection (NEW)
    extract_synergy_tags,
    find_combos_for_card,
    detect_archetype_combos,
    add_combo_evaluations,
    SYNERGY_PATTERNS,
    ARCHETYPES,
)

from .card_data import (
    # String utilities
    sanitize_filename,
    slugify,
    title_case_from_slug,
    clean_card_name,
    extract_card_name,  # NEW: clean display text by removing parenthetical tags
    
    # HTML parsers
    CardNameExtractor,
    extract_card_names_from_html,
    extract_card_names_from_alt_attributes,
    
    # Data model
    CardData,
    
    # File operations
    load_card_cache,
    save_card_cache,
    get_cached_image_paths,
    find_image_file,  # NEW: smart image lookup with typo handling
)

from .color_rarity import (
    # Constants
    COLOR_NAMES,
    COLOR_GROUP_DISPLAY,
    COLOR_GROUP_ORDER,
    COLOR_CSS_CLASSES,
    COLOR_SECTIONS,
    
    RARITY_ORDER,
    RARITY_LETTERS,
    RARITY_COLORS,
    RARITY_INFO,
    
    # Color group functions
    get_color_group,
    get_color_group_for_card,
    
    # Rarity functions
    get_rarity_from_string,
    get_rarity_letter,
    get_rarity_color,
    get_rarity_sort_key,
    
    # Sorting/grouping helpers
    sort_cards_by_color_then_rarity,
    group_cards_by_color,
    group_cards_by_rarity,
)

from .html_templates import (
    # Template functions
    get_gallery_html_template,
    generate_rarity_legend_html,
    generate_card_item_html,
    generate_card_grid_html,
    generate_rarity_group_html,
    generate_color_section_html,
    generate_full_gallery_html,
    save_gallery_html,
)


# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# Kept for backward compatibility with existing scripts
# ============================================================================

def get_color_group_display_name(group: str) -> str:
    """Legacy: Get display name for a color group."""
    return COLOR_GROUP_DISPLAY.get(group, group.replace('_', ' ').title())


def get_rarity_order(rarity: str) -> int:
    """Legacy: Return sort order for rarity (M=0, R=1, U=2, C=3)."""
    return get_rarity_sort_key(rarity)


def get_color_group_order(group: str) -> int:
    """Legacy: Return sort order for color groups."""
    return COLOR_GROUP_ORDER.index(group) if group in COLOR_GROUP_ORDER else 99


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
