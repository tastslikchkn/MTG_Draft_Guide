# Card Browser Test Checklist

## PRD Version 1.2 — Interactive Card Browser for MTG Draft Guide

**Generated:** April 25, 2026  
**Total Tests:** ~110+ across all categories

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not tested / Pending |
| ✅ | Pass |
| ❌ | Fail |
| 🔄 | In Progress |

---

## US-1: Search for Cards by Name or Text

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| US-1.1 | Search input field prominently displayed at top of page | Input visible with placeholder text and search icon | ⬜ |
| US-1.2 | Type "removal" in search box | Results filter in real-time without button click | ⬜ |
| US-1.3 | Search for "haste" | Cards with "haste" in name OR oracle_text shown | ⬜ |
| US-1.4 | Search for "LIGHTNING" (uppercase) | Case-insensitive: finds "Lightning Bolt" | ⬜ |
| US-1.5 | Results count updates as typing | Display shows filtered card count immediately | ⬜ |

---

## US-2: Filter by Multiple Criteria Simultaneously

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| US-2.1 | Color filter displays five mana symbol buttons (WUBRG) + "All" | Six clickable buttons with Scryfall images | ⬜ |
| US-2.2 | Rarity dropdown shows: All, Common, Uncommon, Rare, Mythic Rare | Five options available | ⬜ |
| US-2.3 | Type dropdown shows main card types | Creature, Instant, Sorcery, Enchantment, Land, Artifact, Planeswalker | ⬜ |
| US-2.4 | Apply Blue + Common + Creature filters together | Only blue common creatures shown (AND logic) | ⬜ |
| US-2.5 | Active filter shows visual feedback | Selected button has border glow/transform effect | ⬜ |

---

## US-3: Sort Cards by Different Criteria

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| US-3.1 | Sort dropdown shows four options | Score (High→Low), CMC (Low→High), Name (A→Z), Rarity (Mythic→Common) | ⬜ |
| US-3.2 | Default sort is Score descending | Highest eval_score cards appear first on load | ⬜ |
| US-3.3 | Sort by CMC ascending | 1-drops, then 2-drops, then 3-drops... | ⬜ |
| US-3.4 | Sorting applies after filtering | Filtered results re-sorted when sort changed | ⬜ |
| US-3.5 | Visual indicator shows current sort order | Dropdown displays selected option | ⬜ |

---

## US-4: View Card Details in Modal

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| US-4.1 | Click any card thumbnail | Modal overlay opens with backdrop dim/blur | ⬜ |
| US-4.2 | Modal displays large card image (PNG quality) | High-resolution image from Scryfall | ⬜ |
| US-4.3 | Modal shows card name, type line, oracle text | All text fields rendered correctly | ⬜ |
| US-4.4 | Mana cost shown as individual symbol images | Each {W}, {U}, etc. is separate image | ⬜ |
| US-4.5 | Power/Toughness displayed for creatures | "3/2" format in bottom-right of card info | ⬜ |
| US-4.6 | Click X button closes modal | Modal disappears, returns to grid | ⬜ |
| US-4.7 | Press Escape key closes modal | Keyboard shortcut works | ⬜ |

---

## US-5: Filter by Mana Cost Range

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| US-5.1 | CMC slider control visible (0 to 20+) | Range input with min=0, max≥20 | ⬜ |
| US-5.2 | Current max value displayed next to slider | Number updates as slider moves | ⬜ |
| US-5.3 | Drag slider to CMC=3 | Only cards with cmc≤3 shown in real-time | ⬜ |
| US-5.4 | Default position at maximum (show all) | Slider starts at rightmost position | ⬜ |

---

## US-6: Clear All Filters

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| US-6.1 | "Clear All" button visible when any filter active | Button appears after applying first filter | ⬜ |
| US-6.2 | Click "Clear All" resets all filters | Search, color, rarity, type, CMC, sort all reset | ⬜ |
| US-6.3 | After clearing, all cards shown immediately | Grid displays full ~850 card set | ⬜ |
| US-6.4 | Button disabled/hidden when no filters active | Not visible on initial page load | ⬜ |

---

## FR-1: Data Loading

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-1.1 | Page loads and fetches evaluated_sos.json | JSON loaded successfully from same directory | ⬜ |
| FR-1.2 | Loading spinner displayed while fetching | Visual feedback during network request | ⬜ |
| FR-1.3.1 | JSON file not found → error banner displays | Message: "Card data unavailable..." shown inline | ⬜ |
| FR-1.3.2 | Error includes retry button | Clicking re-attempts fetch | ⬜ |
| FR-1.3.3 | Detailed error logged to console | Developer can see fetch failure details | ⬜ |
| FR-1.4 | ~850 cards load without performance issues | Page remains responsive during render | ⬜ |

---

## FR-2: Search Functionality

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-2.1 | Search input has placeholder text and icon | "Search cards..." or similar hint visible | ⬜ |
| FR-2.2 | Real-time filtering as user types | No Enter key required, instant results | ⬜ |
| FR-2.3 | Search matches card.name field | Typing card name finds it | ⬜ |
| FR-2.4 | Search matches card.oracle_text field | Typing "draw a card" finds draw spells | ⬜ |
| FR-2.5 | Case-insensitive matching | "BOLT", "Bolt", "bolt" all work | ⬜ |
| FR-2.6 | Clear search restores all cards | Deleting text shows full set again | ⬜ |
| FR-2.7 | Partial match supported ("light" → "Lightning Bolt") | Substring matching works | ⬜ |
| FR-2.8 | No fuzzy matching — exact substring only | "lghtng" does NOT find "Lightning" | ⬜ |

---

## FR-3: Color Filtering

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-3.1 | Five colored mana symbol buttons displayed (WUBRG) | Using Scryfall PNG images | ⬜ |
| FR-3.2 | "All" button shows cards of any color | Default state, all cards visible | ⬜ |
| FR-3.3 | Active state has visual feedback (glow/transform) | Selected button stands out | ⬜ |
| FR-3.4 | Single-select behavior only one color active at a time | Clicking Blue deselects Red automatically | ⬜ |
| FR-3.5 | Filter excludes non-matching colors AND multicolor when single selected | Clicking White shows ONLY white cards (no W/B, W/U, etc.) | ⬜ |

---

## FR-4: Rarity Filtering

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-4.1 | Dropdown options: All, Common, Uncommon, Rare, Mythic Rare | Five choices available | ⬜ |
| FR-4.2 | "Mythic" option maps to `mythic_rare` in JSON | Selecting shows mythic rare cards only | ⬜ |
| FR-4.3 | Default selection is "All Rarities" | Page loads with all rarities shown | ⬜ |

---

## FR-5: Type Filtering

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-5.1 | Dropdown shows main card types as options | Creature, Instant, Sorcery, etc. | ⬜ |
| FR-5.2 | Extracts main type from type_line (before " — ") | "Creature — Human Wizard" → "Creature" | ⬜ |
| FR-5.3 | Handles subtype variations correctly | All creature subtypes grouped under "Creature" | ⬜ |
| FR-5.4 | "Basic Land" extracted as "Land" (grouped with all lands) | Forest, Island, Mountain, Plains, Swamp all show under Land filter | ⬜ |
| FR-5.5 | Double-faced cards use front face type for filtering | DFC filtered by front face main type | ⬜ |

---

## FR-6: CMC Filtering

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-6.1 | Range slider from 0 to 20+ | Min=0, max≥20 available | ⬜ |
| FR-6.2 | Current max value displayed next to slider | Numeric display updates live | ⬜ |
| FR-6.3 | Filters cards where cmc ≤ selected_value | Slider at 5 shows only CMC 0-5 cards | ⬜ |

---

## FR-7: Sorting

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-7.1 | Four sort options in dropdown | Score, CMC, Name, Rarity available | ⬜ |
| FR-7.2 | Score descending uses eval_score field (default 0 if missing) | Cards with no score appear at bottom | ⬜ |
| FR-7.3 | CMC ascending sorts numerically | 1 < 2 < 3, not lexicographically | ⬜ |
| FR-7.4 | Name ascending uses localeCompare for proper alphabetical order | "A" before "B", handles special chars | ⬜ |
| FR-7.5 | Rarity descending: Mythic > Rare > Uncommon > Common | Correct hierarchy enforced | ⬜ |

---

## FR-8: Card Display

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-8.1 | Grid layout with responsive columns (auto-fill, min 200px) | Cards wrap based on viewport width | ⬜ |
| FR-8.2 | Each card shows image, name, type, rarity badge | All four elements visible per card | ⬜ |
| FR-8.3 | Rarity badges color-coded correctly | Common=bronze, Uncommon=silver, Rare=purple, Mythic=orange | ⬜ |
| FR-8.4 | Hover effect with lift and shadow | Card elevates on mouseover | ⬜ |
| FR-8.5 | Lazy loading for card images | `loading="lazy"` attribute present | ⬜ |

---

## FR-9: Pagination

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-9.1 | Display 48 cards per page (configurable) | First load shows exactly 48 cards | ⬜ |
| FR-9.2 | Previous/Next buttons with disabled state at boundaries | "Previous" disabled on page 1, "Next" disabled on last page | ⬜ |
| FR-9.3 | Page number buttons for direct navigation | Click "5" jumps to page 5 | ⬜ |
| FR-9.4 | Result count displayed: "Showing X cards" | Accurate count of filtered results | ⬜ |

---

## FR-10: Modal Details View

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-10.1 | Full-screen overlay with backdrop blur/dim | Background dimmed, focus on modal | ⬜ |
| FR-10.2 | Large card image (PNG quality from Scryfall) | High-res PNG displayed | ⬜ |
| FR-10.3 | Card name, type line, oracle text displayed | All fields rendered | ⬜ |
| FR-10.4 | Mana cost rendered as individual symbol images | Each mana symbol is separate image element | ⬜ |
| FR-10.5 | Power/Toughness shown for creatures | P/T values visible in modal | ⬜ |
| FR-10.6 | Close on Escape keypress | Keyboard shortcut functional | ⬜ |
| FR-10.7 | Close on overlay click (outside modal content) | Clicking backdrop closes modal | ⬜ |

---

## FR-11: Accessibility

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-11.1 | All interactive elements reachable via Tab key | Focus moves through all buttons, inputs, cards | ⬜ |
| FR-11.2 | Modal traps focus when open, returns on close | Tab cycling stays within modal; closes → focus returns to grid | ⬜ |
| FR-11.3 | Card images have alt text with card name | `alt="Card Name"` present on all thumbnails | ⬜ |
| FR-11.4 | Color filter buttons include text labels for screen readers | `alt="White"`, `alt="Blue"`, etc. or aria-label | ⬜ |
| FR-11.5 | Error messages announced to screen readers | Uses role="alert" or aria-live for errors | ⬜ |

---

## FR-12: Data Validation

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| FR-12.1 | Validate JSON structure on load (required fields present) | Missing required fields detected | ⬜ |
| FR-12.2 | Skip cards with missing `name` or `image_uris.normal` silently | Invalid cards not rendered, no crash | ⬜ |
| FR-12.3 | Default `eval_score` to 0 if missing or invalid | Cards without score sort to bottom | ⬜ |
| FR-12.4 | Log validation errors to console with card ID for debugging | Developer can identify problematic cards | ⬜ |
| FR-12.5 | Display warning banner if >5% of cards skipped due to validation failures | User notified of significant data issues | ⬜ |

---

## TC-5: Edge Cases

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| TC-5.1 | Search for non-existent term "xyz123" | Shows 0 results, displays "No cards match your criteria" message | ⬜ |
| TC-5.2 | Search with special characters "!@#" | Treated literally as substring search, no regex interpretation | ⬜ |
| TC-5.3 | CMC slider at minimum (0) | Only shows cards with CMC = 0 (e.g., some artifacts like "Sol Ring") | ⬜ |
| TC-5.4 | All filters combined yielding 0 results | Graceful "No cards match" message with suggestion to clear filters | ⬜ |
| TC-5.5 | Card name with apostrophe "It That Ain't Dead Yet" | Search handles correctly without escaping issues | ⬜ |
| TC-5.6 | Empty search after clearing | Restores all cards immediately | ⬜ |

---

## Browser Compatibility Tests

Run each core functionality test on:

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| **Chrome** | 87+ (latest) | ⬜ | Primary development browser |
| **Firefox** | 88+ (latest) | ⬜ | Secondary testing |
| **Safari** | 14+ (macOS/iOS) | ⬜ | CSS Grid support verification |
| **Edge** | 87+ (Chromium) | ⬜ | Should match Chrome behavior |

---

## NFR: Security Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| NFR-S1 | All external images loaded from HTTPS sources only | No HTTP image URLs in page source | ⬜ |
| NFR-S2 | No user input stored or transmitted — entirely client-side | Network tab shows no POST requests with user data | ⬜ |
| NFR-S3 | No third-party analytics or tracking scripts | No Google Analytics, no cookies set by third parties | ⬜ |

---

## NFR: Reliability Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| NFR-R1 | Page functions entirely offline after initial load (cacheable) | Reload with network disabled works (if cached) | ⬜ |
| NFR-R2 | Graceful degradation if Scryfall image CDN unavailable | Placeholder shown, page doesn't break | ⬜ |

---

## NFR: Maintainability Checks

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| NFR-M1 | Single HTML file, no build step required | Works by opening card-browser.html directly | ⬜ |
| NFR-M2 | Inline CSS/JS documented with comments for future editors | Code has explanatory comments | ⬜ |
| NFR-M3 | Variable/function names follow consistent naming conventions (camelCase) | No snake_case or PascalCase in JS | ⬜ |

---

## Performance Tests

| # | Test Case | Expected Result | Status |
|---|-----------|-----------------|--------|
| PERF-1 | Initial load time < 2s on local server | JSON (~1.6MB) loads and renders quickly | ⬜ |
| PERF-2 | Filter response time < 100ms | Changing filters feels instant | ⬜ |
| PERF-3 | Memory usage < 50MB in browser DevTools | No memory leaks during extended use | ⬜ |
| PERF-4 | Mobile viewport (375px) grid collapses to 2 columns | Responsive design works on phone-sized screen | ⬜ |

---

## Summary Statistics

```
Total Tests: ~110+
├── User Stories:        27 tests
├── Functional Req:      60+ tests  
├── Edge Cases:          6 tests
├── Browser Compat:      4 browsers × core features
├── NFRs (Security):     3 tests
├── NFRs (Reliability):  2 tests
├── NFRs (Maintainability): 3 tests
└── Performance:         4 tests
```

---

## How to Use This Checklist

1. **Copy into spreadsheet** or project management tool
2. **Run tests systematically** by category
3. **Mark status**: ⬜ = Not tested, ✅ = Pass, ❌ = Fail
4. **Document failures** with screenshots and steps to reproduce
5. **Retest after fixes** until all green

---

## Test Execution Template

```
Test Run: ___________
Date: _______________
Tester: _____________
Browser/Version: ________________________
Build/Commit: ___________________________

Results Summary:
├── Passed: ___ / ___
├── Failed: ___ / ___  
└── Blocked: ___ / ___

Notes:
_____________________________________________
_____________________________________________
```
