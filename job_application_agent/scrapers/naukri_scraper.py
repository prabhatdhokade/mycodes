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

from utils.browser_utils import BrowserManager
from utils.logger import get_logger
from config.profile_config import USER_PROFILE, PLATFORM_CONFIG

load_dotenv()
logger = get_logger('NaukriScraper')

class NaukriScraper:
    def __init__(self):
        self.browser = BrowserManager()
        self.base_url = PLATFORM_CONFIG['naukri']['base_url']
        self.is_logged_in = False
        self.profile = USER_PROFILE
        
    def initialize(self):
        """Initialize the browser and navigate to Naukri"""
        if not self.browser.initialize_driver():
            logger.error("Failed to initialize browser")
            return False
            
        if not self.browser.navigate_to(self.base_url):
            logger.error("Failed to navigate to Naukri.com")
            return False
            
        return True
    
    def login(self):
        """Login to Naukri.com"""
        try:
            email = os.getenv('NAUKRI_EMAIL')
            password = os.getenv('NAUKRI_PASSWORD')
            
            if not email or not password:
                logger.error("Naukri credentials not found in environment variables")
                return False
            
            # Navigate to login page
            login_url = f"{self.base_url}/nlogin/login"
            if not self.browser.navigate_to(login_url):
                return False
            
            # Wait for and fill email
            email_field = self.browser.wait_for_element(By.ID, "usernameField")
            if not email_field:
                logger.error("Email field not found")
                return False
            
            self.browser.safe_send_keys(email_field, email)
            
            # Fill password
            password_field = self.browser.wait_for_element(By.ID, "passwordField")
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
            
            # Wait for login success
            time.sleep(5)
            
            # Check if login was successful
            if "naukri.com/mnjuser/homepage" in self.browser.driver.current_url or "naukri.com/mnjuser/profile" in self.browser.driver.current_url:
                self.is_logged_in = True
                logger.info("Successfully logged into Naukri.com")
                return True
            else:
                logger.error("Login failed - not redirected to homepage")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def search_jobs(self, location="", keywords="", experience=""):
        """Search for jobs on Naukri"""
        try:
            # Construct search parameters based on profile
            if not keywords:
                keywords = " ".join(self.profile['target_roles'][:3])
            
            if not location:
                location = self.profile['preferred_locations'][0]
            
            # Navigate to jobs search page
            search_url = f"{self.base_url}/jobs-in-{location.lower().replace(' ', '-')}"
            
            # Add search parameters
            search_params = f"?k={keywords.replace(' ', '%20')}"
            full_url = search_url + search_params
            
            logger.info(f"Searching jobs with URL: {full_url}")
            
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
            self.browser.scroll_to_bottom(pause_time=2)
            
            # Get page source
            page_source = self.browser.get_page_source()
            if not page_source:
                return jobs
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find job cards (Naukri uses different selectors, this might need adjustment)
            job_cards = soup.find_all(['div'], class_=re.compile(r'jobTuple|srp-jobtuple-wrapper|job-tuple'))
            
            logger.info(f"Found {len(job_cards)} job cards on page")
            
            for card in job_cards:
                job_data = self._extract_job_details(card)
                if job_data:
                    jobs.append(job_data)
            
        except Exception as e:
            logger.error(f"Error extracting jobs from page: {e}")
        
        return jobs
    
    def _extract_job_details(self, job_card):
        """Extract details from a single job card"""
        try:
            job_data = {
                'platform': 'naukri',
                'scraped_date': datetime.now()
            }
            
            # Extract job title
            title_element = job_card.find(['a', 'h3', 'h4'], class_=re.compile(r'title|job-title|jobTitle'))
            if title_element:
                job_data['title'] = title_element.get_text(strip=True)
                # Extract job URL
                if title_element.name == 'a' and title_element.get('href'):
                    job_url = title_element['href']
                    if not job_url.startswith('http'):
                        job_url = self.base_url + job_url
                    job_data['job_url'] = job_url
            
            # Extract company name
            company_element = job_card.find(['a', 'span', 'div'], class_=re.compile(r'company|subTitle'))
            if company_element:
                job_data['company'] = company_element.get_text(strip=True)
            
            # Extract location
            location_element = job_card.find(['span', 'div'], class_=re.compile(r'location|locationsContainer'))
            if location_element:
                job_data['location'] = location_element.get_text(strip=True)
            
            # Extract experience
            exp_element = job_card.find(['span', 'div'], class_=re.compile(r'experience|exp'))
            if exp_element:
                job_data['experience_required'] = exp_element.get_text(strip=True)
            
            # Extract salary
            salary_element = job_card.find(['span', 'div'], class_=re.compile(r'salary|ctc'))
            if salary_element:
                salary_text = salary_element.get_text(strip=True)
                salary_min, salary_max = self._parse_salary(salary_text)
                job_data['salary_min'] = salary_min
                job_data['salary_max'] = salary_max
            
            # Extract job description snippet
            desc_element = job_card.find(['span', 'div', 'p'], class_=re.compile(r'job-description|description'))
            if desc_element:
                job_data['description'] = desc_element.get_text(strip=True)
            
            # Extract posted date
            date_element = job_card.find(['span', 'div'], class_=re.compile(r'date|posted|time'))
            if date_element:
                posted_date = self._parse_posted_date(date_element.get_text(strip=True))
                if posted_date:
                    job_data['posted_date'] = posted_date
            
            # Only return job if we have essential information
            if job_data.get('title') and job_data.get('company'):
                return job_data
            
        except Exception as e:
            logger.warning(f"Error extracting job details: {e}")
        
        return None
    
    def _parse_salary(self, salary_text):
        """Parse salary text and extract min/max values in LPA"""
        try:
            # Remove common unwanted characters
            salary_text = re.sub(r'[^\d\.\-\s]', '', salary_text)
            
            # Look for patterns like "5-8", "5.5-7.5", "5 - 8"
            range_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', salary_text)
            if range_match:
                min_sal = float(range_match.group(1))
                max_sal = float(range_match.group(2))
                return min_sal, max_sal
            
            # Look for single number
            single_match = re.search(r'(\d+(?:\.\d+)?)', salary_text)
            if single_match:
                salary = float(single_match.group(1))
                return salary, salary
            
        except Exception as e:
            logger.warning(f"Error parsing salary: {salary_text} - {e}")
        
        return None, None
    
    def _parse_posted_date(self, date_text):
        """Parse posted date text"""
        try:
            date_text = date_text.lower().strip()
            
            # Handle relative dates
            if 'today' in date_text or 'just now' in date_text:
                return datetime.now()
            elif 'yesterday' in date_text:
                return datetime.now() - timedelta(days=1)
            elif 'day' in date_text:
                days = re.search(r'(\d+)', date_text)
                if days:
                    return datetime.now() - timedelta(days=int(days.group(1)))
            elif 'week' in date_text:
                weeks = re.search(r'(\d+)', date_text)
                if weeks:
                    return datetime.now() - timedelta(weeks=int(weeks.group(1)))
            
            # Try parsing absolute dates
            for date_format in ['%d %b %Y', '%d-%m-%Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_text, date_format)
                except ValueError:
                    continue
            
        except Exception as e:
            logger.warning(f"Error parsing date: {date_text} - {e}")
        
        return None
    
    def get_job_details(self, job_url):
        """Get detailed job information from job URL"""
        try:
            if not self.browser.navigate_to(job_url):
                return None
            
            time.sleep(2)
            page_source = self.browser.get_page_source()
            if not page_source:
                return None
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract detailed job description
            desc_element = soup.find(['div', 'section'], class_=re.compile(r'job-description|jd|description'))
            description = ""
            if desc_element:
                description = desc_element.get_text(strip=True, separator=' ')
            
            return {
                'detailed_description': description,
                'full_page_html': page_source
            }
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def apply_to_job(self, job_url):
        """Apply to a job (basic implementation)"""
        try:
            if not self.is_logged_in:
                logger.error("Not logged in, cannot apply to jobs")
                return False
            
            if not self.browser.navigate_to(job_url):
                return False
            
            # Look for apply button
            apply_selectors = [
                "button[id*='apply']",
                "a[id*='apply']",
                "button:contains('Apply')",
                ".apply-button",
                "#apply-button"
            ]
            
            for selector in apply_selectors:
                try:
                    apply_button = self.browser.wait_for_clickable(By.CSS_SELECTOR, selector, timeout=5)
                    if apply_button:
                        self.browser.safe_click(apply_button)
                        time.sleep(2)
                        
                        # Handle any application form or confirmation
                        self._handle_application_form()
                        
                        logger.info(f"Successfully applied to job: {job_url}")
                        return True
                except Exception:
                    continue
            
            logger.warning(f"Apply button not found for job: {job_url}")
            return False
            
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return False
    
    def _handle_application_form(self):
        """Handle application form if it appears"""
        try:
            # Look for submit button in application form
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Submit')",
                ".submit-button"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.browser.wait_for_clickable(By.CSS_SELECTOR, selector, timeout=3)
                    if submit_button:
                        self.browser.safe_click(submit_button)
                        time.sleep(1)
                        break
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error handling application form: {e}")
    
    def close(self):
        """Close the browser"""
        if self.browser:
            self.browser.close_browser()