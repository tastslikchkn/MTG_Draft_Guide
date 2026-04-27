# Google Sheets Test Checklist Setup Guide

## 🎯 Quick Start (5 Minutes)

### Option A: Import Existing CSV

1. **Open [Google Sheets](https://sheets.new)**
2. Click **File → Import**
3. Upload `test_checklist_google_sheets.csv`
4. Select "Create new spreadsheet"
5. Name it: **"Card Browser Test Checklist"**
6. Apply formatting (see below)

---

### Option B: Copy Template Directly

1. Open [Google Sheets](https://sheets.new)
2. Copy the table from `test_checklist_template.html`
3. Paste into cell A1
4. Format as needed

---

## 📋 Step-by-Step Setup Instructions

### 1️⃣ Add Filter Row (Essential)

```
Click any cell in row 1 → Data → Create a filter
```

This adds dropdown arrows to each column header for sorting/filtering.

---

### 2️⃣ Apply Conditional Formatting (Visual Status Indicators)

#### For Status Column (Column E):

```
Select column E → Format → Conditional formatting
```

| Rule | Format | Color |
|------|--------|-------|
| Text is exactly `Pass` | Green background | 🟢 #C6EFCE |
| Text is exactly `Fail` | Red background | 🔴 #FFC7CC |
| Text is exactly `Blocked` | Orange background | 🟠 #FFEB9C |
| Text is exactly `Skipped` | Gray background | ⚪ #F2F2F2 |

#### For Priority Column (Column F):

```
Select column F → Format → Conditional formatting
```

| Rule | Format | Color |
|------|--------|-------|
| Text is exactly `P0` | Red text, bold | 🔴 Critical |
| Text is exactly `P1` | Orange text | 🟠 High |
| Text is exactly `P2` | Blue text | 🔵 Medium |
| Text is exactly `P3` | Gray text | ⚪ Low |

---

### 3️⃣ Add Data Validation (Dropdown Menus)

#### For Status Column:

```
Select column E → Data → Data validation
```

**Criteria:** List of items  
**Values:** `Pending,Pass,Fail,Blocked,Skipped`  
**Show:** Dropdown in cell

#### For Priority Column:

```
Select column F → Data → Data validation
```

**Criteria:** List of items  
**Values:** `P0,P1,P2,P3`  
**Show:** Dropdown in cell

---

### 4️⃣ Freeze Header Row

```
View → Freeze → 1 row
```

This keeps headers visible while scrolling.

---

### 5️⃣ Adjust Column Widths

| Column | Suggested Width |
|--------|------------------|
| A (Category) | 200 px |
| B (Test ID) | 100 px |
| C (Test Case) | 300 px |
| D (Expected Result) | 350 px |
| E (Status) | 80 px |
| F (Priority) | 60 px |

---

### 6️⃣ Add Summary Dashboard (Optional)

In a new sheet called "Dashboard", add these formulas:

```excel
// Total Tests
=COUNTA(Sheet1!B:B)-1

// Passed Tests
=COUNTIF(Sheet1!E:E,"Pass")

// Failed Tests  
=COUNTIF(Sheet1!E:E,"Fail")

// Pending Tests
=COUNTIF(Sheet1!E:E,"Pending")

// Completion Percentage
=COUNTIF(Sheet1!E:E,"Pass")/(COUNTA(Sheet1!B:B)-1)*100

// P0 Tests Remaining
=COUNTIFS(Sheet1!F:F,"P0",Sheet1!E:E,"<>","Pass")
```

---

## 🎨 Recommended Visual Setup

### Color Scheme for Status:

| Status | Background | Text |
|--------|------------|------|
| Pass | Light Green (#C6EFCE) | Dark Green (#006100) |
| Fail | Light Red (#FFC7CC) | Dark Red (#9C0006) |
| Blocked | Light Orange (#FFEB9C) | Dark Orange (#9C6500) |
| Skipped | Light Gray (#F2F2F2) | Dark Gray (#666666) |
| Pending | White | Black |

### Priority Badge Colors:

| Priority | Color | Meaning |
|----------|-------|---------|
| P0 | 🔴 Red | Critical - Blocker |
| P1 | 🟠 Orange | High - Must have |
| P2 | 🔵 Blue | Medium - Should have |
| P3 | ⚪ Gray | Low - Nice to have |

---

## 📊 Dashboard Formulas Reference

### Copy These Into Your "Dashboard" Sheet:

```excel
// Cell A1: DASHBOARD HEADER
// Cell A2:A9: Metrics

A2: Total Tests
B2: =COUNTA('Test Checklist'!B:B)-1

A3: Passed ✅
B3: =COUNTIF('Test Checklist'!E:E,"Pass")

A4: Failed ❌
B4: =COUNTIF('Test Checklist'!E:E,"Fail")

A5: Blocked 🚧
B5: =COUNTIF('Test Checklist'!E:E,"Blocked")

A6: Pending ⏳
B6: =COUNTIF('Test Checklist'!E:E,"Pending")

A7: Completion Rate
B7: =(B3/B2)*100 & "%"

A8: Pass Rate  
B8: =(B3/(B3+B4))*100 & "%"
```

### Priority Breakdown:

```excel
// Cell D1:D5: BY PRIORITY

D1: By Priority
E1: Remaining

D2: P0 (Critical)
E2: =COUNTIFS('Test Checklist'!F:F,"P0", 'Test Checklist'!E:E,"<>","Pass")

D3: P1 (High)
E3: =COUNTIFS('Test Checklist'!F:F,"P1", 'Test Checklist'!E:E,"<>","Pass")

D4: P2 (Medium)
E4: =COUNTIFS('Test Checklist'!F:F,"P2", 'Test Checklist'!E:E,"<>","Pass")

D5: P3 (Low)
E5: =COUNTIFS('Test Checklist'!F:F,"P3", 'Test Checklist'!E:E,"<>","Pass")
```

---

## 🔍 Useful Filter Combinations

### View Only Failed Tests:
```
Filter Status column → Uncheck all → Check "Fail" only
```

### View P0 Tests Not Yet Passed:
```
Filter Priority → Select "P0"
Filter Status → Uncheck "Pass"
```

### View Tests by Category:
```
Filter Category → Select specific category (e.g., "US-1: Search...")
```

---

## 📱 Mobile Access

Once set up, access on mobile:

1. Install **Google Sheets app** (iOS/Android)
2. Open the spreadsheet
3. Use filter buttons to sort by priority/status
4. Tap cells to update status during testing

---

## 💾 Backup & Sharing

### Share with Team:
```
Click "Share" button → Add email addresses → Set permission level
```

### Export Options:
- **PDF:** File → Download → PDF Document (.pdf)
- **Excel:** File → Download → Microsoft Excel (.xlsx)
- **CSV:** File → Download → Comma-separated values (.csv)

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

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|
| Filters not working | Ensure data starts at row 1 with headers |
| Conditional formatting not applying | Check exact text match (case-sensitive) |
| Formulas showing #REF! | Verify sheet name matches exactly |
| Import fails | Try saving CSV as UTF-8 encoded |

---

## 🚀 Next Steps After Setup

1. ✅ **Share** with team members who will test
2. ✅ **Create comments column** for failure notes (optional)
3. ✅ **Set up notifications** for status changes (Google Sheets feature)
4. ✅ **Link to PRD** in sheet description
5. ✅ **Schedule testing sessions** based on priority groups

---

## 📞 Need Help?

If you encounter issues during setup:
- Check that all formulas reference the correct sheet name
- Ensure no extra blank rows at top of data
- Verify CSV encoding is UTF-8
- Try re-importing if formatting seems broken

---

**Template Version:** 1.0  
**Compatible with:** Google Sheets, Microsoft Excel 365, LibreOffice Calc
