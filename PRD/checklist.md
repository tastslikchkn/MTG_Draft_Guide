# Implementation Checklist

## 📊 Status Summary (April 21, 2026)

| Phase | Progress | Notes |
|-------|----------|-------|
| **Phase 1: Foundation** | ✅ 100% | API fixes, requirements.txt, .env.example complete |
| **Phase 2: Image Cache** | ✅ 100% | 92/92 cards cached (35MB) |
| **Phase 3: Mobile Nav** | ✅ Already done | Sticky nav implemented in HTML |
| **Phase 4: Print CSS** | ✅ Already done | Full print stylesheet present |

### Remaining Quick Wins:
- [ ] Add `loading="lazy"` to images (~5 min) — ✅ DONE
- [ ] Reduce hover scale 2.0x → 1.1x (~5 min) — ✅ Already done
- [ ] Use local image cache (FR-8, ~15 min)
- [ ] Meta description tag (FR-9.1, ~30 sec)
- [ ] Back-to-top button (FR-9.2, ~15 min)

---

## Phase 1: Image Reliability (CRITICAL) 🔴

### 1.1 Enhanced Fallback System
- [ ] **Research Cardmarket API format** - Test exact URL structure for card images
- [ ] **Add CMC (Card Market) fallback** - Third tier after Scryfall variants
- [x] **Create local image cache directory** - `/images/cards/` for offline backup
- [x] **Write Python script to download all card images** - Pre-cache every card in guide
  - [x] Extract unique card names from HTML
  - [x] Download from Scryfall (normal format)
  - [x] Save as PNG with consistent naming
  - [x] Handle rate limiting (1 req/sec)
- [ ] **Update JavaScript fallback chain** to include local files:
  ```
  Scryfall → Borderless → Cardmarket → Local /images/ → Styled placeholder
  ```
- [ ] **Test each fallback tier** - Verify chain works when each level fails

### 1.2 Image Optimization
- [ ] Add `loading="lazy"` to all card images (except above-fold)
- [ ] Add `width` and `height` attributes to prevent layout shift
- [ ] Preload critical bomb images in `<head>`
- [ ] Compress downloaded images to <100KB each

---

## Phase 2: Mobile-First Improvements 📱

### 2.1 Responsive Layout Fixes
- [ ] **Reduce card hover scale** - Change from `scale(2.0)` to `scale(1.1)` max
- [ ] **Fix bombs horizontal scroll** - Add `-webkit-overflow-scrolling: touch`
- [ ] **Increase minimum card width** on mobile from 160px to fit screen
- [ ] **Add sticky navigation** - Nav pills fixed at top on scroll (mobile only)
- [ ] **Touch target sizes** - Ensure all clickable elements ≥44px height

### 2.2 Mobile CSS Additions
```css
[ ] Add @media queries for:
    - Font size adjustments (16px min body)
    - Card grid: 2 columns on mobile, 4+ on desktop
    - Bombs section: vertical stack on small screens option
    - Navigation: hamburger menu or scrollable pill bar
```

### 2.3 Mobile Testing
- [ ] Test on iPhone SE simulator (375px width)
- [ ] Test on iPhone 14 Pro Max (430px width)
- [ ] Verify thumb reachability for all sections
- [ ] Check text readability at 100% zoom

---

## Phase 3: Print-Friendly Design 🖨️

### 3.1 Print Stylesheet
```css
[ ] Add @media print section:
    - Remove background gradients (save ink)
    - Convert colors to black/white/gray
    - Hide navigation pills
    - Remove box shadows and decorative elements
    - Set font-family to Times New Roman or similar
    - Ensure card images scale to fit page
```

### 3.2 Print Layout Fixes
- [ ] **Page break control** - `break-inside: avoid` on card items
- [ ] **Section breaks** - Add `page-break-before: always` for major sections
- [ ] **Header on each page** - Small title/header repeats on printed pages
- [ ] **Remove horizontal scroll** - Stack bombs vertically for print
- [ ] **Condense whitespace** - Reduce margins/padding for density

### 3.3 Print Testing
- [ ] Chrome Print Preview → Save as PDF
- [ ] Verify no cards cut off at page edges
- [ ] Check readability in grayscale
- [ ] Count pages (target: under 5 pages)

---

## Phase 4: Performance Optimization ⚡

### 4.1 Image Performance
- [ ] Convert images to WebP format with fallback
- [ ] Implement responsive images (`srcset`) for different densities
- [ ] Add image compression for local cached versions
- [ ] Consider SVG placeholders while images load

### 4.2 Code Optimization
- [ ] Minify CSS (remove comments, whitespace)
- [ ] Move non-critical JS to end of `<body>`
- [ ] Defer archetype section loading (below fold)
- [ ] Add meta viewport tag properly configured

### 4.3 Metrics
- [ ] Run Lighthouse audit (mobile)
- [ ] Target: Performance score > 80
- [ ] Target: First Contentful Paint < 1.5s

---

## Phase 5: Accessibility & Polish ♿

### 5.1 Accessibility
- [ ] Add ARIA labels to navigation pills
- [ ] Ensure color isn't only indicator (add text icons)
- [ ] Add `alt` text with card names to all images
- [ ] Test keyboard navigation (Tab through cards)
- [ ] Add skip-to-content link for screen readers

### 5.2 SEO Meta Tags
```html
[ ] Add to <head>:
    - <meta name="description" content="...">
    - <meta name="viewport" content="width=device-width, initial-scale=1.0">
    - Open Graph tags for sharing
```

### 5.3 Bug Fixes
- [ ] Fix recursive `onerror` handler bug (line 678)
- [ ] Remove `!important` overrides with better selectors
- [ ] Add error boundary for image loading failures

---

## Phase 6: Testing & Validation ✅

### 6.1 Image Verification
- [ ] **Count total unique cards** in guide
- [ ] **Verify every card** has at least one working image source
- [ ] Document any cards that fail all fallbacks
- [ ] Manually download missing card images as last resort

### 6.2 Cross-Platform Testing
| Platform | Status | Notes |
|----------|--------|-------|
| iPhone Safari | [ ] | Primary mobile target |
| Android Chrome | [ ] | Secondary mobile |
| Desktop Chrome | [ ] | Print preview |
| Desktop Firefox | [ ] | Compatibility |

### 6.3 Real-World Testing
- [ ] Open guide on phone at coffee shop (4G)
- [ ] Try printing to PDF from desktop
- [ ] Share link and have friend test on different device

---

## Quick Wins (Do First) 🚀

1. **[30 min]** Add `loading="lazy"` to all images — [ ] TODO
2. **[1 hour]** Run Python script to download/cache all card images locally — ✅ DONE (92 cards, 35MB)
3. **[30 min]** Add print stylesheet with basic fixes — ✅ Already implemented
4. **[1 hour]** Fix mobile navigation (sticky header) — ✅ Already implemented
5. **[30 min]** Reduce hover scale from 2.0x to 1.1x — [ ] TODO

---

## Card Inventory (For Image Caching)

**Total unique cards to cache:** ~80 cards

Breakdown:
- Trap Commons: 4 cards
- Bomb Rares/Mythics: ~12 cards
- Top Commons by Color: ~35 cards
- Archetype Cards: ~60 cards (some overlap)

**Unique card list extraction needed** - Write script to parse HTML and dedupe.

---

*Created: April 14, 2026*
*Last Updated: April 21, 2026 — PRD v1.2: Added FR-8 (local image cache) and FR-9 (UX polish). Lazy loading + hover scale complete.*
*Estimated Total Time: 6-8 hours*
