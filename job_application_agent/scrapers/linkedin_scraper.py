import time
import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import random

from utils.browser_utils import BrowserManager
from utils.logger import get_logger
from config.profile_config import USER_PROFILE, PLATFORM_CONFIG

load_dotenv()
logger = get_logger('LinkedInScraper')

class LinkedInScraper:
    def __init__(self):
        self.browser = BrowserManager()
        self.base_url = PLATFORM_CONFIG['linkedin']['base_url']
        self.jobs_url = PLATFORM_CONFIG['linkedin']['jobs_url']
        self.is_logged_in = False
        self.profile = USER_PROFILE
        
    def initialize(self):
        """Initialize the browser and navigate to LinkedIn"""
        if not self.browser.initialize_driver():
            logger.error("Failed to initialize browser")
            return False
            
        if not self.browser.navigate_to(self.base_url):
            logger.error("Failed to navigate to LinkedIn")
            return False
            
        return True
    
    def login(self):
        """Login to LinkedIn"""
        try:
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if not email or not password:
                logger.error("LinkedIn credentials not found in environment variables")
                return False
            
            # Navigate to login page
            login_url = f"{self.base_url}/login"
            if not self.browser.navigate_to(login_url):
                return False
            
            # Wait for and fill email
            email_field = self.browser.wait_for_element(By.ID, "username")
            if not email_field:
                logger.error("Email field not found")
                return False
            
            self.browser.safe_send_keys(email_field, email)
            
            # Fill password
            password_field = self.browser.wait_for_element(By.ID, "password")
            if not password_field:
                logger.error("Password field not found")
                return False
            
            self.browser.safe_send_keys(password_field, password)
            
            # Click login button
            login_button = self.browser.wait_for_clickable(By.CSS_SELECTOR, "button[type='submit']")
            if not login_button:
                logger.error("Login button not found")
                return False
            
            self.browser.safe_click(login_button)
            
            # Wait for potential security check
            time.sleep(5)
            
            # Handle security verification if it appears
            self._handle_security_verification()
            
            # Check if login was successful
            if "linkedin.com/feed" in self.browser.driver.current_url or "linkedin.com/in/" in self.browser.driver.current_url:
                self.is_logged_in = True
                logger.info("Successfully logged into LinkedIn")
                return True
            else:
                logger.error("Login failed or requires manual verification")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def _handle_security_verification(self):
        """Handle LinkedIn security verification if it appears"""
        try:
            # Check for security verification page
            if "challenge" in self.browser.driver.current_url or "checkpoint" in self.browser.driver.current_url:
                logger.warning("LinkedIn security verification required - please complete manually")
                # Wait for user to complete verification
                input("Please complete the security verification in the browser and press Enter to continue...")
                
        except Exception as e:
            logger.warning(f"Error handling security verification: {e}")
    
    def search_jobs(self, location="", keywords="", experience_level=""):
        """Search for jobs on LinkedIn"""
        try:
            # Construct search parameters based on profile
            if not keywords:
                keywords = " ".join(self.profile['target_roles'][:3])
            
            if not location:
                location = self.profile['preferred_locations'][0]
            
            # Build search URL
            search_params = {
                'keywords': keywords,
                'location': location,
                'f_TPR': 'r86400',  # Past 24 hours
                'f_E': '2',  # Entry level (adjust based on experience)
                'sortBy': 'DD'  # Sort by date
            }
            
            # Convert experience level
            if experience_level or self.profile.get('experience_years', 0) <= 2:
                search_params['f_E'] = '1,2'  # Internship, Entry level
            elif self.profile.get('experience_years', 0) <= 5:
                search_params['f_E'] = '3'  # Associate
            else:
                search_params['f_E'] = '4,5'  # Mid-Senior, Director
            
            # Construct full URL
            params_string = "&".join([f"{k}={v.replace(' ', '%20')}" for k, v in search_params.items()])
            full_url = f"{self.jobs_url}?{params_string}"
            
            logger.info(f"Searching LinkedIn jobs with URL: {full_url}")
            
            if not self.browser.navigate_to(full_url):
                return []
            
            # Handle any popups
            self.browser.handle_popup()
            
            # Wait for job listings to load
            time.sleep(3)
            
            return self._extract_jobs_from_page()
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []
    
    def _extract_jobs_from_page(self):
        """Extract job details from the current page"""
        jobs = []
        
        try:
            # Scroll to load more jobs
            self._scroll_and_load_jobs()
            
            # Get page source
            page_source = self.browser.get_page_source()
            if not page_source:
                return jobs
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find job cards - LinkedIn uses specific class names
            job_cards = soup.find_all(['div'], class_=re.compile(r'job-search-card|jobs-search-results__list-item'))
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all(['li'], class_=re.compile(r'jobs-search-results__list-item'))
            
            logger.info(f"Found {len(job_cards)} job cards on LinkedIn page")
            
            for card in job_cards:
                job_data = self._extract_job_details(card)
                if job_data:
                    jobs.append(job_data)
            
        except Exception as e:
            logger.error(f"Error extracting jobs from LinkedIn page: {e}")
        
        return jobs
    
    def _scroll_and_load_jobs(self):
        """Scroll down to load more jobs on LinkedIn"""
        try:
            last_height = self.browser.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(3):  # Scroll a few times to load more jobs
                # Scroll down
                self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content to load
                time.sleep(random.uniform(2, 4))
                
                # Check for "Show more" button
                try:
                    show_more_btn = self.browser.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Show more']")
                    if show_more_btn.is_displayed():
                        self.browser.safe_click(show_more_btn)
                        time.sleep(2)
                except NoSuchElementException:
                    pass
                
                # Check if new content loaded
                new_height = self.browser.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"Error during scrolling: {e}")
    
    def _extract_job_details(self, job_card):
        """Extract details from a single LinkedIn job card"""
        try:
            job_data = {
                'platform': 'linkedin',
                'scraped_date': datetime.now()
            }
            
            # Extract job title and URL
            title_element = job_card.find('a', class_=re.compile(r'job-search-card__title-link'))
            if not title_element:
                title_element = job_card.find(['h3', 'h4'], class_=re.compile(r'job-search-card__title'))
                if title_element:
                    title_element = title_element.find('a')
            
            if title_element:
                job_data['title'] = title_element.get_text(strip=True)
                if title_element.get('href'):
                    job_url = title_element['href']
                    if not job_url.startswith('http'):
                        job_url = self.base_url + job_url
                    job_data['job_url'] = job_url
            
            # Extract company name
            company_element = job_card.find(['a', 'h4'], class_=re.compile(r'job-search-card__subtitle-link|hidden-nested-link'))
            if company_element:
                job_data['company'] = company_element.get_text(strip=True)
            
            # Extract location
            location_element = job_card.find(['span'], class_=re.compile(r'job-search-card__location'))
            if location_element:
                job_data['location'] = location_element.get_text(strip=True)
            
            # Extract posted date
            date_element = job_card.find(['time'], class_=re.compile(r'job-search-card__listdate'))
            if date_element:
                posted_date = self._parse_posted_date(date_element.get_text(strip=True))
                if posted_date:
                    job_data['posted_date'] = posted_date
            
            # Extract job description snippet (if available)
            desc_element = job_card.find(['p', 'span'], class_=re.compile(r'job-search-card__snippet'))
            if desc_element:
                job_data['description'] = desc_element.get_text(strip=True)
            
            # Extract easy apply indicator
            easy_apply = job_card.find(['span'], class_=re.compile(r'job-search-card__easy-apply'))
            if easy_apply:
                job_data['easy_apply'] = True
            
            # Only return job if we have essential information
            if job_data.get('title') and job_data.get('company'):
                return job_data
            
        except Exception as e:
            logger.warning(f"Error extracting LinkedIn job details: {e}")
        
        return None
    
    def _parse_posted_date(self, date_text):
        """Parse LinkedIn posted date text"""
        try:
            date_text = date_text.lower().strip()
            
            # Handle relative dates
            if 'just now' in date_text or 'moments ago' in date_text:
                return datetime.now()
            elif 'minute' in date_text:
                minutes = re.search(r'(\d+)', date_text)
                if minutes:
                    return datetime.now() - timedelta(minutes=int(minutes.group(1)))
            elif 'hour' in date_text:
                hours = re.search(r'(\d+)', date_text)
                if hours:
                    return datetime.now() - timedelta(hours=int(hours.group(1)))
            elif 'day' in date_text:
                days = re.search(r'(\d+)', date_text)
                if days:
                    return datetime.now() - timedelta(days=int(days.group(1)))
            elif 'week' in date_text:
                weeks = re.search(r'(\d+)', date_text)
                if weeks:
                    return datetime.now() - timedelta(weeks=int(weeks.group(1)))
            elif 'month' in date_text:
                months = re.search(r'(\d+)', date_text)
                if months:
                    return datetime.now() - timedelta(days=int(months.group(1)) * 30)
            
        except Exception as e:
            logger.warning(f"Error parsing LinkedIn date: {date_text} - {e}")
        
        return None
    
    def get_job_details(self, job_url):
        """Get detailed job information from LinkedIn job URL"""
        try:
            if not self.browser.navigate_to(job_url):
                return None
            
            time.sleep(2)
            
            # Click "Show more" to expand job description if needed
            try:
                show_more_btn = self.browser.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Show more']")
                if show_more_btn.is_displayed():
                    self.browser.safe_click(show_more_btn)
                    time.sleep(1)
            except NoSuchElementException:
                pass
            
            page_source = self.browser.get_page_source()
            if not page_source:
                return None
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract detailed job description
            desc_element = soup.find(['div'], class_=re.compile(r'jobs-description-content|jobs-box__html-content'))
            description = ""
            if desc_element:
                description = desc_element.get_text(strip=True, separator=' ')
            
            # Extract company info
            company_element = soup.find(['div'], class_=re.compile(r'jobs-company'))
            company_info = ""
            if company_element:
                company_info = company_element.get_text(strip=True, separator=' ')
            
            return {
                'detailed_description': description,
                'company_info': company_info,
                'full_page_html': page_source
            }
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn job details: {e}")
            return None
    
    def apply_to_job(self, job_url):
        """Apply to a LinkedIn job"""
        try:
            if not self.is_logged_in:
                logger.error("Not logged in, cannot apply to jobs")
                return False
            
            if not self.browser.navigate_to(job_url):
                return False
            
            time.sleep(2)
            
            # Look for Easy Apply button first
            easy_apply_btn = self.browser.wait_for_clickable(
                By.CSS_SELECTOR, 
                "button[aria-label*='Easy Apply']", 
                timeout=5
            )
            
            if easy_apply_btn:
                return self._handle_easy_apply(easy_apply_btn)
            
            # Look for regular Apply button
            apply_selectors = [
                "a[aria-label*='Apply']",
                "button:contains('Apply')",
                "a[href*='apply']"
            ]
            
            for selector in apply_selectors:
                try:
                    apply_button = self.browser.wait_for_clickable(By.CSS_SELECTOR, selector, timeout=3)
                    if apply_button:
                        self.browser.safe_click(apply_button)
                        # This will redirect to external site
                        logger.info(f"Redirected to external application for: {job_url}")
                        return True
                except Exception:
                    continue
            
            logger.warning(f"No apply button found for LinkedIn job: {job_url}")
            return False
            
        except Exception as e:
            logger.error(f"Error applying to LinkedIn job: {e}")
            return False
    
    def _handle_easy_apply(self, easy_apply_btn):
        """Handle LinkedIn Easy Apply process"""
        try:
            self.browser.safe_click(easy_apply_btn)
            time.sleep(2)
            
            # Handle multi-step application process
            max_steps = 5
            current_step = 0
            
            while current_step < max_steps:
                # Look for Next button
                next_btn = self.browser.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Continue'], button[aria-label*='Next']")
                
                if next_btn:
                    # Fill any required fields before clicking next
                    self._fill_application_fields()
                    
                    self.browser.safe_click(next_btn[0])
                    time.sleep(2)
                    current_step += 1
                    continue
                
                # Look for Submit/Review button (final step)
                submit_btn = self.browser.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Submit'], button[aria-label*='Review']")
                
                if submit_btn:
                    self._fill_application_fields()
                    self.browser.safe_click(submit_btn[0])
                    time.sleep(2)
                    logger.info("Successfully submitted LinkedIn Easy Apply application")
                    return True
                
                # If no next or submit button found, break
                break
            
            logger.warning("Easy Apply process incomplete - may require manual intervention")
            return False
            
        except Exception as e:
            logger.error(f"Error in Easy Apply process: {e}")
            return False
    
    def _fill_application_fields(self):
        """Fill common application fields during Easy Apply"""
        try:
            # Fill phone number if required
            phone_fields = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='tel'], input[id*='phone']")
            for field in phone_fields:
                if field.is_displayed() and not field.get_attribute('value'):
                    self.browser.safe_send_keys(field, self.profile.get('phone', ''))
            
            # Handle dropdown selections (experience level, etc.)
            dropdowns = self.browser.driver.find_elements(By.CSS_SELECTOR, "select")
            for dropdown in dropdowns:
                if dropdown.is_displayed():
                    # Try to select appropriate option based on context
                    options = dropdown.find_elements(By.TAG_NAME, "option")
                    for option in options[1:]:  # Skip first option (usually "Select...")
                        option_text = option.text.lower()
                        if any(exp in option_text for exp in ['2', '3', 'years']) and len(options) > 2:
                            option.click()
                            break
            
            # Handle yes/no questions (authorize to work, etc.)
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            for radio in radio_buttons:
                if radio.is_displayed() and 'yes' in radio.get_attribute('value', '').lower():
                    radio.click()
            
        except Exception as e:
            logger.warning(f"Error filling application fields: {e}")
    
    def close(self):
        """Close the browser"""
        if self.browser:
            self.browser.close_browser()