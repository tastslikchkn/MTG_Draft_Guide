# 📋 Test Checklist - Quick Reference

## 🎯 Files Created

| File | Purpose | Size |
|------|---------|------|
| `test_checklist.md` | Human-readable markdown checklist | 16 KB |
| `test_checklist.csv` | Generic CSV for any spreadsheet app | 15 KB |
| `test_checklist_google_sheets.csv` | Optimized for Google Sheets import | 15 KB |
| `test_checklist_template.html` | Pre-formatted HTML (copy-paste to Sheets) | 32 KB |
| `test_checklist_setup_guide.md` | Step-by-step setup instructions | 7 KB |

---

## 🚀 Quick Start Options

### Option A: Google Sheets Import (Recommended)
```
1. Open https://sheets.new
2. File → Import → Upload test_checklist_google_sheets.csv
3. Click "Create new spreadsheet"
4. Data → Create a filter
5. Done!
```

### Option B: HTML Copy-Paste (Best Formatting)
```
1. Open test_checklist_template.html in browser
2. Select all (Ctrl+A) and copy (Ctrl+C)
3. Paste into new Google Sheet at cell A1
4. Apply filters via Data → Create a filter
5. Done!
```

### Option C: Markdown Viewer
```
Open test_checklist.md in:
- VS Code, Obsidian, or any markdown editor
- GitHub/GitLab issues (copy-paste)
- Convert to PDF for offline testing
```

---

## 📊 Test Summary

```
Total Tests: 115
├── User Stories (US):        27 tests
├── Functional Req (FR):      68 tests
├── Edge Cases (TC-5):         6 tests
├── Browser Compatibility:     4 tests
├── Security NFRs:             3 tests
├── Reliability NFRs:          2 tests
├── Maintainability NFRs:      3 tests
└── Performance Tests:         4 tests
```

### By Priority:
- 🔴 **P0 (Critical)**: ~45 tests — Must pass before release
- 🟠 **P1 (High)**: ~40 tests — Important features
- 🔵 **P2 (Medium)**: ~25 tests — Nice to have
- ⚪ **P3 (Low)**: ~5 tests — Future enhancements

---

## 🎨 Google Sheets Setup Checklist

After importing, apply these settings:

### Essential (Do First):
- [ ] **Add Filter Row**: Data → Create a filter
- [ ] **Freeze Header**: View → Freeze → 1 row
- [ ] **Adjust Column Widths**: Drag column borders to fit content

### Recommended:
- [ ] **Conditional Formatting for Status**:
  - Pass = Green background (#C6EFCE)
  - Fail = Red background (#FFC7CC)
  - Blocked = Orange background (#FFEB9C)
- [ ] **Data Validation Dropdowns**:
  - Status column: Pending, Pass, Fail, Blocked, Skipped
  - Priority column: P0, P1, P2, P3

### Optional (Dashboard):
- [ ] Create new sheet named "Dashboard"
- [ ] Add summary formulas (see setup guide)
- [ ] Create charts for pass rate by category

---

## 📝 Status Values Reference

| Value | Emoji | Meaning |
|-------|-------|---------|
| Pending | ⬜ | Not yet tested |
| Pass | ✅ | Test succeeded as expected |
| Fail | ❌ | Test did not meet expectations |
| Blocked | 🚧 | Cannot test due to dependency |
| Skipped | ⏭️ | Intentionally not tested |

---

## 🔍 Useful Filter Combinations

### View Critical Unpassed Tests:
```
Filter Priority → Select "P0"
Filter Status → Uncheck "Pass"
```

### View All Failed Tests:
```
Filter Status → Check only "Fail"
```

### View Tests by Category:
```
Filter Category → Select specific category
```

---

## 📱 Mobile Testing Tips

1. **Download Google Sheets app** (iOS/Android)
2. Open the spreadsheet on mobile
3. Use filter buttons to sort by priority
4. Tap status cells to update during testing
5. Add comments for failure details

---

## 💾 Backup & Export Options

### From Google Sheets:
- **PDF**: File → Download → PDF Document (.pdf)
- **Excel**: File → Download → Microsoft Excel (.xlsx)
- **CSV**: File → Download → Comma-separated values (.csv)

### Sharing:
```
Click "Share" button → Add email addresses → Set permission level
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Filters not working | Ensure data starts at row 1 with headers |
| Conditional formatting not applying | Check exact text match (case-sensitive) |
| Formulas showing #REF! | Verify sheet name matches exactly |
| Import fails | Try saving CSV as UTF-8 encoded |

---

## 📞 Next Steps After Setup

1. ✅ **Share** with team members who will test
2. ✅ **Sort by Priority** (P0 first)
3. ✅ **Begin systematic testing** top-to-bottom
4. ✅ **Update Status** as you go
5. ✅ **Add comments** for failures with screenshots
6. ✅ **Review Dashboard** after each session

---

## 📂 File Locations

```
~/repos/MTG_Draft_Guide/
├── test_checklist.md                    # Markdown version
├── test_checklist.csv                   # Generic CSV
├── test_checklist_google_sheets.csv     # Google Sheets optimized
├── test_checklist_template.html         # HTML copy-paste template
└── test_checklist_setup_guide.md        # Detailed setup instructions
```

---

## 🎯 Testing Workflow Recommendation

```
1. Sort by Priority (P0 first)
2. Within each priority, sort by Category
3. Test systematically top-to-bottom
4. Update Status as you go
5. Add notes in comments for failures
6. Review Dashboard after each session
```

---

**Template Version:** 1.0  
**Compatible with:** Google Sheets, Microsoft Excel 365, LibreOffice Calc
