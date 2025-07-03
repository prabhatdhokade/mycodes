"""
Optimized Job Applicator - Enhanced Single Platform Job Application System
Features smart form handling, intelligent platform selection, and dynamic question answering
"""

import time
import random
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from selenium.webdriver.common.by import By

from scrapers.naukri_scraper import NaukriScraper
from scrapers.linkedin_scraper import LinkedInScraper
from filters.job_filter import JobFilter
from data.models import DatabaseManager
from core.smart_form_handler import SmartFormHandler
from utils.logger import get_logger, log_application_sent, log_application_failed, log_scraping_session
from config.enhanced_profile_config import (
    USER_PROFILE, 
    APPLICATION_CONFIG, 
    PLATFORM_CONFIG,
    JOB_FILTER_CONFIG
)

logger = get_logger('OptimizedJobApplicator')

class OptimizedJobApplicator:
    """Enhanced job applicator with smart form handling and single platform focus"""
    
    def __init__(self, preferred_platform: str = None):
        self.profile = USER_PROFILE
        self.config = APPLICATION_CONFIG
        self.platform_config = PLATFORM_CONFIG
        self.db = DatabaseManager()
        self.job_filter = JobFilter()
        
        # Smart platform selection
        self.current_platform = self._select_optimal_platform(preferred_platform)
        self.scraper = None
        self.form_handler = None
        
        # Enhanced tracking
        self.session_stats = {
            'jobs_found': 0,
            'jobs_filtered': 0,
            'applications_attempted': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'forms_handled': 0,
            'platform': self.current_platform,
            'start_time': datetime.now()
        }
        
        # Resume file path
        self.resume_path = os.getenv('RESUME_PATH', self._find_resume_file())
        
    def _select_optimal_platform(self, preferred: str = None) -> str:
        """Intelligently select the best platform for this session"""
        if preferred and preferred in self.platform_config:
            if self.platform_config[preferred]['enabled']:
                logger.info(f"Using preferred platform: {preferred}")
                return preferred
        
        # Get platform performance history
        platform_stats = self.db.get_platform_performance_stats()
        
        # Select based on priority and recent success rates
        available_platforms = [
            p for p, config in self.platform_config.items() 
            if config['enabled']
        ]
        
        if not available_platforms:
            raise ValueError("No platforms enabled")
        
        # Simple rotation if no preference
        if self.config.get('platform_rotation', True):
            last_platform = self.db.get_last_used_platform()
            for platform in available_platforms:
                if platform != last_platform:
                    logger.info(f"Rotating to platform: {platform}")
                    return platform
        
        # Default to highest priority platform
        best_platform = min(
            available_platforms, 
            key=lambda p: self.platform_config[p]['priority']
        )
        
        logger.info(f"Selected optimal platform: {best_platform}")
        return best_platform
    
    def _find_resume_file(self) -> Optional[str]:
        """Find resume file in common locations"""
        possible_paths = [
            "resume.pdf",
            "Resume.pdf", 
            "CV.pdf",
            "cv.pdf",
            os.path.expanduser("~/Downloads/resume.pdf"),
            os.path.expanduser("~/Documents/resume.pdf"),
            os.path.expanduser("~/Desktop/resume.pdf")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found resume at: {path}")
                return os.path.abspath(path)
        
        logger.warning("Resume file not found - applications may require manual intervention")
        return None
    
    def initialize(self) -> bool:
        """Initialize the selected platform scraper"""
        try:
            logger.info(f"Initializing {self.current_platform} scraper...")
            
            if self.current_platform == 'naukri':
                self.scraper = NaukriScraper()
            elif self.current_platform == 'linkedin':
                self.scraper = LinkedInScraper()
            else:
                logger.error(f"Unknown platform: {self.current_platform}")
                return False
            
            # Initialize scraper
            if not self.scraper.initialize():
                logger.error(f"Failed to initialize {self.current_platform} scraper")
                return False
            
            # Initialize smart form handler
            self.form_handler = SmartFormHandler(self.scraper.browser.driver)
            
            logger.info(f"{self.current_platform} scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing platform: {e}")
            return False
    
    def login(self) -> bool:
        """Login to the selected platform"""
        try:
            logger.info(f"Logging into {self.current_platform}...")
            
            success = self.scraper.login()
            
            if success:
                logger.info(f"Successfully logged into {self.current_platform}")
                # Record successful login
                self.db.record_platform_activity(self.current_platform, 'login_success')
            else:
                logger.error(f"Failed to login to {self.current_platform}")
                self.db.record_platform_activity(self.current_platform, 'login_failed')
            
            return success
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def run_optimized_session(self) -> Dict:
        """Run an optimized job hunting session"""
        session_id = self.db.start_scraping_session(self.current_platform)
        
        try:
            logger.info(f"Starting optimized job hunting session on {self.current_platform}")
            
            # Update application counts
            self._update_rate_limits()
            
            if self._should_skip_session():
                logger.info("Skipping session due to rate limits")
                return self._get_session_results()
            
            # Search for jobs with enhanced parameters
            jobs = self._enhanced_job_search()
            self.session_stats['jobs_found'] = len(jobs)
            
            if not jobs:
                logger.warning(f"No jobs found on {self.current_platform}")
                return self._get_session_results()
            
            # Apply intelligent filtering
            suitable_jobs = self._intelligent_job_filtering(jobs)
            self.session_stats['jobs_filtered'] = len(suitable_jobs)
            
            if not suitable_jobs:
                logger.info("No suitable jobs after filtering")
                return self._get_session_results()
            
            # Apply to jobs with smart form handling
            self._apply_to_jobs_intelligently(suitable_jobs)
            
            # Record session success
            self.db.record_platform_activity(self.current_platform, 'session_success')
            
            return self._get_session_results()
            
        except Exception as e:
            logger.error(f"Error in optimized session: {e}")
            self.db.record_platform_activity(self.current_platform, 'session_failed')
            return self._get_session_results()
        
        finally:
            # End session
            duration = (datetime.now() - self.session_stats['start_time']).total_seconds()
            self.db.end_scraping_session(session_id, {
                'jobs_found': self.session_stats['jobs_found'],
                'jobs_suitable': self.session_stats['jobs_filtered'],
                'applications_sent': self.session_stats['applications_successful'],
                'applications_failed': self.session_stats['applications_failed'],
                'success': self.session_stats['applications_successful'] > 0
            })
            
            log_scraping_session(
                self.current_platform,
                self.session_stats['jobs_found'],
                self.session_stats['applications_successful'],
                duration
            )
    
    def _enhanced_job_search(self) -> List[Dict]:
        """Enhanced job search with multiple strategies"""
        all_jobs = []
        
        try:
            search_params = self.platform_config[self.current_platform]['search_parameters']
            max_searches = 3  # Limit searches to avoid being flagged
            
            # Search with different combinations
            for i, location in enumerate(self.profile['preferred_locations'][:2]):
                for j, role in enumerate(self.profile['target_roles'][:2]):
                    if i + j >= max_searches:
                        break
                    
                    try:
                        logger.info(f"Searching for {role} in {location}")
                        
                        jobs = self.scraper.search_jobs(
                            location=location,
                            keywords=role,
                            experience=str(self.profile['total_experience_years'])
                        )
                        
                        if jobs:
                            all_jobs.extend(jobs)
                            logger.info(f"Found {len(jobs)} jobs for {role} in {location}")
                        
                        # Rate limiting between searches
                        delay = self.platform_config[self.current_platform]['rate_limit']
                        time.sleep(delay + random.uniform(1, 3))
                        
                    except Exception as e:
                        logger.warning(f"Error searching {role} in {location}: {e}")
                        continue
            
            # Remove duplicates
            unique_jobs = self._remove_duplicate_jobs(all_jobs)
            logger.info(f"Found {len(unique_jobs)} unique jobs after deduplication")
            
            return unique_jobs
            
        except Exception as e:
            logger.error(f"Error in enhanced job search: {e}")
            return []
    
    def _remove_duplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on URL and title+company"""
        seen_urls = set()
        seen_combinations = set()
        unique_jobs = []
        
        for job in jobs:
            job_url = job.get('job_url', '')
            job_combo = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            
            if job_url and job_url not in seen_urls:
                seen_urls.add(job_url)
                seen_combinations.add(job_combo)
                unique_jobs.append(job)
            elif job_combo not in seen_combinations:
                seen_combinations.add(job_combo)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _intelligent_job_filtering(self, jobs: List[Dict]) -> List[Dict]:
        """Apply intelligent filtering with enhanced criteria"""
        try:
            logger.info(f"Applying intelligent filtering to {len(jobs)} jobs")
            
            # Use enhanced job filter
            suitable_jobs = self.job_filter.filter_jobs(jobs)
            
            # Additional intelligent filtering
            filtered_jobs = []
            
            for job in suitable_jobs:
                # Skip if already applied
                if self.db.is_job_applied(job.get('job_url', '')):
                    continue
                
                # Enhanced scoring
                score = self._calculate_job_score(job)
                job['intelligence_score'] = score
                
                # Only include high-scoring jobs if quality_over_quantity is enabled
                if self.config.get('quality_over_quantity', True):
                    if score >= JOB_FILTER_CONFIG.get('minimum_match_score', 0.6):
                        filtered_jobs.append(job)
                else:
                    filtered_jobs.append(job)
            
            # Sort by score (highest first)
            filtered_jobs.sort(key=lambda x: x.get('intelligence_score', 0), reverse=True)
            
            # Limit based on platform configuration
            max_applications = self.platform_config[self.current_platform]['max_applications_per_session']
            filtered_jobs = filtered_jobs[:max_applications]
            
            logger.info(f"Selected {len(filtered_jobs)} high-quality jobs for application")
            return filtered_jobs
            
        except Exception as e:
            logger.error(f"Error in intelligent filtering: {e}")
            return jobs
    
    def _calculate_job_score(self, job: Dict) -> float:
        """Calculate intelligent job matching score"""
        score = 0.0
        
        try:
            title = job.get('title', '').lower()
            description = job.get('description', '').lower()
            company = job.get('company', '').lower()
            
            # Title matching (30% weight)
            for role in self.profile['target_roles']:
                if role.lower() in title:
                    score += 0.3
                    break
            
            # Skills matching (40% weight)
            skill_matches = 0
            for skill in self.profile['skills']:
                if skill.lower() in description or skill.lower() in title:
                    skill_matches += 1
            
            if self.profile['skills']:
                skill_score = min(skill_matches / len(self.profile['skills']) * 0.4, 0.4)
                score += skill_score
            
            # Experience matching (20% weight)
            experience_required = job.get('experience_required', '')
            if experience_required:
                # Parse experience requirement
                exp_numbers = [int(x) for x in re.findall(r'\d+', experience_required)]
                if exp_numbers:
                    min_exp = min(exp_numbers)
                    max_exp = max(exp_numbers) if len(exp_numbers) > 1 else min_exp
                    
                    user_exp = self.profile['total_experience_years']
                    if min_exp <= user_exp <= max_exp + 1:  # Allow 1 year flexibility
                        score += 0.2
            
            # Location preference (10% weight)
            location = job.get('location', '').lower()
            for pref_loc in self.profile['preferred_locations']:
                if pref_loc.lower() in location:
                    score += 0.1
                    break
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.warning(f"Error calculating job score: {e}")
            return 0.5  # Default score
    
    def _apply_to_jobs_intelligently(self, jobs: List[Dict]):
        """Apply to jobs with intelligent form handling"""
        for i, job in enumerate(jobs):
            try:
                # Check rate limits
                if self._should_stop_applications():
                    logger.info("Rate limit reached, stopping applications")
                    break
                
                logger.info(f"Applying to job {i+1}/{len(jobs)}: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                
                success = self._apply_to_single_job(job)
                
                if success:
                    self.session_stats['applications_successful'] += 1
                    log_application_sent(
                        job.get('title', 'Unknown'),
                        job.get('company', 'Unknown'),
                        self.current_platform
                    )
                else:
                    self.session_stats['applications_failed'] += 1
                    log_application_failed(
                        job.get('title', 'Unknown'),
                        job.get('company', 'Unknown'),
                        self.current_platform,
                        "Application failed"
                    )
                
                self.session_stats['applications_attempted'] += 1
                
                # Human-like delay between applications
                self._add_intelligent_delay()
                
            except Exception as e:
                logger.error(f"Error applying to job: {e}")
                self.session_stats['applications_failed'] += 1
                continue
    
    def _apply_to_single_job(self, job: Dict) -> bool:
        """Apply to a single job with smart form handling"""
        try:
            job_url = job.get('job_url')
            if not job_url:
                logger.warning("No job URL available")
                return False
            
            # Navigate to job page
            if not self.scraper.browser.navigate_to(job_url):
                logger.error("Failed to navigate to job page")
                return False
            
            # Get detailed job information
            job_details = self.scraper.get_job_details(job_url)
            if job_details:
                job.update(job_details)
            
            # Save job to database
            job_id = self._save_job_to_database(job)
            
            # Click apply button
            if not self._click_apply_button():
                logger.warning("Apply button not found or not clickable")
                return False
            
            # Handle file upload if required
            if self.resume_path:
                self.form_handler.handle_file_upload(self.resume_path)
            
            # Check for CAPTCHA
            if self.form_handler.detect_captcha():
                logger.warning("CAPTCHA detected - skipping this application")
                return False
            
            # Handle application form with smart form handler
            form_success = self.form_handler.handle_application_form()
            
            if form_success:
                self.session_stats['forms_handled'] += 1
                
                # Record successful application
                self._record_application(job_id, job, 'applied')
                return True
            else:
                logger.warning("Form handling failed")
                self._record_application(job_id, job, 'failed')
                return False
                
        except Exception as e:
            logger.error(f"Error in single job application: {e}")
            return False
    
    def _click_apply_button(self) -> bool:
        """Find and click the apply button"""
        try:
            apply_selectors = [
                "button[class*='apply']",
                "a[class*='apply']",
                "button:contains('Apply')",
                "a:contains('Apply')",
                ".apply-button",
                ".apply-btn",
                "#apply-button",
                "#apply-btn",
                "button[id*='apply']",
                "a[id*='apply']"
            ]
            
            for selector in apply_selectors:
                try:
                    apply_button = self.scraper.browser.wait_for_clickable(
                        By.CSS_SELECTOR, 
                        selector, 
                        timeout=5
                    )
                    
                    if apply_button:
                        # Scroll to button if needed
                        self.scraper.browser.driver.execute_script(
                            "arguments[0].scrollIntoView(true);", 
                            apply_button
                        )
                        time.sleep(1)
                        
                        # Click the button
                        self.scraper.browser.safe_click(apply_button)
                        time.sleep(2)
                        
                        logger.info("Apply button clicked successfully")
                        return True
                        
                except Exception:
                    continue
            
            logger.warning("No apply button found")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking apply button: {e}")
            return False
    
    def _save_job_to_database(self, job: Dict) -> int:
        """Save job details to database"""
        try:
            return self.db.add_job({
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'description': job.get('description', ''),
                'detailed_description': job.get('detailed_description', ''),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'experience_required': job.get('experience_required', ''),
                'job_url': job.get('job_url', ''),
                'platform': self.current_platform,
                'posted_date': job.get('posted_date'),
                'is_suitable': True,
                'suitability_score': job.get('intelligence_score', 0),
                'scraped_date': datetime.now()
            })
        except Exception as e:
            logger.error(f"Error saving job to database: {e}")
            return 0
    
    def _record_application(self, job_id: int, job: Dict, status: str):
        """Record application attempt in database"""
        try:
            self.db.add_application({
                'job_id': job_id,
                'job_title': job.get('title', ''),
                'company': job.get('company', ''),
                'platform': self.current_platform,
                'job_url': job.get('job_url', ''),
                'status': status,
                'application_method': 'smart_automated',
                'form_filled': status == 'applied',
                'resume_uploaded': bool(self.resume_path),
                'applied_date': datetime.now()
            })
        except Exception as e:
            logger.error(f"Error recording application: {e}")
    
    def _update_rate_limits(self):
        """Update current application counts for rate limiting"""
        try:
            # Get today's applications
            today_apps = self.db.get_applied_jobs(hours=24)
            self.applications_today = len(today_apps)
            
            # Get this hour's applications
            hour_apps = self.db.get_applied_jobs(hours=1)
            self.applications_this_hour = len(hour_apps)
            
            logger.info(f"Rate limits - Today: {self.applications_today}/{self.config['max_applications_per_day']}, "
                       f"This hour: {self.applications_this_hour}/{self.config['max_applications_per_hour']}")
            
        except Exception as e:
            logger.error(f"Error updating rate limits: {e}")
            self.applications_today = 0
            self.applications_this_hour = 0
    
    def _should_skip_session(self) -> bool:
        """Check if we should skip this session due to rate limits"""
        return (self.applications_today >= self.config['max_applications_per_day'] or
                self.applications_this_hour >= self.config['max_applications_per_hour'])
    
    def _should_stop_applications(self) -> bool:
        """Check if we should stop sending applications"""
        return (self.session_stats['applications_successful'] >= 
                self.platform_config[self.current_platform]['max_applications_per_session'] or
                self._should_skip_session())
    
    def _add_intelligent_delay(self):
        """Add intelligent delay between applications"""
        if self.config.get('human_like_behavior', True):
            # Longer delays to avoid detection
            base_delay = 45  # Base 45 seconds
            random_delay = random.uniform(15, 60)  # Additional 15-60 seconds
            total_delay = base_delay + random_delay
            
            logger.info(f"Waiting {total_delay:.1f} seconds before next application")
            time.sleep(total_delay)
    
    def _get_session_results(self) -> Dict:
        """Get comprehensive session results"""
        duration = (datetime.now() - self.session_stats['start_time']).total_seconds()
        
        return {
            'platform': self.current_platform,
            'duration_seconds': duration,
            'jobs_found': self.session_stats['jobs_found'],
            'jobs_filtered': self.session_stats['jobs_filtered'],
            'applications_attempted': self.session_stats['applications_attempted'],
            'applications_successful': self.session_stats['applications_successful'],
            'applications_failed': self.session_stats['applications_failed'],
            'forms_handled': self.session_stats['forms_handled'],
            'success_rate': (self.session_stats['applications_successful'] / 
                           max(self.session_stats['applications_attempted'], 1)) * 100,
            'resume_path': self.resume_path,
            'rate_limits': {
                'today': getattr(self, 'applications_today', 0),
                'hour': getattr(self, 'applications_this_hour', 0)
            }
        }
    
    def close(self):
        """Close all resources"""
        try:
            if self.scraper:
                self.scraper.close()
            
            if self.db:
                self.db.close()
            
            logger.info("Optimized job applicator closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing applicator: {e}")


class OptimizedJobSession:
    """Context manager for optimized job application sessions"""
    
    def __init__(self, platform: str = None):
        self.platform = platform
        self.applicator = None
        
    def __enter__(self):
        self.applicator = OptimizedJobApplicator(self.platform)
        
        if not self.applicator.initialize():
            raise RuntimeError(f"Failed to initialize {self.applicator.current_platform}")
        
        if not self.applicator.login():
            raise RuntimeError(f"Failed to login to {self.applicator.current_platform}")
        
        return self.applicator
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.applicator:
            self.applicator.close()
        
        if exc_type:
            logger.error(f"Session ended with error: {exc_val}")
        else:
            logger.info("Optimized job session completed successfully")