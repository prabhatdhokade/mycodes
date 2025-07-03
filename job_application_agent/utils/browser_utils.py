from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import random
import os
import logging

class BrowserManager:
    def __init__(self, headless=False, user_agent=None):
        self.headless = headless
        self.user_agent = user_agent or UserAgent().random
        self.driver = None
        self.wait = None
        
    def initialize_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Basic browser settings
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Set user agent
            chrome_options.add_argument(f"--user-agent={self.user_agent}")
            
            # Disable images and CSS for faster loading (optional)
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize the driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            # Initialize WebDriverWait
            self.wait = WebDriverWait(self.driver, 10)
            
            logging.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error initializing browser: {e}")
            return False
    
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