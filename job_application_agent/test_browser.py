#!/usr/bin/env python3
"""
Simple browser test script to verify ChromeDriver fixes
Run this to test if the browser initialization works on your system
"""

import sys
import os
import platform

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_import():
    """Test if basic imports work"""
    print("🧪 Testing basic imports...")
    try:
        from utils.browser_utils import BrowserManager
        print("✅ BrowserManager import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_browser_initialization():
    """Test browser initialization"""
    print("\n🧪 Testing browser initialization...")
    try:
        from utils.browser_utils import BrowserManager
        
        # Test with headless mode for reliability
        browser = BrowserManager(headless=True)
        print("   Creating browser instance...")
        
        if browser.initialize_driver():
            print("✅ Browser initialized successfully!")
            
            # Test basic navigation
            print("   Testing navigation...")
            if browser.navigate_to("https://www.google.com"):
                print("✅ Navigation test passed")
                
                # Get page title
                try:
                    title = browser.driver.title
                    print(f"   Page title: {title}")
                except:
                    print("   Could not get page title (but that's okay)")
                
            else:
                print("⚠️ Navigation test failed")
            
            # Clean up
            browser.close_browser()
            return True
        else:
            print("❌ Browser initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Browser test error: {e}")
        return False

def test_platform_detection():
    """Test platform-specific functionality"""
    print("\n🧪 Testing platform detection...")
    try:
        from utils.browser_utils import BrowserManager
        
        browser = BrowserManager()
        
        # Test architecture detection
        arch = browser._detect_system_architecture()
        print(f"   Detected architecture: {arch}")
        
        # Test Chrome version detection
        chrome_version = browser._get_chrome_version()
        if chrome_version:
            print(f"   Chrome version: {chrome_version}")
        else:
            print("   Chrome version: Could not detect")
        
        # Test Chrome path detection
        chrome_path = browser._get_system_chrome_path()
        if chrome_path:
            print(f"   Chrome path: {chrome_path}")
        else:
            print("   Chrome path: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform detection error: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Browser Test Script")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Basic Imports", test_basic_import),
        ("Platform Detection", test_platform_detection),
        ("Browser Initialization", test_browser_initialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("Your browser setup is working correctly.")
        print("\nNext steps:")
        print("1. Configure your credentials: cp .env.example .env")
        print("2. Update your profile: edit config/profile_config.py")
        print("3. Run the agent: python main.py --run-once")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Try running the troubleshooter:")
        print("   python troubleshoot.py")
        print("Or run full diagnostics:")
        print("   python main.py --diagnose")

if __name__ == "__main__":
    main()