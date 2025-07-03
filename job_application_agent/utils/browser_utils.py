from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import random
import os
import logging
import platform
import subprocess
import shutil
import requests
import zipfile
import stat

class BrowserManager:
    def __init__(self, headless=False, user_agent=None):
        self.headless = headless
        self.user_agent = user_agent or UserAgent().random
        self.driver = None
        self.wait = None
        self.chrome_driver_path = None
        
    def _detect_system_architecture(self):
        """Detect system and architecture"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Detect ARM64 Mac
        if system == 'darwin':
            try:
                # Check if running on Apple Silicon
                result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
                if result.returncode == 0 and 'arm64' in result.stdout:
                    return 'mac_arm64'
                else:
                    return 'mac_x64'
            except:
                return 'mac_x64'  # Default to Intel
        elif system == 'windows':
            if 'amd64' in machine or 'x86_64' in machine:
                return 'win64'
            else:
                return 'win32'
        elif system == 'linux':
            if 'aarch64' in machine or 'arm64' in machine:
                return 'linux_arm64'
            else:
                return 'linux64'
        
        return 'unknown'
    
    def _get_chrome_version(self):
        """Get installed Chrome version"""
        try:
            system = platform.system().lower()
            
            if system == 'darwin':  # Mac
                cmd = '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            elif system == 'windows':
                # Try multiple possible Chrome paths
                chrome_paths = [
                    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
                ]
                result = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        result = subprocess.run([path, '--version'], capture_output=True, text=True)
                        break
            else:  # Linux
                result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            
            if result and result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                # Extract major version
                major_version = version.split('.')[0]
                return major_version
                
        except Exception as e:
            logging.warning(f"Could not detect Chrome version: {e}")
        
        return None
    
    def _download_chromedriver_manually(self, version=None):
        """Manually download ChromeDriver if webdriver-manager fails"""
        try:
            arch = self._detect_system_architecture()
            chrome_version = version or self._get_chrome_version() or "114"  # Default to stable version
            
            # ChromeDriver download URLs
            base_url = "https://chromedriver.storage.googleapis.com"
            
            # For newer versions (115+), use the new endpoint
            if int(chrome_version) >= 115:
                base_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
                
            # Map architecture to download names
            arch_map = {
                'mac_arm64': 'mac-arm64',
                'mac_x64': 'mac-x64', 
                'win32': 'win32',
                'win64': 'win64',
                'linux64': 'linux64',
                'linux_arm64': 'linux64'  # Use linux64 as fallback
            }
            
            platform_name = arch_map.get(arch, 'linux64')
            
            # Create drivers directory
            drivers_dir = os.path.expanduser("~/.chrome_drivers")
            os.makedirs(drivers_dir, exist_ok=True)
            
            # Try to get the latest stable version first
            try:
                if int(chrome_version) >= 115:
                    # New API for Chrome 115+
                    api_url = f"https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json"
                    response = requests.get(api_url, timeout=30)
                    if response.status_code == 200:
                        versions = response.json()
                        stable_version = versions.get('milestones', {}).get(chrome_version, {}).get('version')
                        if stable_version:
                            download_url = f"{base_url}/{stable_version}/{platform_name}/chromedriver-{platform_name}.zip"
                        else:
                            # Fallback to a known working version
                            download_url = f"{base_url}/120.0.6099.71/{platform_name}/chromedriver-{platform_name}.zip"
                    else:
                        download_url = f"{base_url}/120.0.6099.71/{platform_name}/chromedriver-{platform_name}.zip"
                else:
                    # Old API for Chrome < 115
                    latest_url = f"{base_url}/LATEST_RELEASE_{chrome_version}"
                    response = requests.get(latest_url, timeout=10)
                    if response.status_code == 200:
                        version = response.text.strip()
                        download_url = f"{base_url}/{version}/chromedriver_{platform_name}.zip"
                    else:
                        # Fallback to a known working version
                        download_url = f"{base_url}/114.0.5735.90/chromedriver_{platform_name}.zip"
                        
            except Exception:
                # Ultimate fallback
                if int(chrome_version) >= 115:
                    download_url = f"{base_url}/120.0.6099.71/{platform_name}/chromedriver-{platform_name}.zip"
                else:
                    download_url = f"{base_url}/114.0.5735.90/chromedriver_{platform_name}.zip"
            
            logging.info(f"Downloading ChromeDriver from: {download_url}")
            
            # Download the zip file
            zip_path = os.path.join(drivers_dir, "chromedriver.zip")
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(drivers_dir)
            
            # Find the chromedriver executable
            chromedriver_name = "chromedriver.exe" if platform.system().lower() == 'windows' else "chromedriver"
            
            # Look for chromedriver in extracted folders
            for root, dirs, files in os.walk(drivers_dir):
                for file in files:
                    if file == chromedriver_name:
                        chromedriver_path = os.path.join(root, file)
                        # Make executable on Unix systems
                        if platform.system().lower() != 'windows':
                            os.chmod(chromedriver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                        
                        # Clean up
                        try:
                            os.remove(zip_path)
                        except:
                            pass
                        
                        logging.info(f"ChromeDriver downloaded successfully: {chromedriver_path}")
                        return chromedriver_path
            
            raise Exception("ChromeDriver executable not found in downloaded archive")
            
        except Exception as e:
            logging.error(f"Failed to download ChromeDriver manually: {e}")
            return None
    
    def _get_system_chrome_path(self):
        """Get Chrome executable path based on system"""
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
        
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        
        return None
        
    def initialize_driver(self):
        """Initialize Chrome WebDriver with improved cross-platform support"""
        try:
            chrome_options = Options()
            
            # Basic options
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Essential options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Set user agent
            chrome_options.add_argument(f"--user-agent={self.user_agent}")
            
            # Additional stability options
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--remote-debugging-port=9222")
            
            # Try to set Chrome binary path
            chrome_path = self._get_system_chrome_path()
            if chrome_path:
                chrome_options.binary_location = chrome_path
                logging.info(f"Using Chrome binary: {chrome_path}")
            
            # Disable images and notifications for faster loading
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.notifications": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Try multiple methods to get ChromeDriver
            driver_methods = [
                self._try_webdriver_manager,
                self._try_manual_download,
                self._try_system_chromedriver
            ]
            
            for method in driver_methods:
                try:
                    driver_path = method()
                    if driver_path:
                        service = Service(driver_path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        break
                except Exception as e:
                    logging.warning(f"Driver method failed: {e}")
                    continue
            
            if not self.driver:
                raise Exception("All ChromeDriver initialization methods failed")
            
            # Execute script to hide webdriver property
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except:
                pass
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            # Initialize WebDriverWait
            self.wait = WebDriverWait(self.driver, 10)
            
            logging.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error initializing browser: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
    
    def _try_webdriver_manager(self):
        """Try using webdriver-manager"""
        try:
            # Clear any cached drivers that might be corrupted
            import tempfile
            wdm_cache = os.path.join(tempfile.gettempdir(), '.wdm')
            if os.path.exists(wdm_cache):
                shutil.rmtree(wdm_cache, ignore_errors=True)
            
            driver_path = ChromeDriverManager().install()
            
            # Verify the driver is executable
            if os.path.exists(driver_path):
                # Test if the driver can be executed
                result = subprocess.run([driver_path, '--version'], capture_output=True, timeout=10)
                if result.returncode == 0:
                    return driver_path
                else:
                    # Driver exists but can't execute, try to fix permissions
                    if platform.system().lower() != 'windows':
                        os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                        # Test again
                        result = subprocess.run([driver_path, '--version'], capture_output=True, timeout=10)
                        if result.returncode == 0:
                            return driver_path
            
            return None
            
        except Exception as e:
            logging.warning(f"webdriver-manager failed: {e}")
            return None
    
    def _try_manual_download(self):
        """Try manual ChromeDriver download"""
        try:
            chrome_version = self._get_chrome_version()
            return self._download_chromedriver_manually(chrome_version)
        except Exception as e:
            logging.warning(f"Manual download failed: {e}")
            return None
    
    def _try_system_chromedriver(self):
        """Try using system-installed ChromeDriver"""
        try:
            # Check if chromedriver is in PATH
            result = subprocess.run(['chromedriver', '--version'], capture_output=True, timeout=10)
            if result.returncode == 0:
                return 'chromedriver'  # Use system chromedriver
        except:
            pass
        
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
                try:
                    result = subprocess.run([path, '--version'], capture_output=True, timeout=10)
                    if result.returncode == 0:
                        return path
                except:
                    continue
        
        return None
    
    def navigate_to(self, url, max_retries=3):
        """Navigate to a URL with retries"""
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                time.sleep(random.uniform(1, 3))  # Random delay
                return True
            except Exception as e:
                logging.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    logging.error(f"Failed to navigate to {url} after {max_retries} attempts")
                    return False
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.warning(f"Element not found: {by}={value}")
            return None
    
    def wait_for_clickable(self, by, value, timeout=10):
        """Wait for an element to be clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logging.warning(f"Element not clickable: {by}={value}")
            return None
    
    def safe_click(self, element):
        """Safely click an element with error handling"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            time.sleep(random.uniform(0.5, 1.5))
            return True
        except Exception as e:
            logging.warning(f"Failed to click element: {e}")
            try:
                # Try JavaScript click as fallback
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(random.uniform(0.5, 1.5))
                return True
            except Exception as e2:
                logging.error(f"JavaScript click also failed: {e2}")
                return False
    
    def safe_send_keys(self, element, text, clear_first=True):
        """Safely send keys to an element"""
        try:
            if clear_first:
                element.clear()
            
            # Type with random delays to simulate human behavior
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.01, 0.1))
            
            time.sleep(random.uniform(0.5, 1.0))
            return True
        except Exception as e:
            logging.warning(f"Failed to send keys: {e}")
            return False
    
    def take_screenshot(self, filename=None):
        """Take a screenshot of the current page"""
        try:
            if filename is None:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = os.path.join("logs", filename)
            os.makedirs("logs", exist_ok=True)
            
            self.driver.save_screenshot(screenshot_path)
            logging.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")
            return None
    
    def scroll_to_bottom(self, pause_time=2):
        """Scroll to the bottom of the page to load all content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait to load page
                time.sleep(pause_time)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            logging.warning(f"Error during scrolling: {e}")
    
    def get_page_source(self):
        """Get the page source with error handling"""
        try:
            return self.driver.page_source
        except Exception as e:
            logging.error(f"Failed to get page source: {e}")
            return None
    
    def close_browser(self):
        """Close the browser and clean up"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("Browser closed successfully")
        except Exception as e:
            logging.error(f"Error closing browser: {e}")
    
    def human_like_delay(self, min_seconds=1, max_seconds=3):
        """Add human-like delays between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def handle_popup(self):
        """Handle common popups and overlays"""
        try:
            # Common selectors for popups/overlays
            popup_selectors = [
                "button[aria-label='Close']",
                "button[aria-label='close']",
                ".close-button",
                ".modal-close",
                "[class*='close']",
                ".popup-close"
            ]
            
            for selector in popup_selectors:
                try:
                    popup_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if popup_element.is_displayed():
                        popup_element.click()
                        time.sleep(1)
                        logging.info("Popup closed")
                        return True
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            logging.warning(f"Error handling popup: {e}")
        
        return False
    
    def switch_to_new_tab(self):
        """Switch to the newest tab"""
        try:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            return True
        except Exception as e:
            logging.error(f"Failed to switch to new tab: {e}")
            return False
    
    def close_current_tab(self):
        """Close the current tab and switch to the previous one"""
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
            return True
        except Exception as e:
            logging.error(f"Failed to close tab: {e}")
            return False