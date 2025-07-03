"""
Smart Form Handler - Intelligent Dynamic Form Filling System
Detects and answers dynamic questions in job application forms
"""

import re
import time
import random
from typing import Dict, List, Optional, Tuple, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

from config.enhanced_profile_config import (
    SMART_FORM_ANSWERS, 
    QUESTION_PATTERNS, 
    APPLICATION_CONFIG,
    USER_PROFILE
)
from utils.logger import get_logger

logger = get_logger('SmartFormHandler')

class SmartFormHandler:
    """Intelligent form handler for dynamic job application questions"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.profile = USER_PROFILE
        self.answers = SMART_FORM_ANSWERS
        self.patterns = QUESTION_PATTERNS
        self.config = APPLICATION_CONFIG
        
        # Track filled fields to avoid duplicates
        self.filled_fields = set()
        
    def handle_application_form(self) -> bool:
        """Main method to handle application form with dynamic questions"""
        try:
            logger.info("Starting smart form handling...")
            
            # Wait for form to load
            time.sleep(2)
            
            # Find and fill all form elements
            form_filled = self._process_form_elements()
            
            if form_filled:
                logger.info("Form filled successfully")
                return self._submit_form()
            else:
                logger.warning("No form elements found or filled")
                return False
                
        except Exception as e:
            logger.error(f"Error handling application form: {e}")
            return False
    
    def _process_form_elements(self) -> bool:
        """Process all form elements and fill them intelligently"""
        filled_count = 0
        
        try:
            # Find all possible form elements
            form_elements = self._find_all_form_elements()
            
            logger.info(f"Found {len(form_elements)} form elements to process")
            
            for element in form_elements:
                try:
                    if self._fill_form_element(element):
                        filled_count += 1
                        
                    # Human-like delay between fields
                    self._add_human_delay()
                    
                except Exception as e:
                    logger.warning(f"Error filling form element: {e}")
                    continue
            
            logger.info(f"Successfully filled {filled_count} form elements")
            return filled_count > 0
            
        except Exception as e:
            logger.error(f"Error processing form elements: {e}")
            return False
    
    def _find_all_form_elements(self) -> List:
        """Find all form elements on the page"""
        elements = []
        
        try:
            # Find input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            elements.extend(inputs)
            
            # Find textarea fields
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            elements.extend(textareas)
            
            # Find select dropdowns
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            elements.extend(selects)
            
            # Find radio buttons and checkboxes
            radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            elements.extend(radios)
            
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            elements.extend(checkboxes)
            
            # Filter out hidden and disabled elements
            visible_elements = []
            for element in elements:
                try:
                    if (element.is_displayed() and 
                        element.is_enabled() and 
                        element.get_attribute('type') not in ['hidden', 'submit', 'button']):
                        visible_elements.append(element)
                except:
                    continue
            
            return visible_elements
            
        except Exception as e:
            logger.error(f"Error finding form elements: {e}")
            return []
    
    def _fill_form_element(self, element) -> bool:
        """Fill a specific form element based on its context"""
        try:
            # Get element attributes and context
            element_info = self._analyze_element(element)
            
            if not element_info:
                return False
            
            # Skip if already filled
            element_id = element_info.get('id', '')
            if element_id in self.filled_fields:
                return False
            
            # Determine the appropriate answer
            answer = self._get_smart_answer(element_info)
            
            if answer is None:
                logger.debug(f"No answer found for element: {element_info.get('question', 'Unknown')}")
                return False
            
            # Fill the element based on its type
            success = self._fill_element_by_type(element, element_info, answer)
            
            if success and element_id:
                self.filled_fields.add(element_id)
                logger.info(f"Filled field '{element_info.get('question', element_id)}' with '{answer}'")
            
            return success
            
        except Exception as e:
            logger.warning(f"Error filling form element: {e}")
            return False
    
    def _analyze_element(self, element) -> Optional[Dict]:
        """Analyze form element to understand what it's asking"""
        try:
            info = {
                'element': element,
                'tag': element.tag_name.lower(),
                'type': element.get_attribute('type') or '',
                'id': element.get_attribute('id') or '',
                'name': element.get_attribute('name') or '',
                'placeholder': element.get_attribute('placeholder') or '',
                'label': self._find_element_label(element),
                'question': '',
                'context': ''
            }
            
            # Build question context from available text
            question_parts = []
            
            if info['label']:
                question_parts.append(info['label'])
            if info['placeholder']:
                question_parts.append(info['placeholder'])
            if info['name']:
                question_parts.append(info['name'].replace('_', ' ').replace('-', ' '))
            if info['id']:
                question_parts.append(info['id'].replace('_', ' ').replace('-', ' '))
            
            info['question'] = ' '.join(question_parts).lower()
            info['context'] = info['question']
            
            # Additional context from nearby text
            nearby_text = self._get_nearby_text(element)
            if nearby_text:
                info['context'] += ' ' + nearby_text.lower()
            
            return info
            
        except Exception as e:
            logger.warning(f"Error analyzing element: {e}")
            return None
    
    def _find_element_label(self, element) -> str:
        """Find the label associated with an element"""
        try:
            # Try to find label by 'for' attribute
            element_id = element.get_attribute('id')
            if element_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                if label:
                    return label.text.strip()
        except:
            pass
        
        try:
            # Try to find parent label
            parent = element.find_element(By.XPATH, "..")
            if parent.tag_name.lower() == 'label':
                return parent.text.strip()
        except:
            pass
        
        try:
            # Try to find preceding label
            preceding_labels = element.find_elements(By.XPATH, "preceding-sibling::label")
            if preceding_labels:
                return preceding_labels[-1].text.strip()
        except:
            pass
        
        return ""
    
    def _get_nearby_text(self, element) -> str:
        """Get text content near the element for context"""
        try:
            # Get text from parent container
            parent = element.find_element(By.XPATH, "..")
            parent_text = parent.text.strip()
            
            # Filter out very long text (likely not relevant)
            if len(parent_text) < 200:
                return parent_text
            
        except:
            pass
        
        return ""
    
    def _get_smart_answer(self, element_info: Dict) -> Optional[str]:
        """Get the appropriate answer for a form element using smart matching"""
        question = element_info.get('question', '').lower()
        context = element_info.get('context', '').lower()
        
        # Direct keyword matching
        for key, answer in self.answers.items():
            if key.lower() in question or key.lower() in context:
                return str(answer)
        
        # Pattern matching using regex
        for pattern, answer_key in self.patterns.items():
            if re.search(pattern, context, re.IGNORECASE):
                if answer_key in self.answers:
                    return str(self.answers[answer_key])
        
        # Skill-specific experience matching
        skill_match = self._match_skill_experience(context)
        if skill_match:
            return skill_match
        
        # Fallback to common answers based on element type
        return self._get_fallback_answer(element_info)
    
    def _match_skill_experience(self, context: str) -> Optional[str]:
        """Match skill-specific experience questions"""
        skill_experience = self.profile.get('skill_experience', {})
        
        for skill, years in skill_experience.items():
            skill_lower = skill.lower()
            if skill_lower in context:
                # Look for experience-related keywords
                if any(keyword in context for keyword in ['experience', 'years', 'worked', 'using']):
                    return str(years)
        
        return None
    
    def _get_fallback_answer(self, element_info: Dict) -> Optional[str]:
        """Get fallback answers for common element types"""
        element_type = element_info.get('type', '').lower()
        tag = element_info.get('tag', '').lower()
        question = element_info.get('question', '').lower()
        
        # Common fallbacks based on keywords
        fallbacks = {
            'email': self.profile['email'],
            'phone': self.profile['phone'],
            'mobile': self.profile['phone'],
            'name': self.profile['name'],
            'location': self.profile['location'],
            'city': self.profile['preferred_locations'][0],
            'experience': str(self.profile['total_experience_years']),
            'salary': str(self.profile['expected_ctc']),
            'ctc': str(self.profile['expected_ctc']),
            'notice': self.profile['notice_period'],
            'cover': self.answers['cover_letter']
        }
        
        for keyword, answer in fallbacks.items():
            if keyword in question:
                return str(answer)
        
        # Type-based fallbacks
        if element_type == 'email':
            return self.profile['email']
        elif element_type == 'tel':
            return self.profile['phone']
        elif element_type == 'number':
            if 'year' in question or 'experience' in question:
                return str(self.profile['total_experience_years'])
            elif 'salary' in question or 'ctc' in question:
                return str(self.profile['expected_ctc'])
        
        return None
    
    def _fill_element_by_type(self, element, element_info: Dict, answer: str) -> bool:
        """Fill element based on its type"""
        try:
            element_type = element_info.get('type', '').lower()
            tag = element_info.get('tag', '').lower()
            
            if tag == 'select':
                return self._fill_select_element(element, answer)
            elif element_type in ['radio', 'checkbox']:
                return self._fill_choice_element(element, element_info, answer)
            elif tag == 'textarea':
                return self._fill_text_element(element, answer)
            elif element_type in ['text', 'email', 'tel', 'number', '']:
                return self._fill_text_element(element, answer)
            else:
                logger.debug(f"Unknown element type: {element_type}")
                return False
                
        except Exception as e:
            logger.warning(f"Error filling element by type: {e}")
            return False
    
    def _fill_text_element(self, element, answer: str) -> bool:
        """Fill text input or textarea"""
        try:
            # Clear existing content
            element.clear()
            
            # Type with human-like speed
            self._human_type(element, answer)
            
            return True
            
        except Exception as e:
            logger.warning(f"Error filling text element: {e}")
            return False
    
    def _fill_select_element(self, element, answer: str) -> bool:
        """Fill select dropdown"""
        try:
            select = Select(element)
            options = select.options
            
            # Try exact match first
            for option in options:
                if option.text.strip().lower() == answer.lower():
                    select.select_by_visible_text(option.text)
                    return True
            
            # Try partial match
            for option in options:
                if answer.lower() in option.text.strip().lower():
                    select.select_by_visible_text(option.text)
                    return True
            
            # Try value match
            for option in options:
                if option.get_attribute('value').lower() == answer.lower():
                    select.select_by_value(option.get_attribute('value'))
                    return True
            
            logger.debug(f"No matching option found for: {answer}")
            return False
            
        except Exception as e:
            logger.warning(f"Error filling select element: {e}")
            return False
    
    def _fill_choice_element(self, element, element_info: Dict, answer: str) -> bool:
        """Fill radio button or checkbox"""
        try:
            element_type = element_info.get('type', '').lower()
            
            # For radio buttons, find the matching option
            if element_type == 'radio':
                name = element.get_attribute('name')
                if name:
                    # Find all radio buttons with same name
                    radios = self.driver.find_elements(By.CSS_SELECTOR, f"input[name='{name}']")
                    
                    for radio in radios:
                        radio_label = self._find_element_label(radio)
                        radio_value = radio.get_attribute('value') or ''
                        
                        # Check if this radio matches our answer
                        if (answer.lower() in radio_label.lower() or 
                            answer.lower() == radio_value.lower()):
                            radio.click()
                            return True
            
            # For checkboxes, click based on yes/no answer
            elif element_type == 'checkbox':
                should_check = answer.lower() in ['yes', 'true', '1', 'y']
                if element.is_selected() != should_check:
                    element.click()
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error filling choice element: {e}")
            return False
    
    def _human_type(self, element, text: str):
        """Type text with human-like timing"""
        if not self.config.get('human_like_behavior', True):
            element.send_keys(text)
            return
        
        typing_speed = self.config.get('typing_speed', (0.1, 0.3))
        
        for char in text:
            element.send_keys(char)
            delay = random.uniform(typing_speed[0], typing_speed[1])
            time.sleep(delay)
    
    def _add_human_delay(self):
        """Add human-like delay between form actions"""
        if self.config.get('human_like_behavior', True):
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)
    
    def _submit_form(self) -> bool:
        """Submit the application form"""
        try:
            # Look for submit buttons
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Apply')",
                "button:contains('Submit')",
                "button:contains('Send Application')",
                ".apply-btn",
                ".submit-btn",
                "#apply-button",
                "#submit-button"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    if submit_button:
                        # Add delay before submission
                        delay = random.uniform(*self.config.get('form_submission_delay', (2, 5)))
                        time.sleep(delay)
                        
                        # Click submit button
                        self.driver.execute_script("arguments[0].click();", submit_button)
                        
                        logger.info("Form submitted successfully")
                        time.sleep(3)  # Wait for submission to process
                        return True
                        
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            # Try pressing Enter as fallback
            try:
                active_element = self.driver.switch_to.active_element
                active_element.send_keys(Keys.RETURN)
                logger.info("Form submitted using Enter key")
                time.sleep(3)
                return True
            except:
                pass
            
            logger.warning("No submit button found")
            return False
            
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False
    
    def handle_file_upload(self, file_path: str) -> bool:
        """Handle resume/file upload if required"""
        try:
            # Look for file input elements
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            if not file_inputs:
                return True  # No file upload required
            
            for file_input in file_inputs:
                try:
                    if file_input.is_displayed():
                        file_input.send_keys(file_path)
                        logger.info(f"Uploaded file: {file_path}")
                        time.sleep(2)
                        return True
                except Exception as e:
                    logger.warning(f"Error uploading file: {e}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling file upload: {e}")
            return False
    
    def detect_captcha(self) -> bool:
        """Detect if there's a CAPTCHA on the page"""
        try:
            captcha_selectors = [
                "[class*='captcha']",
                "[id*='captcha']",
                ".recaptcha",
                "#recaptcha",
                ".g-recaptcha",
                "[class*='security']"
            ]
            
            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(elem.is_displayed() for elem in elements):
                    logger.warning("CAPTCHA detected - manual intervention required")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return False