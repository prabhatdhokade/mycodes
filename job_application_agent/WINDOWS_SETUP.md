# 🪟 Windows Setup Guide - Optimized Job Hunter

**Quick setup guide for Windows users to avoid Unicode issues and get started fast**

## ⚡ Quick Start (5 Minutes)

### 1. **Run Windows Launcher** (Recommended)
```batch
# Navigate to job_application_agent folder
cd job_application_agent

# Run Windows launcher
run_windows.bat
```

### 2. **Or Use Windows-Compatible Script**
```powershell
# Run optimized version with Windows support
python optimized_main_windows.py --hunt-once
```

## 🔧 If You See Unicode Errors

If you get errors like `UnicodeEncodeError: 'charmap' codec can't encode character`, follow these steps:

### **Option 1: Use Windows Scripts (Easiest)**
```batch
# Just double-click or run:
run_windows.bat
```

### **Option 2: Fix Console Encoding**
```powershell
# Set console to UTF-8
chcp 65001

# Then run the Windows version
python optimized_main_windows.py --profile
```

### **Option 3: Use PowerShell**
```powershell
# PowerShell handles Unicode better
powershell
python optimized_main_windows.py --test-forms
```

## 🎯 Smart Commands for Windows

```batch
# Windows-compatible commands (no Unicode errors)
python optimized_main_windows.py --hunt              # Start hunting
python optimized_main_windows.py --hunt-once         # Single session
python optimized_main_windows.py --status            # Check status
python optimized_main_windows.py --profile           # Show profile
python optimized_main_windows.py --test-forms        # Test answers
python optimized_main_windows.py --diagnose          # Diagnostics

# Platform-specific hunting
python optimized_main_windows.py --hunt-once --platform naukri
python optimized_main_windows.py --hunt-once --platform linkedin
```

## 📊 What You'll See (Windows-Compatible Output)

### **Profile Display:**
```
======================================================================
[TARGET] OPTIMIZED JOB HUNTER - PROFILE ACTIVE
======================================================================
[USER] Hunter: Prabhat Dhokade
[EMAIL] Contact: prabhatdhokade@gmail.com
[TARGET] Experience: 2.5 years
[SALARY] Current CTC: 7.0 LPA
[SALARY] Expected CTC: 15.0 LPA
[DATE] Available from: End of July 2024

[TARGET] Target Roles:
   • Python Developer
   • Software Engineer
   • Backend Developer
   • Software Developer

[LOCATION] Hunting Zones:
   • Pune
   • Mumbai
   • Bangalore
   • Hyderabad
   • Remote

[SKILLS] Core Skills:
   Python, C++, Flask, Streamlit, MySQL, PostgreSQL, AWS, EC2

[START] Intelligence Features:
   • Smart Form Handling: True
   • Dynamic Questions: True
   • Single Platform Focus: True
   • Human-like Behavior: True
   • Quality Over Quantity: True

[SAFETY] Safety Limits:
   • Max per hour: 12
   • Max per day: 40
======================================================================
```

### **Smart Form Test:**
```
======================================================================
[FORM] SMART FORM ANSWERS - TEST MODE
======================================================================
[FORM] Sample Questions and Automatic Answers:
   ? Years of Python experience?  ➜ 3.5
   ? Current CTC?                 ➜ 7
   ? Expected salary?             ➜ 15
   ? Notice period?               ➜ 1 Month
   ? Last working day?            ➜ End of July 2024
   ? Preferred location?          ➜ Pune
   ? Total experience?            ➜ 2.5
   ? Remote work?                 ➜ Yes
   ? Immediate joiner?            ➜ No
   ? Highest qualification?       ➜ Bachelor of Engineering

[CONFIG] Pattern Recognition: 64 predefined answers
[AI] Skill Experience: 14 technologies mapped
======================================================================
```

## 🚀 Windows Setup Steps

### **1. Install Dependencies**
```powershell
# Install required packages
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your credentials using notepad
notepad .env
```

### **2. Test Your Setup**
```batch
# Test Windows compatibility
python optimized_main_windows.py --diagnose

# Test smart form handling
python optimized_main_windows.py --test-forms

# Test profile display
python optimized_main_windows.py --profile
```

### **3. Configure Credentials**
Edit `.env` file:
```
NAUKRI_EMAIL=your_email@gmail.com
NAUKRI_PASSWORD=your_password
LINKEDIN_EMAIL=your_email@gmail.com
LINKEDIN_PASSWORD=your_password
RESUME_PATH=C:\path\to\your\resume.pdf
```

### **4. Start Job Hunting**
```batch
# Single hunt to test
python optimized_main_windows.py --hunt-once --platform naukri

# If successful, start automated hunting
python optimized_main_windows.py --hunt
```

## ❓ Common Windows Issues & Solutions

### **Issue 1: "Python not found"**
```batch
# Install Python 3.8+ from python.org
# Make sure to check "Add Python to PATH" during installation
```

### **Issue 2: "Module not found"**
```batch
# Install dependencies
pip install selenium beautifulsoup4 requests python-dotenv schedule
```

### **Issue 3: "ChromeDriver issues"**
```batch
# Run auto-fix
python optimized_main_windows.py --diagnose

# Or install manually
python troubleshoot.py
```

### **Issue 4: Still seeing Unicode errors**
```batch
# Use the launcher script instead
run_windows.bat

# Or set environment variable
set PYTHONIOENCODING=utf-8
python optimized_main_windows.py --profile
```

## 🎯 Windows-Specific Features

### **1. Automatic Encoding Fix**
- Sets console to UTF-8 automatically
- Replaces emojis with text equivalents
- Handles all Unicode characters gracefully

### **2. Safe Logging**
- All logs work properly on Windows
- File logs use UTF-8 encoding
- Console output is Windows-compatible

### **3. Batch Script Launcher**
- `run_windows.bat` - Easy menu-driven interface
- Automatic environment setup
- Error checking and helpful messages

## 📈 Expected Performance on Windows

### **What Works:**
- ✅ Smart form filling (all platforms)
- ✅ Dynamic question answering
- ✅ Platform rotation and optimization
- ✅ Rate limiting and safety features
- ✅ Complete logging and analytics
- ✅ Cross-browser compatibility

### **Windows Optimizations:**
- ✅ No Unicode encoding errors
- ✅ Proper console output formatting
- ✅ Windows-compatible file paths
- ✅ PowerShell and CMD support
- ✅ Batch script automation

## 🔒 Security Notes for Windows

### **Windows Defender:**
- Add exclusion for the job_application_agent folder
- This prevents false virus warnings for automation scripts

### **Firewall:**
- Allow Python through Windows Firewall
- Required for web scraping functionality

### **User Account Control (UAC):**
- Run PowerShell as regular user (not admin)
- Admin privileges not required

## 📞 Windows Support

### **Getting Help:**
1. **Run diagnostics:** `python optimized_main_windows.py --diagnose`
2. **Check logs:** Look in `logs/` folder
3. **Test forms:** `python optimized_main_windows.py --test-forms`
4. **Use launcher:** Double-click `run_windows.bat`

### **Common Solutions:**
- **Encoding issues:** Use `optimized_main_windows.py` instead of `optimized_main.py`
- **Console problems:** Use `run_windows.bat` launcher
- **Path issues:** Use full paths in `.env` file
- **Permission issues:** Run from user folder, not system folders

## 🎉 Windows Success Tips

### **1. Use the Right Script**
- ✅ `optimized_main_windows.py` - Windows-compatible
- ❌ `optimized_main.py` - May have Unicode issues

### **2. Use the Launcher**
- ✅ `run_windows.bat` - Easy menu interface
- ✅ Handles encoding automatically

### **3. Check Your Setup**
- ✅ Python 3.8+ installed
- ✅ Dependencies installed
- ✅ `.env` file configured
- ✅ Resume path is correct

### **4. Start Small**
```batch
# Test first
python optimized_main_windows.py --test-forms

# Then try single hunt
python optimized_main_windows.py --hunt-once --platform naukri

# Finally start automated hunting
python optimized_main_windows.py --hunt
```

---

**🎯 Your Windows-compatible AI job hunter is ready!**

No more Unicode errors, just smooth job hunting automation that works perfectly on Windows.