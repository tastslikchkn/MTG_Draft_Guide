# Product Requirements Document
## SOS Pauper Decks Webpage

---

## 1. Overview

### 1.1 Purpose
Create a static HTML webpage displaying 6 competitive Magic: The Gathering Standard Pauper deck lists using exclusively Secrets of Strixhaven (SOS) common and uncommon cards.

### 1.2 Target Audience
- MTG draft players preparing for SOS events
- Pauper format enthusiasts exploring new card pools
- Players looking for budget-friendly competitive decks

### 1.3 Success Criteria
- All 60 cards per deck displayed with local images (no external API calls)
- Responsive design matching existing Strixhaven Draft Guide theme
- Fast load times using cached local assets
- Print-friendly layout

---

## 2. Scope

### 2.1 In Scope
| Item | Description |
|------|-------------|
| Single HTML page | `html_json/sos_pauper_decks.html` |
| 6 deck lists | Azorius, Bogardan, Lorehold, Prismari, Forum, Witherbloom |
| Card images | Local files from `images/cards/SOS/` and `images/cards/` |
| Navigation | Sticky nav bar + section pills for each deck |
| Styling | Match existing Strixhaven Draft Guide theme |

### 2.2 Out of Scope
- Scryfall API integration (no live card fetching)
- Interactive deck builder functionality
- Multiple pages or routing
- Backend/database components

---

## 3. Functional Requirements

### FR-1: Deck Display
| ID | Requirement |
|----|-------------|
| FR-1.1 | Each deck shows exactly 60 cards (creatures, spells, lands) |
| FR-1.2 | Cards organized into three subsections: Creatures, Spells, Lands |
| FR-1.3 | Card count displayed next to each card name |
| FR-1.4 | Archetype description and win condition shown above deck list |

### FR-2: Visual Design
| ID | Requirement |
|----|-------------|
| FR-2.1 | Dark gradient background (`#1a1a2e` → `#16213e`) |
| FR-2.2 | Gold accent color (`#fbbf24`) for headers and highlights |
| FR-2.3 | Color-coded left borders per deck archetype |
| FR-2.4 | Card hover effects with lift animation |

### FR-3: Navigation
| ID | Requirement |
|----|-------------|
| FR-3.1 | Sticky navigation bar fixed at top of viewport |
| FR-3.2 | Nav pills linking to each deck section via anchor IDs |
| FR-3.3 | Active state highlighting for current section |

### FR-4: Images
| ID | Requirement |
|----|-------------|
| FR-4.1 | All card images served from local filesystem only |
| FR-4.2 | SOS cards path: `../../images/cards/SOS/{slug}.jpg` |
| FR-4.3 | Non-SOS cards path: `../../images/cards/{slug}.jpg` |
| FR-4.4 | No external API fallbacks or hotlinking |

---

## 4. Technical Specifications

### 4.1 File Locations
```
Project Root: /home/dgetty/repos/MTG_Draft_Guide/
├── html_json/sos_pauper_decks.html (output)
├── images/cards/SOS/*.jpg (SOS card images)
└── images/cards/*.jpg (other set card images)
```

### 4.2 Card Image Naming Convention
- Lowercase with hyphens replacing spaces and apostrophes
- Split cards use `//` separator in filename
- Examples:
  - "Ajani's Response" → `ajanis-response.jpg`
  - "Lluwen, Exchange Student // Pest Friend" → `lluwen-exchange-student-pest-friend.jpg`

### 4.3 Deck Color Mapping
```css
.archetype-bw   { border-color: #fbbf24; }   /* Azorius B/W */
.archetype-br   { border-color: #a855f7; }    /* Bogardan R/G */
.archetype-rw   { border-color: #fb923c; }     /* Lorehold R/W */
.archetype-bur  { border-color: #ec4899; }     /* Prismari B/R */
.archetype-bg   { border-color: #10b981; }     /* Witherbloom B/G */
.archetype-forum{ border-color: #6366f1; }     /* Forum alt B/W */
```

### 4.4 Card Color Classes (for individual cards)
```css
.color-w { border-left: 4px solid #fbbf24; }  /* White/Gold */
.color-u { border-left: 4px solid #3b82f6; }  /* Blue */
.color-b { border-left: 4px solid #525252; }  /* Black */
.color-r { border-left: 4px solid #ef4444; }  /* Red */
.color-g { border-left: 4px solid #22c55e; }  /* Green */
.color-n { border-left: 4px solid #a8a8a8; }  /* Colorless */
```

---

## 5. Deck Data

### 5.1 Deck List Summary
| # | Name | Colors | Strategy |
|---|------|--------|----------|
| 1 | Azorius Control | U/W | Counterspells, bounce, Silverquill Charm value |
| 2 | Bogardan Aggro | R/G | Fast creatures + Ancestral Anger pump |
| 3 | Lorehold Midrange | R/W | Removal suite + Kirol synergy + Colossus finisher |
| 4 | Prismari Tempo | R/U | Fractalize + cheap threats + Visionary's Dance |
| 5 | Forum Control | B/W | Removal, Arnyn value engine |
| 6 | Witherbloom Value | B/G | Lluwen token generation + removal |

### 5.2 Source Data Location
Deck lists stored in: `/home/dgetty/repos/MTG_Draft_Guide/sos_pauper_decks.md`

---

## 6. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Page loads in <2 seconds on standard broadband |
| NFR-2 | Responsive design works on mobile (320px+) and desktop (1920px) |
| NFR-3 | Print-friendly CSS included for physical deck reference |
| NFR-4 | No JavaScript dependencies (pure HTML/CSS) |

---

## 7. Acceptance Criteria

### AC-1: Content Verification
- [ ] All 6 decks present with correct names and color pairs
- [ ] Each deck contains exactly 60 cards total
- [ ] Creatures, Spells, Lands subsections clearly labeled
- [ ] Archetype descriptions match source document

### AC-2: Visual Verification
- [ ] Theme matches strixhaven-draft-guide.html
- [ ] Color borders correctly applied per archetype
- [ ] Card hover animations functional
- [ ] Sticky nav bar stays fixed on scroll

### AC-3: Image Verification
- [ ] All card images load from local paths
- [ ] No broken image icons visible
- [ ] SOS cards use `../../images/cards/SOS/` path
- [ ] No Scryfall API URLs in source code

---

## 8. Implementation Checklist

### Phase 1: Setup
- [ ] Create `html_json/sos_pauper_decks.html`
- [ ] Copy base CSS from strixhaven-draft-guide.html
- [ ] Add deck-specific color classes

### Phase 2: Content Entry
- [ ] Build header section with title
- [ ] Create sticky navigation bar
- [ ] Add nav pills for each deck
- [ ] Insert all 6 deck sections with card grids

### Phase 3: Image Integration
- [ ] Map each card to correct local image path
- [ ] Handle split cards with `//` naming
- [ ] Verify all images exist locally

### Phase 4: Testing
- [ ] Open in browser, verify layout
- [ ] Test responsive behavior on mobile view
- [ ] Check print preview
- [ ] Validate no external requests made

---

## 9. Dependencies

| Dependency | Purpose |
|------------|---------|
| strixhaven-draft-guide.html | CSS/theme reference |
| sos_pauper_decks.md | Deck list source data |
| images/cards/SOS/*.jpg | Card image assets |

---

## 10. Notes & Constraints

- **No Scryfall API**: User explicitly requested local-only images
- **Card naming**: Must match existing slugify convention in project
- **Single page**: All content on one HTML file, no routing
- **Static only**: No dynamic content or JavaScript logic required

---

*Document Version: 1.0*
*Created: April 21, 2026*
*Status: Ready for Implementation*
