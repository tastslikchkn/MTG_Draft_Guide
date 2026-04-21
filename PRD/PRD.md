# Product Requirements Document: MTG Draft Guide
## Secrets of Strixhaven Interactive Reference System

---

## 📋 Executive Summary

**Product:** Interactive HTML draft guide for Magic: The Gathering - Secrets of Strixhaven  
**Platform:** Responsive web application (mobile-first, print-friendly)  
**User:** Dan - MTG player preparing for weekend draft events  
**Goal:** Reliable, beautiful reference guide that works perfectly on phone during draft and prints cleanly

### Core Value Proposition
A single-file HTML solution that provides:
- **100% image reliability** through multi-tier fallback strategy
- **Mobile-first design** optimized for thumb navigation on small screens
- **Print-ready output** with clean grayscale-friendly layout
- **Zero dependencies** - works offline, no build step required

---

## 🎯 User Stories & Requirements

### Primary User Story
> As a MTG player at a draft event, I want to quickly reference card information and archetype strategies on my phone so that I can make informed picks without relying on memory or asking other players.

### Secondary User Story  
> As someone preparing for a draft, I want to print the guide as a backup so that I have a physical copy if my phone battery dies or internet is unavailable.

---

## 📱 Functional Requirements

### FR-1: Mobile-First Design
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Touch-friendly interface with minimum 44px tap targets | Must Have |
| FR-1.2 | Responsive layouts scaling from 320px to desktop widths | Must Have |
| FR-1.3 | Sticky navigation accessible at all scroll positions on mobile | Should Have |
| FR-1.4 | Horizontal scrolling bombs section with smooth thumb interaction | Must Have |
| FR-1.5 | Minimum 16px body text, scalable headings | Must Have |

### FR-2: Print-Friendly Output
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Clean black/white optimized print layout | Must Have |
| FR-2.2 | Page breaks prevent cards from splitting across pages | Must Have |
| FR-2.3 | Hidden interactive elements (nav pills, shadows) on print | Should Have |
| FR-2.4 | Card images scale appropriately for letter/A4 paper | Must Have |

### FR-3: Image Reliability (CRITICAL)
**Requirement: Every single card image MUST display - no exceptions.**

Multi-tier fallback strategy:
```
Tier 1: Scryfall API (normal format) → Primary source
Tier 2: Scryfall borderless (border-cropped) → Secondary source  
Tier 3: Cardmarket API proxy → Tertiary source
Tier 4: Local cached images (/images/cards/) → Offline backup
Tier 5: Styled placeholder with card name → Last resort
```

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Lazy loading for performance (`loading="lazy"`) | Must Have |
| FR-3.2 | Preload critical above-fold images | Should Have |
| FR-3.3 | Fallback to text-only display with color badge if all fail | Must Have |
| FR-3.4 | Console logging of failed images for debugging | Nice to Have |

### FR-4: Content Sections
| Section | Purpose | Mobile Priority | Status |
|---------|---------|-----------------|--------|
| 📚 Draft Tips | Quick strategy reminders | High - visible on load | ✅ Implemented |
| ⚠️ Trap Commons | Cards to avoid early | Medium | ✅ Implemented |
| 💣 Bomb Rares/Mythics | Best-in-slot cards by color | High | ✅ Implemented |
| ⭐ Top Commons | Strong common/uncommon picks | High | ✅ Implemented |
| 🎯 Archetypes | Color pair strategies + combos | Medium | ✅ Implemented |

### FR-5: Performance Targets
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Mobile load time (4G) | < 3 seconds | Lighthouse mobile |
| First Contentful Paint | < 1 second | Lighthouse mobile |
| Image size per card | Max 200KB | File inspection |
| Total page weight | Under 5MB | Network tab |

---

## 🛠 Technical Specifications

### TS-1: Browser Support Matrix
| Platform | Version | Priority |
|----------|---------|----------|
| Chrome/Edge (iOS) | Latest 2 | Primary |
| Safari (iOS) | Latest 2 | Primary |
| Chrome (Android) | Latest 2 | Secondary |
| Firefox Desktop | Latest | Compatibility |

### TS-2: Responsive Breakpoints
```css
/* Mobile-first approach */
Mobile Portrait:    320px - 479px   /* iPhone SE, small phones */
Mobile Landscape:   480px - 767px   /* Large phones landscape */
Tablet:            768px - 1023px   /* iPad portrait */
Desktop:           1024px+          /* Laptops, desktops, print */
```

### TS-3: Print Specifications
| Parameter | Value |
|-----------|-------|
| Paper size | Letter (US) / A4 |
| Margins | 0.5 inch minimum |
| Orientation | Portrait preferred, Landscape optional |
| Color mode | Grayscale compatible |
| Target pages | Under 5 pages |

### TS-4: Image Specifications
| Type | Format | Max Size | Notes |
|------|--------|----------|-------|
| Card images (online) | PNG via Scryfall API | ~100KB each | Normal format preferred |
| Card images (cached) | PNG locally | < 200KB each | Compressed if needed |
| Fallback placeholder | CSS-generated | N/A | No image required |

---

## 🗂 Data Model & Architecture

### DM-1: Card Data Structure
```python
class CardData:
    name: str                    # "Elite Interceptor // Rejoinder"
    mana_cost: str              # "{2}{W}"
    type_line: str             # "Creature — Human Soldier"
    oracle_text: str           # Full rules text
    colors: List[str]          # ["W"] or ["W", "U"]
    color_identity: List[str]  # For commander legality
    rarity: str                # "common", "uncommon", "rare", "mythic"
    image_path: Optional[str]  # Local path if cached
```

### DM-2: Color Group Classification
```python
COLOR_GROUPS = [
    "mono_white",   # Single white mana symbol
    "mono_blue",    # Single blue mana symbol
    "mono_black",   # Single black mana symbol
    "mono_red",     # Single red mana symbol
    "mono_green",   # Single green mana symbol
    "multicolor",   # Two or more colors
    "colorless",    # No colored mana symbols
]
```

### DM-3: Rarity Ordering (Descending)
```python
RARITY_ORDER = {
    "mythic": 0,     # M - Gold
    "rare": 1,       # R - Red
    "uncommon": 2,   # U - Green
    "common": 3,     # C - Gray
}
```

---

## 🔌 API Integration Specifications

### API-1: Scryfall API (Primary)
| Endpoint | Purpose | Rate Limit |
|----------|---------|------------|
| `/cards/named/{name}` | Fetch single card by name | 1 req/sec |
| `/cards/search?q={query}` | Search cards | 1 req/sec |

**Image URL Format:**
```
https://api.scryfall.com/cards/named/fuzzy={card_name}&format=normal
→ Returns JSON with image_uris.normal, image_uris.art_crop, etc.
```

### API-2: JustTCG API (Secondary - Price Data)
| Endpoint | Purpose | Authentication |
|----------|---------|---------------|
| `/cards?game=magic-the-gathering&q={name}` | Card prices | X-API-Key header |

**Response Structure:**
```json
{
  "data": [{
    "prices": {
      "near_mint_normal": {"avg_price_7d": 0.25}
    }
  }]
}
```

---

## 🧪 Testing Strategy

### TT-1: Image Reliability Tests
| Test | Method | Success Criteria |
|------|--------|------------------|
| All cards display | Visual inspection on Chrome DevTools mobile emulator | 100% images visible |
| Fallback chain works | Block Scryfall, verify local fallback kicks in | No broken image icons |
| Offline mode | Disable network, reload page | Cached images still load |

### TT-2: Mobile Compatibility Tests
| Device/Emulator | Test Cases |
|-----------------|------------|
| iPhone SE (375px) | All sections readable at 100% zoom |
| iPhone 14 Pro Max (430px) | Thumb reachability for all nav elements |
| Android Pixel (360px) | Horizontal scroll works smoothly |

### TT-3: Print Tests
| Test | Method | Success Criteria |
|------|--------|------------------|
| Page breaks | Chrome Print Preview → PDF | No cards cut in half |
| Grayscale readability | Print preview grayscale mode | All text legible |
| Page count | Count pages in PDF | Under 5 pages |

---
## 📅 Implementation Phases & Timeline

### Phase 1: Foundation Fixes (Week 1)
**Goal:** Fix critical bugs, establish baseline functionality

| Task | Est. Time | Status |
|------|-----------|--------|
| Fix missing `urllib.parse` import in api.py | 5 min | ✅ Done |
| Remove duplicate function in card_data.py | 5 min | ✅ Done |
| Add `.env` support for API keys | 30 min | ✅ Done |
| Create `requirements.txt` | 10 min | ✅ Done |

### Phase 2: Image Reliability (Week 1-2)
**Goal:** Achieve 100% image display rate

| Task | Est. Time | Status |
|------|-----------|--------|
| Research Cardmarket API format | 30 min | 🔴 TODO |
| Add CMC fallback tier to JavaScript | 1 hour | 🔴 TODO |
| Write Python script to download all card images | 2 hours | 🔴 TODO |
| Update HTML with local image paths | 1 hour | 🔴 TODO |
| Test each fallback tier independently | 1 hour | 🔴 TODO |

### Phase 3: Mobile Optimization (Week 2)
**Goal:** Perfect mobile experience

| Task | Est. Time | Status |
|------|-----------|--------|
| Reduce card hover scale from 2.0x to 1.1x | 15 min | 🔴 TODO |
| Fix bombs horizontal scroll (webkit-overflow) | 30 min | 🔴 TODO |
| Add sticky navigation header for mobile | 1 hour | 🔴 TODO |
| Ensure all tap targets ≥44px | 30 min | 🔴 TODO |

### Phase 4: Print Support (Week 2-3)
**Goal:** Professional print output

| Task | Est. Time | Status |
|------|-----------|--------|
| Add `@media print` stylesheet | 1 hour | 🔴 TODO |
| Implement page break control (`break-inside: avoid`) | 30 min | 🔴 TODO |
| Hide nav pills on print | 15 min | 🔴 TODO |
| Convert to grayscale-friendly colors | 45 min | 🔴 TODO |

### Phase 5: Performance & Polish (Week 3)
**Goal:** Meet performance targets, add finishing touches

| Task | Est. Time | Status |
|------|-----------|--------|
| Add `loading="lazy"` to all images | 15 min | 🔴 TODO |
| Preload critical bomb images in `<head>` | 30 min | 🔴 TODO |
| Run Lighthouse audit, optimize to score >80 | 2 hours | 🔴 TODO |
| Add ARIA labels for accessibility | 45 min | 🔴 TODO |

---

## 📊 Success Metrics (KPIs)

### Must-Have (MVP) Criteria
- [ ] **100% image display rate** on mobile Chrome/Safari
- [ ] Page readable at **100% zoom on iPhone SE** (375px width)
- [ ] Print preview shows clean layout without cut-off content
- [ ] Navigation works with thumb reach on large phones
- [ ] Load time under **5 seconds on mobile 4G**

### Nice-to-Have Criteria
- [ ] Offline capability via service worker caching
- [ ] Search/filter cards by name functionality
- [ ] Toggle between compact/detailed views
- [ ] Shareable deep links to specific archetypes

---

## 🚨 Known Issues & Technical Debt

| Issue | Impact | Fix Priority |
|-------|--------|--------------|
| No lazy loading on images | Slower mobile load times | 🟢 Low - Quick fix available |
| Card hover scale too aggressive (2.0x) | Breaks layout on small screens | 🟡 Medium - Mobile UX issue |

---

## 📁 Project Structure Reference

```
MTG_Draft_Guide/
├── PRD/                          # This document + checklist
│   ├── PRD.md                   # ← You are here
│   └── checklist.md             # Task tracking
│
├── scripts/
│   ├── utils/                   # Centralized modules (DO NOT MODIFY)
│   │   ├── __init__.py         # Main exports + API config
│   │   ├── api.py              # Scryfall/JustTCG clients
│   │   ├── card_data.py        # Card name handling, HTML parsing
│   │   ├── color_rarity.py     # Color groups, rarity ordering
│   │   └── html_templates.py   # Gallery HTML generation
│   │
│   ├── archive/                 # Legacy scripts (REFERENCE ONLY)
│   │   └── *.py                # 18 archived scripts
│   │
│   └── draft_sources/           # Raw draft notes
│       ├── StixhavenDraft.txt  # Original text notes
│       └── StrixhavenDraft.md  # Markdown version
│
├── html_json/                   # Generated output files
│   ├── strixhaven-draft-guide.html  # Main guide
│   ├── card-gallery.html        # Full set gallery
│   ├── pauper-decks.html        # Common-only decks
│   └── *.json                  # Cached data
│
├── images/                      # Local image cache
│   └── cards/                  # Downloaded card PNGs
│
└── index.html                   # Navigation hub
```

---

## 🎓 Glossary & References

### MTG Terms
| Term | Definition |
|------|------------|
| Draft | Limited format where players build decks from sealed booster packs |
| Bomb | Powerful rare/mythic card that wins games single-handedly |
| Trap common | Weak common card that looks good but isn't |
| Converge | Strixhaven mechanic: benefits from casting multiple colors |
| Repartee | Strixhaven mechanic: bonuses for instants/sorceries |

### External Resources
- **Scryfall API Docs:** https://docs.scryfall.com/
- **JustTCG API Docs:** https://justtcg.com/api-docs
- **Strixhaven Set Page:** https://scryfall.com/set/sos

---

## 🚀 Upcoming Features (Post-MVP)

### FR-6: Card Search/Filter
**Goal:** Allow users to quickly find specific cards without scrolling

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Text input field for card name search | Must Have |
| FR-6.2 | Real-time filtering as user types | Should Have |
| FR-6.3 | Case-insensitive partial matching | Must Have |
| FR-6.4 | Highlight matched cards visually | Nice to Have |

**Estimated Effort:** 1-2 hours

### FR-7: Performance Optimization
**Goal:** Meet performance targets on mobile

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | Add `loading="lazy"` to all images | ✅ Done |
| FR-7.2 | Preload critical above-fold images | Should Have |
| FR-7.3 | Reduce card hover scale from 2.0x to 1.1x | ✅ Already done (scale(1)) |

**Estimated Effort:** 30 minutes

### FR-8: Use Local Image Cache 🔴
**Goal:** Enable true offline mode by using cached images with Scryfall fallback

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.1 | Update all `<img>` tags to point to `/images/cards/*.jpg` first | Must Have |
| FR-8.2 | Add `onerror` fallback to Scryfall API for missing images | Must Have |
| FR-8.3 | Use `card_image_mapping.json` for filename lookup | Must Have |

**Estimated Effort:** 15 minutes (scripted)

### FR-9: UX Polish
**Goal:** Improve user experience with small enhancements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-9.1 | Add meta description tag for browser tabs/sharing | Nice to Have |
| FR-9.2 | Back-to-top sticky button on scroll | Should Have |
| FR-9.3 | Print test verification (PDF export) | Must Have |

**Estimated Effort:** 20 minutes total

---

## 📝 Change Log

| Version | Date | Changes |
|---------|------|--------|
| 1.2 | April 21, 2026 | Added FR-8 (local image cache usage) and FR-9 (UX polish: meta description, back-to-top button, print test). Marked lazy loading + hover scale as complete. |
| 1.1 | April 21, 2026 | Phase 1 complete: Fixed API key truncation, created requirements.txt + .env.example, cached 92 card images locally (35MB). Added upcoming features section (search/filter, performance optimizations). |
| 1.0 | April 20, 2026 | Initial PRD created from existing docs + codebase review |

---

*Document Owner: Dan Getty*  
*Last Updated: April 20, 2026*  
*Version: 1.0*
