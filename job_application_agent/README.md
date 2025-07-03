# Automated Job Application Agent

An intelligent Python-based system that automatically searches for job openings on platforms like Naukri.com and LinkedIn, filters them based on your profile, and applies to suitable positions.

## 🚀 Features

- **Multi-Platform Support**: Naukri.com, LinkedIn (more platforms can be added)
- **Intelligent Job Filtering**: AI-powered matching based on skills, experience, and preferences
- **Automated Applications**: Handles form filling and application submission
- **Smart Scheduling**: Runs at configurable intervals with rate limiting
- **Comprehensive Logging**: Tracks all activities, applications, and results
- **Database Storage**: SQLite database to track applied jobs and prevent duplicates
- **Rate Limiting**: Respects platform limits to avoid being blocked
- **Resume Management**: Uses your uploaded resume for applications

## 📋 Prerequisites

- Python 3.7 or higher
- Chrome/Chromium browser
- Valid accounts on job platforms (Naukri.com, LinkedIn)
- Your resume in PDF format

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   cd job_application_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your credentials:
   ```env
   # LinkedIn Credentials
   LINKEDIN_EMAIL=your_linkedin_email@gmail.com
   LINKEDIN_PASSWORD=your_linkedin_password

   # Naukri.com Credentials
   NAUKRI_EMAIL=your_naukri_email@gmail.com
   NAUKRI_PASSWORD=your_naukri_password

   # Resume File Path
   RESUME_FILE_PATH=/path/to/your/resume.pdf
   ```

4. **Configure your profile**
   
   Edit `config/profile_config.py` to match your details:
   - Update personal information (name, email, phone, location)
   - Modify target roles and preferred locations
   - Update skills list
   - Set salary expectations
   - Configure application limits

## 🎯 Usage

### Interactive Mode (Recommended for first-time users)
```bash
python main.py
```

### Command Line Options

#### Start the scheduler (runs continuously)
```bash
python main.py --start
```

#### Run a single session
```bash
python main.py --run-once
```

#### Run on specific platform only
```bash
python main.py --run-once --platform naukri
python main.py --run-once --platform linkedin
```

#### Check status
```bash
python main.py --status
```

#### Show configuration
```bash
python main.py --config
```

#### Stop the scheduler
```bash
python main.py --stop
```

## ⚙️ Configuration

### Profile Configuration (`config/profile_config.py`)

Update the following sections:

1. **Personal Information**
   ```python
   USER_PROFILE = {
       "name": "Your Name",
       "email": "your.email@gmail.com",
       "phone": "+91 1234567890",
       "location": "Your City, State",
       # ...
   }
   ```

2. **Job Preferences**
   ```python
   "target_roles": [
       "Python Developer", "Software Engineer", 
       "Backend Developer", "Full Stack Developer"
   ],
   "preferred_locations": [
       "Mumbai", "Bangalore", "Pune", "Remote"
   ],
   ```

3. **Skills**
   ```python
   "skills": [
       "Python", "Django", "Flask", "JavaScript", 
       "React", "AWS", "Docker", "Git"
   ],
   ```

### Application Settings

```python
APPLICATION_CONFIG = {
    "max_applications_per_hour": 10,
    "max_applications_per_day": 50,
    "check_interval_hours": 1,
    # ...
}
```

## 📊 Monitoring and Logs

### Log Files
- `logs/job_agent.log` - General application logs
- `logs/applications.log` - Specific application attempts
- `logs/errors.log` - Error logs

### Database
- `job_applications.db` - SQLite database with all job and application data

### View Statistics
```bash
python main.py --status
```

## 🔧 Advanced Configuration

### Browser Settings
```python
BROWSER_CONFIG = {
    "headless": False,  # Set to True for background operation
    "window_size": (1920, 1080),
    "implicit_wait": 10,
    # ...
}
```

### Platform-Specific Settings
```python
PLATFORM_CONFIG = {
    "naukri": {
        "rate_limit": 2,  # seconds between requests
    },
    "linkedin": {
        "rate_limit": 3,
    }
}
```

## 🛡️ Safety Features

1. **Rate Limiting**: Prevents overwhelming job platforms
2. **Duplicate Prevention**: Tracks applied jobs to avoid re-applying
3. **Human-like Delays**: Random delays between actions
4. **Error Handling**: Graceful error recovery
5. **Logging**: Comprehensive activity tracking

## ⚠️ Important Considerations

### Legal and Ethical
- **Terms of Service**: Ensure you comply with platform terms of service
- **Rate Limits**: Respect platform rate limits to avoid account suspension
- **Accuracy**: Review and customize the profile configuration carefully
- **Monitoring**: Regularly monitor the application logs

### Technical
- **Internet Connection**: Stable internet required for continuous operation
- **Browser Updates**: Chrome browser should be up to date
- **Account Security**: Use strong passwords and enable 2FA where possible
- **Resource Usage**: Monitor CPU and memory usage during operation

### Platform-Specific Notes

#### LinkedIn
- May require manual verification for new login locations
- Easy Apply works best for automated applications
- Premium accounts may have higher success rates

#### Naukri.com
- Resume should be updated and complete
- Profile completion affects job recommendations
- Regular profile updates improve visibility

## 📈 Optimization Tips

1. **Profile Optimization**
   - Keep your platform profiles updated
   - Use relevant keywords in your profile
   - Upload a well-formatted resume

2. **Application Strategy**
   - Start with lower application limits
   - Monitor success rates and adjust
   - Focus on quality over quantity

3. **Scheduling**
   - Run during business hours for better response
   - Avoid weekends if configured
   - Adjust intervals based on job market activity

## 🔍 Troubleshooting

### Quick Fix for Browser Issues
If you encounter ChromeDriver or browser initialization errors:

```bash
# Run the automatic troubleshooter
python troubleshoot.py

# Or run comprehensive diagnostics
python main.py --diagnose
```

### Platform-Specific Fixes

#### **Mac Users (especially M1/M2)**
```bash
# Clear caches and fix permissions
rm -rf ~/.wdm ~/.chrome_drivers
python troubleshoot.py

# Install ChromeDriver via Homebrew
brew install chromedriver

# For Apple Silicon, ensure ARM64 compatibility
arch -arm64 python main.py --run-once
```

#### **Windows Users**
```bash
# Run as Administrator
python troubleshoot.py

# Manually download ChromeDriver to C:\chromedriver\
# Add to Windows Defender exclusions
```

#### **Linux Users**
```bash
# Install Chrome and ChromeDriver
sudo apt-get update
sudo apt-get install google-chrome-stable chromium-chromedriver

# Fix permissions
sudo chmod +x /usr/bin/chromedriver
```

### Common Issues and Solutions

1. **Browser Initialization Errors**
   ```bash
   # Error: Exec format error (Mac) or %1 is not a valid Win32 application (Windows)
   python troubleshoot.py  # Automatic fix
   
   # Manual fix - clear all caches
   rm -rf ~/.wdm ~/.chrome_drivers  # Mac/Linux
   del %TEMP%\.wdm  # Windows
   ```

2. **ChromeDriver Version Mismatch**
   ```bash
   # Update Chrome browser first, then:
   python troubleshoot.py
   ```

3. **Permission Denied (Mac/Linux)**
   ```bash
   chmod +x ~/.chrome_drivers/*/chromedriver
   # Or run troubleshoot.py to fix all permissions
   ```

4. **Login Failures**
   - Check credentials in `.env` file
   - Verify account isn't locked
   - Handle 2FA manually if required
   - Check for CAPTCHA requirements

5. **No Jobs Found**
   - Broaden search criteria in `config/profile_config.py`
   - Check target roles and locations
   - Verify platform availability
   - Check internet connection

6. **Application Failures**
   - Check internet connection
   - Verify resume file path in `.env`
   - Monitor platform changes
   - Check application limits

### Debug Mode
```bash
# Run with verbose logging
LOG_LEVEL=DEBUG python main.py --run-once

# Test browser only
python main.py --diagnose

# Quick troubleshoot
python troubleshoot.py
```

### System Requirements Check
```bash
# Check if your system is compatible
python main.py --diagnose
```

This will check:
- Python version compatibility
- Required dependencies
- Chrome browser installation
- ChromeDriver availability
- Network connectivity
- File permissions

## 📝 Customization

### Adding New Platforms
1. Create a new scraper in `scrapers/`
2. Implement required methods (search_jobs, apply_to_job, etc.)
3. Add platform configuration
4. Update the job applicator

### Custom Filters
Modify `filters/job_filter.py` to add custom filtering logic:
- Company blacklist/whitelist
- Salary requirements
- Job type preferences
- Experience level matching

### Notification Integration
Add email/SMS notifications by modifying the scheduler:
```python
# Add notification service
from utils.notifications import send_notification

# In scheduler after successful application
send_notification(f"Applied to {job_title} at {company}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and personal use only. Please ensure compliance with platform terms of service and local laws.

## ⚡ Quick Start Example

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Update profile
# Edit config/profile_config.py

# 4. Test run
python main.py --run-once --platform naukri

# 5. Start scheduler
python main.py --start
```

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for errors
3. Ensure all prerequisites are met
4. Verify configuration files

---

**Disclaimer**: This tool is for educational purposes. Users are responsible for ensuring compliance with platform terms of service and applicable laws. Use responsibly and ethically.