# Product Requirements Document: Strixhaven Draft Guide

## Overview
**Product:** Interactive HTML draft guide for Magic: The Gathering - Secrets of Strixhaven  
**Platform:** Responsive web page (mobile-first, print-friendly)  
**User:** Dan - MTG player preparing for weekend draft events  
**Goal:** Reliable, beautiful reference guide that works perfectly on phone during draft and prints cleanly

---

## Core Requirements

### 1. Mobile-First Design
- **Touch-friendly**: All interactive elements minimum 44px tap targets
- **Responsive layouts**: Cards scale appropriately from 320px to desktop widths
- **Navigation**: Sticky nav pills accessible at all scroll positions on mobile
- **Horizontal scrolling**: Bombs section must work smoothly with thumb on small screens
- **Font sizes**: Minimum 16px body text, scalable headings

### 2. Print-Friendly Output
- **Print stylesheet**: Clean black/white optimized layout
- **Page breaks**: Prevent cards from splitting across pages
- **Remove interactive elements**: Hide nav pills, reduce shadows on print
- **Card images**: Scale appropriately for letter/A4 paper
- **Background colors**: Convert to grayscale-friendly or remove heavy backgrounds

### 3. Image Reliability (CRITICAL)
**Requirement: Every single card image MUST display - no exceptions.**

Multi-tier fallback strategy:
1. **Scryfall API** (primary) - `&format=normal` for bordered cards
2. **Scryfall borderless** - `&format=border-cropped`
3. **Cardmarket API** - proxy through their image service
4. **Local cached images** - Download and serve from `/images/` folder as last resort
5. **Placeholder with card name** - Styled fallback if all sources fail

Image features:
- Lazy loading for performance (`loading="lazy"`)
- Preload critical above-fold images
- Fallback to text-only display with color badge if image fails completely
- Console logging of failed images for debugging

### 4. Content Sections (Existing + Improvements)
| Section | Purpose | Mobile Priority |
|---------|---------|----------------|
| 📚 Draft Tips | Quick strategy reminders | High - visible on load |
| ⚠️ Trap Commons | Cards to avoid early | Medium |
| 💣 Bomb Rares/Mythics | Best-in-slot cards by color | High |
| ⭐ Top Commons | Strong common/uncommon picks | High |
| 🎯 Archetypes | Color pair strategies + combos | Medium |

### 5. Performance Targets
- **Mobile load time**: < 3 seconds on 4G
- **First contentful paint**: < 1 second
- **Image optimization**: Max 200KB per card image, lazy loaded
- **Total page weight**: Under 5MB (with all images)

---

## Technical Specifications

### Browser Support
- Chrome/Edge/Safari on iOS and Android (primary)
- Desktop browsers for print preview
- No IE support required

### Responsive Breakpoints
```css
Mobile:    320px - 767px  (phone portrait/landscape)
Tablet:    768px - 1023px
Desktop:   1024px+       (and print)
```

### Print Specifications
- Paper size: Letter (US) / A4
- Margins: 0.5 inch minimum
- Orientation: Portrait preferred, Landscape optional
- Color mode: Grayscale compatible

---

## Success Criteria

**Must Have (MVP):**
- [ ] All card images display reliably on mobile
- [ ] Page readable at 100% zoom on iPhone SE (375px width)
- [ ] Print preview shows clean layout without cut-off content
- [ ] Navigation works with thumb reach on large phones
- [ ] Load time under 5 seconds on mobile 4G

**Nice to Have:**
- [ ] Offline capability (service worker caching)
- [ ] Search/filter cards by name
- [ ] Toggle between compact/detailed views
- [ ] Shareable deep links to specific archetypes

---

## Constraints & Notes
- Single HTML file preferred (no build step complexity)
- No external dependencies beyond Scryfall/Cardmarket APIs
- Must work without JavaScript for basic viewing (progressive enhancement)
- Budget: $0 - use free tiers only

---

*Last Updated: April 14, 2026*
*Version: 1.0*
