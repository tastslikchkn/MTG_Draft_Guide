# Implementation Roadmap: MTG_Draft_Guide (Phase 2 - Refinement & Feature Expansion)
## Version: 1.3
## Date: April 24, 2026

---

## 🎯 Objective
Transition the project from "Functional MVP" to "Optimized Professional Tool" by addressing technical debt, standardizing codebase architecture, and adding key UX features.

---

## 🛠️ Task 1: Codebase Standardization (Technical Debt)

| ID | Requirement | Status | Description |
|----|-------------|--------|-------------|
| TD-1.1 | Standardize Type Hints | 🔴 TODO | Replace mixed `Optional[T]` and `T | None` with a single convention (e.g., `T | None`) across all `utils/` modules for modern Pythonic consistency. |
| TD-1.2 | Remove Hard-coded Paths | 🔴 TODO | In `card_data.py`, replace the hard-coded `'images/cards/'` string with a configurable path or relative lookup to support different project structures. |

---

## ✨ Task 2: Feature Expansion (UX & Performance)

### FR-6: Card Search & Filtering
| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-6.1 | Text Input Field | Must Have | Add a search bar in the HTML header for quick card lookup. |
| FR-6.2 | Real-time Filtering | Should Have | Use JavaScript to filter visible `.card-item` elements based on name matching as the user types. |

### FR-7: Performance Optimization
| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-7.1 | Lighthouse Audit | Must Have | Run an automated audit to ensure mobile load times and scores meet targets. |

### FR-9: Print Verification
| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-9.1 | PDF Export Test | Must Have | Verify that the `@media print` CSS prevents card splitting across pages in a standard PDF output. |

---

## 📊 Success Metrics (Phase 2)
- [ ] All `utils/` files pass a linting check for consistent type hints.
- [ ] Search functionality allows finding a "Bomb" or "Trap" in < 2 seconds of typing.
- [ ] Mobile Lighthouse score > 85.
- [ ] Print preview shows no broken card images/text across page boundaries.

---
*Document Owner: Dan Getty*
*Status: Active Development Phase*
