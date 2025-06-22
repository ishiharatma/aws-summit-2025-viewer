# AWS Summit Japan 2025 Mini-Stage Schedule Viewer

[![🇯🇵 日本語](https://img.shields.io/badge/%F0%9F%87%AF%F0%9F%87%B5-日本語-white)](./README.ja.md) [![🇺🇸 English](https://img.shields.io/badge/%F0%9F%87%BA%F0%9F%87%B8-English-white)](./README.md)

A schedule viewer with Google Calendar-like UI for mini-stage sessions at AWS Summit Japan 2025.

🌐 **[Open Schedule Viewer](https://ishiharatma.github.io/aws-summit-2025-viewer/)**

## ✨ Features

- **Google Calendar-like UI**: Intuitive and easy-to-view calendar format for sessions
- **Three Stage Support**: Display all sessions from AWS Village Stage, Developers on Live, and Community Stage
- **Date Switching**: Switch between Day 1 (6/25) and Day 2 (6/26)
- **Session Detail Display**: Click on sessions to view detailed information in a pop-up
- **Google Calendar Integration**: Directly add sessions to Google Calendar from the detail view
- **Responsive Design**: Compatible with PC, tablet, and smartphone

## 📊 Target Sessions

### AWS Village Stage
- Day 1: 21 sessions (11:30-18:25)
- Day 2: 16 sessions (11:30-16:45)

### Developers on Live  
- Day 1: 13 sessions (11:35-18:25)
- Day 2: 8 sessions (11:35-16:55)

### Community Stage
- Day 1: 12 sessions (11:30-17:25)
- Day 2: 10 sessions (11:30-16:25)

**Total Sessions: 80 sessions**

## 🚀 How to Use

1. **Select Date**: Switch between Day 1/Day 2 using the buttons at the top
2. **Check Sessions**: View session times and titles in the calendar
3. **View Details**: Click on a session to display detailed information
4. **Add to Calendar**: Add to your schedule with the "Add to Google Calendar" button in the details view

## 🔧 Technical Specifications

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Format**: JSON
- **Responsive Design**: Using CSS Grid Layout
- **Browser Support**: All modern browsers

## 📚 Data Source

Session information is retrieved from the [AWS Summit Japan 2025 official website](https://pages.awscloud.com/summit-japan-2025-aws-expo-booth.html#ministage).

## 📄 License

This project is released under the [MIT License](./LICENSE).

## 🛠️ Development Environment

Use the template repository below to start with a pre-configured environment with Amazon Q CLI installed and ready to use:

https://github.com/ishiharatma/devcontainer-amazon-q-cli

## 📋 Development Rules & Guidelines

### **🚨 MANDATORY: Pre-Commit Checklist**

**CRITICAL**: Before any commit or push, verify these settings in `docs/js/script.js`:

```javascript
// ✅ MUST BE FALSE for production
const DEBUG_MODE = false;           // ❌ Never commit with true
const TEST_ACTIVE_SESSION = false;  // ❌ Never commit with true
```

#### **Pre-Commit Verification Steps**
1. **[ ] DEBUG_MODE = false** - Disable debug console logging
2. **[ ] TEST_ACTIVE_SESSION = false** - Disable test active session display
3. **[ ] Test both designs** - Verify modern and 1990s versions work
4. **[ ] Mobile responsive** - Check on mobile devices
5. **[ ] No console errors** - Verify clean browser console

### **⚠️ Why These Rules Matter**

#### **TEST_ACTIVE_SESSION = false**
- **Production Impact**: If `true`, random sessions show as "active" 
- **User Confusion**: Misleading active session indicators
- **Data Integrity**: Only real-time sessions should be highlighted

#### **DEBUG_MODE = false**
- **Performance**: Reduces console logging overhead
- **User Experience**: Clean browser console for end users
- **Security**: Prevents debug information exposure

### **🧪 Development Testing**

#### **To Test Active Sessions During Development:**

1. **Temporarily enable test mode**:
   ```javascript
   const TEST_ACTIVE_SESSION = true;  // Only for testing
   ```

2. **Target sessions**: `13:00 - 13:20` will show as active

3. **Visual verification**:
   - **Modern**: Green gradient + pulse animation
   - **1990s**: Green→yellow flash + red border

4. **⚠️ REMEMBER**: Set back to `false` before commit!

### **🔍 Quick Verification Command**

Before committing, run this check:
```bash
grep -n "TEST_ACTIVE_SESSION.*true\|DEBUG_MODE.*true" docs/js/script.js
```
**Expected result**: No output (both should be `false`)

---

**AWS Summit Japan 2025**  
Dates: June 25 (Wed) - June 26 (Thu), 2025  
Venue: Makuhari Messe
