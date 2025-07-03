# Quick Start Guide - Job Application Agent

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Check System Compatibility
```bash
python main.py --diagnose
```

**If you see browser errors, run the auto-fix:**
```bash
python troubleshoot.py
```

### Step 3: Configure Credentials
```bash
cp .env.example .env
# Edit .env with your login details
```

### Step 4: Update Your Profile
Edit `config/profile_config.py` with your details from the resume.

### Step 5: Test Run
```bash
python main.py --run-once
```

### Step 6: Start Automatic Mode
```bash
python main.py --start
```

---

## 🛠️ Platform-Specific Quick Fixes

### Mac (M1/M2) Issues
```bash
# If you get "Exec format error"
python troubleshoot.py

# Alternative manual fix
rm -rf ~/.wdm ~/.chrome_drivers
brew install chromedriver
```

### Windows Issues
```bash
# If you get "not a valid Win32 application"
python troubleshoot.py

# Run as Administrator if needed
```

### Linux Issues
```bash
# Install Chrome and ChromeDriver
sudo apt-get install google-chrome-stable chromium-chromedriver
python troubleshoot.py
```

---

## 🎯 What This Agent Does

1. **Every Hour**: Searches Naukri.com and LinkedIn for new jobs
2. **Smart Filtering**: Only applies to jobs matching your skills/experience
3. **Automatic Applications**: Fills forms and submits applications
4. **Rate Limited**: Respects platform limits (10/hour, 50/day)
5. **Tracks Progress**: Prevents duplicate applications

---

## 📊 Monitor Your Progress

```bash
# Check status anytime
python main.py --status

# View logs
tail -f logs/applications.log
```

---

## 🆘 Need Help?

1. **Browser Issues**: `python troubleshoot.py`
2. **Full Diagnostics**: `python main.py --diagnose`
3. **Configuration Check**: `python main.py --config`

---

## 🎛️ Key Settings

Edit `config/profile_config.py`:
- `target_roles`: Job titles to search for
- `preferred_locations`: Cities/regions
- `skills`: Your technical skills
- `max_applications_per_hour`: Rate limiting

---

**You're all set! The agent will now automatically find and apply to relevant Python developer positions.** 🎉