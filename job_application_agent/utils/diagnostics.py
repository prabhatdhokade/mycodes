#!/usr/bin/env python3
"""
Diagnostic utility for Job Application Agent
Helps troubleshoot browser and ChromeDriver issues
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def run_command(command, shell=False):
    """Run a command and return result"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_python_environment():
    """Check Python environment"""
    print_section("PYTHON ENVIRONMENT")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Machine: {platform.machine()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Check if running on Apple Silicon
    if platform.system().lower() == 'darwin':
        success, output, _ = run_command(['uname', '-m'])
        if success:
            print(f"Mac Architecture: {output}")
            if 'arm64' in output:
                print("✅ Detected Apple Silicon (M1/M2) Mac")
            else:
                print("✅ Detected Intel Mac")

def check_dependencies():
    """Check required Python packages"""
    print_section("PYTHON DEPENDENCIES")
    
    required_packages = [
        'selenium', 'beautifulsoup4', 'requests', 'pandas', 
        'schedule', 'python-dotenv', 'webdriver-manager', 
        'fake-useragent', 'lxml', 'sqlalchemy'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")

def check_chrome_installation():
    """Check Chrome/Chromium installation"""
    print_section("CHROME BROWSER")
    
    system = platform.system().lower()
    
    if system == 'darwin':  # Mac
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium'
        ]
    elif system == 'windows':
        chrome_paths = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe')
        ]
    else:  # Linux
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium'
        ]
    
    chrome_found = False
    chrome_version = None
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found: {path}")
            chrome_found = True
            
            # Try to get version
            try:
                if system == 'windows':
                    success, output, _ = run_command([path, '--version'])
                else:
                    success, output, _ = run_command([path, '--version'])
                
                if success and output:
                    chrome_version = output.split()[-1] if output else "Unknown"
                    print(f"   Version: {chrome_version}")
                    break
            except:
                pass
    
    if not chrome_found:
        print("❌ Chrome/Chromium not found")
        print("   Please install Google Chrome or Chromium browser")
    
    return chrome_found, chrome_version

def check_chromedriver():
    """Check ChromeDriver availability"""
    print_section("CHROMEDRIVER")
    
    # Check system PATH
    success, output, _ = run_command(['chromedriver', '--version'])
    if success:
        print(f"✅ ChromeDriver in PATH: {output}")
        return True
    
    # Check common installation paths
    system = platform.system().lower()
    
    if system == 'darwin':  # Mac
        paths = ['/usr/local/bin/chromedriver', '/opt/homebrew/bin/chromedriver']
    elif system == 'windows':
        paths = ['C:\\chromedriver\\chromedriver.exe', 'C:\\tools\\chromedriver.exe']
    else:  # Linux
        paths = ['/usr/bin/chromedriver', '/usr/local/bin/chromedriver']
    
    for path in paths:
        if os.path.exists(path):
            success, output, _ = run_command([path, '--version'])
            if success:
                print(f"✅ ChromeDriver found: {path}")
                print(f"   Version: {output}")
                return True
    
    # Check webdriver-manager cache
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("🔍 Checking webdriver-manager cache...")
        driver_path = ChromeDriverManager().install()
        if os.path.exists(driver_path):
            success, output, _ = run_command([driver_path, '--version'])
            if success:
                print(f"✅ webdriver-manager ChromeDriver: {driver_path}")
                print(f"   Version: {output}")
                return True
            else:
                print(f"❌ webdriver-manager ChromeDriver exists but not executable: {driver_path}")
    except Exception as e:
        print(f"❌ webdriver-manager error: {e}")
    
    print("❌ ChromeDriver not found")
    return False

def test_browser_initialization():
    """Test browser initialization"""
    print_section("BROWSER INITIALIZATION TEST")
    
    try:
        # Import the browser manager
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils.browser_utils import BrowserManager
        
        print("🧪 Testing browser initialization...")
        browser = BrowserManager(headless=True)
        
        if browser.initialize_driver():
            print("✅ Browser initialized successfully!")
            
            # Test basic functionality
            try:
                browser.navigate_to("https://www.google.com")
                print("✅ Navigation test passed")
                
                title = browser.driver.title
                print(f"   Page title: {title}")
                
            except Exception as e:
                print(f"❌ Navigation test failed: {e}")
            
            browser.close_browser()
            return True
        else:
            print("❌ Browser initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Browser test error: {e}")
        return False

def check_network_connectivity():
    """Check network connectivity to job platforms"""
    print_section("NETWORK CONNECTIVITY")
    
    test_urls = [
        "https://www.google.com",
        "https://www.naukri.com",
        "https://www.linkedin.com"
    ]
    
    for url in test_urls:
        try:
            import requests
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - Accessible")
            else:
                print(f"⚠️ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

def check_file_permissions():
    """Check file permissions in project directory"""
    print_section("FILE PERMISSIONS")
    
    current_dir = Path.cwd()
    
    # Check if we can write to current directory
    test_file = current_dir / "test_write.tmp"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ Write permissions: {current_dir}")
    except Exception as e:
        print(f"❌ Write permissions error: {e}")
    
    # Check logs directory
    logs_dir = current_dir / "logs"
    try:
        logs_dir.mkdir(exist_ok=True)
        print(f"✅ Logs directory: {logs_dir}")
    except Exception as e:
        print(f"❌ Logs directory error: {e}")

def provide_recommendations():
    """Provide recommendations based on findings"""
    print_section("RECOMMENDATIONS")
    
    system = platform.system().lower()
    
    print("🔧 SETUP RECOMMENDATIONS:")
    print()
    
    if system == 'darwin':  # Mac
        print("For Mac users:")
        print("1. Install Chrome: https://www.google.com/chrome/")
        print("2. If using Homebrew: brew install chromedriver")
        print("3. For Apple Silicon Macs, ensure you have the ARM64 version")
        print("4. Grant Terminal/IDE permissions in System Preferences > Security & Privacy")
        
    elif system == 'windows':
        print("For Windows users:")
        print("1. Install Chrome: https://www.google.com/chrome/")
        print("2. Download ChromeDriver: https://chromedriver.chromium.org/")
        print("3. Add ChromeDriver to PATH or place in C:\\chromedriver\\")
        print("4. Ensure Windows Defender doesn't block the executable")
        
    else:  # Linux
        print("For Linux users:")
        print("1. Install Chrome: sudo apt-get install google-chrome-stable")
        print("2. Install ChromeDriver: sudo apt-get install chromium-chromedriver")
        print("3. Or use: sudo snap install chromium")
    
    print()
    print("🚀 GENERAL TIPS:")
    print("1. Run: python setup.py (for automated setup)")
    print("2. Update Chrome to the latest version")
    print("3. Clear webdriver-manager cache if issues persist:")
    print("   rm -rf ~/.wdm (Mac/Linux) or del %TEMP%\\.wdm (Windows)")
    print("4. Check firewall/antivirus settings")
    print("5. Use headless mode for better stability: browser = BrowserManager(headless=True)")

def main():
    """Main diagnostic function"""
    print("🔍 Job Application Agent - System Diagnostics")
    print(f"Running on: {platform.system()} {platform.release()}")
    
    # Run all checks
    check_python_environment()
    check_dependencies()
    chrome_found, chrome_version = check_chrome_installation()
    chromedriver_found = check_chromedriver()
    check_network_connectivity()
    check_file_permissions()
    
    # Test browser if Chrome and ChromeDriver are available
    if chrome_found and chromedriver_found:
        browser_works = test_browser_initialization()
    else:
        browser_works = False
    
    # Summary
    print_section("SUMMARY")
    
    if chrome_found and chromedriver_found and browser_works:
        print("🎉 ALL CHECKS PASSED!")
        print("Your system should be ready to run the Job Application Agent.")
    else:
        print("⚠️ ISSUES DETECTED")
        print("Please review the recommendations below.")
    
    provide_recommendations()
    
    print(f"\n{'='*60}")
    print("Diagnostic complete. Save this output for troubleshooting.")
    print('='*60)

if __name__ == "__main__":
    main()