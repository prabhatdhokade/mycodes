#!/usr/bin/env python3
"""
Quick Troubleshooting Script for Job Application Agent
Run this if you encounter browser or ChromeDriver issues
"""

import os
import platform
import subprocess
import sys
import shutil
import tempfile

def clear_cache():
    """Clear webdriver-manager cache"""
    print("🧹 Clearing webdriver-manager cache...")
    
    try:
        # Clear webdriver-manager cache
        wdm_cache = os.path.join(tempfile.gettempdir(), '.wdm')
        if os.path.exists(wdm_cache):
            shutil.rmtree(wdm_cache, ignore_errors=True)
            print("✅ Cleared webdriver-manager cache")
        
        # Clear user cache directories
        system = platform.system().lower()
        
        if system == 'darwin':  # Mac
            cache_dirs = [
                os.path.expanduser("~/.wdm"),
                os.path.expanduser("~/Library/Caches/selenium"),
                os.path.expanduser("~/.chrome_drivers")
            ]
        elif system == 'windows':
            cache_dirs = [
                os.path.expanduser("~\\.wdm"),
                os.path.expanduser("~\\AppData\\Local\\Temp\\.wdm"),
                os.path.expanduser("~\\.chrome_drivers")
            ]
        else:  # Linux
            cache_dirs = [
                os.path.expanduser("~/.wdm"),
                os.path.expanduser("~/.cache/selenium"),
                os.path.expanduser("~/.chrome_drivers")
            ]
        
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir, ignore_errors=True)
                print(f"✅ Cleared cache: {cache_dir}")
    
    except Exception as e:
        print(f"⚠️ Error clearing cache: {e}")

def fix_permissions():
    """Fix ChromeDriver permissions on Unix systems"""
    if platform.system().lower() == 'windows':
        print("ℹ️ Permission fix not needed on Windows")
        return
    
    print("🔧 Fixing ChromeDriver permissions...")
    
    # Find potential ChromeDriver locations
    search_paths = [
        os.path.expanduser("~/.wdm"),
        os.path.expanduser("~/.chrome_drivers"),
        "/usr/local/bin",
        "/opt/homebrew/bin"
    ]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if 'chromedriver' in file:
                        file_path = os.path.join(root, file)
                        try:
                            os.chmod(file_path, 0o755)
                            print(f"✅ Fixed permissions: {file_path}")
                        except Exception as e:
                            print(f"⚠️ Could not fix permissions for {file_path}: {e}")

def reinstall_dependencies():
    """Reinstall Python dependencies"""
    print("📦 Reinstalling Python dependencies...")
    
    dependencies = [
        "selenium==4.15.2",
        "webdriver-manager==4.0.1",
        "requests>=2.31.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", dep], 
                         check=True, capture_output=True)
            print(f"✅ Reinstalled: {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to reinstall {dep}: {e}")

def download_chromedriver_manually():
    """Download ChromeDriver manually"""
    print("⬇️ Downloading ChromeDriver manually...")
    
    try:
        # Import after potential reinstall
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from utils.browser_utils import BrowserManager
        
        browser = BrowserManager()
        driver_path = browser._download_chromedriver_manually()
        
        if driver_path:
            print(f"✅ ChromeDriver downloaded successfully: {driver_path}")
            return True
        else:
            print("❌ Manual ChromeDriver download failed")
            return False
    
    except Exception as e:
        print(f"❌ Error during manual download: {e}")
        return False

def test_browser():
    """Test browser initialization"""
    print("🧪 Testing browser initialization...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from utils.browser_utils import BrowserManager
        
        browser = BrowserManager(headless=True)
        if browser.initialize_driver():
            print("✅ Browser test successful!")
            browser.close_browser()
            return True
        else:
            print("❌ Browser test failed")
            return False
    
    except Exception as e:
        print(f"❌ Browser test error: {e}")
        return False

def main():
    """Main troubleshooting function"""
    print("🔧 Job Application Agent - Quick Troubleshoot")
    print("=" * 50)
    
    print("This script will attempt to fix common issues:")
    print("1. Clear all caches")
    print("2. Fix file permissions")
    print("3. Reinstall key dependencies")
    print("4. Download ChromeDriver manually")
    print("5. Test browser initialization")
    
    response = input("\nDo you want to proceed? (y/n): ").lower().strip()
    if not response.startswith('y'):
        print("Troubleshooting cancelled.")
        return
    
    print("\n🚀 Starting troubleshooting process...")
    
    # Step 1: Clear caches
    clear_cache()
    
    # Step 2: Fix permissions (Unix only)
    fix_permissions()
    
    # Step 3: Reinstall dependencies
    reinstall_dependencies()
    
    # Step 4: Download ChromeDriver manually
    download_success = download_chromedriver_manually()
    
    # Step 5: Test browser
    test_success = test_browser()
    
    print("\n" + "=" * 50)
    print("🏁 TROUBLESHOOTING COMPLETE")
    print("=" * 50)
    
    if test_success:
        print("🎉 SUCCESS! Browser is working correctly.")
        print("\nNext steps:")
        print("1. Configure your credentials in .env file")
        print("2. Update your profile in config/profile_config.py")
        print("3. Run: python main.py --run-once")
    else:
        print("❌ ISSUES REMAIN")
        print("\nAdditional steps to try:")
        print("1. Run full diagnostics: python main.py --diagnose")
        print("2. Update Chrome browser to latest version")
        print("3. Check firewall/antivirus settings")
        print("4. Try running with admin/sudo privileges")
        print("5. Install Chrome manually from https://www.google.com/chrome/")
        
        if platform.system().lower() == 'darwin':
            print("\nFor Mac users:")
            print("- Try: brew install chromedriver")
            print("- Check System Preferences > Security & Privacy")
            print("- For M1/M2 Macs, ensure ARM64 compatibility")
        elif platform.system().lower() == 'windows':
            print("\nFor Windows users:")
            print("- Check Windows Defender exclusions")
            print("- Try running as Administrator")
            print("- Manually download ChromeDriver to C:\\chromedriver\\")

if __name__ == "__main__":
    main()