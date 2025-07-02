import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from scrapers.naukri_scraper import NaukriScraper
from scrapers.linkedin_scraper import LinkedInScraper
from filters.job_filter import JobFilter
from data.models import DatabaseManager
from utils.logger import get_logger, log_application_sent, log_application_failed, log_scraping_session
from config.profile_config import USER_PROFILE, APPLICATION_CONFIG

logger = get_logger('JobApplicator')

class JobApplicator:
    def __init__(self):
        self.profile = USER_PROFILE
        self.config = APPLICATION_CONFIG
        self.db = DatabaseManager()
        self.job_filter = JobFilter()
        
        # Initialize scrapers
        self.scrapers = {}
        self.initialize_scrapers()
        
        # Application tracking
        self.applications_today = 0
        self.applications_this_hour = 0
        self.last_application_time = None
        
    def initialize_scrapers(self):
        """Initialize all platform scrapers"""
        try:
            # Initialize Naukri scraper
            naukri_scraper = NaukriScraper()
            if naukri_scraper.initialize():
                self.scrapers['naukri'] = naukri_scraper
                logger.info("Naukri scraper initialized successfully")
            else:
                logger.error("Failed to initialize Naukri scraper")
            
            # Initialize LinkedIn scraper
            linkedin_scraper = LinkedInScraper()
            if linkedin_scraper.initialize():
                self.scrapers['linkedin'] = linkedin_scraper
                logger.info("LinkedIn scraper initialized successfully")
            else:
                logger.error("Failed to initialize LinkedIn scraper")
                
        except Exception as e:
            logger.error(f"Error initializing scrapers: {e}")
    
    def login_to_platforms(self):
        """Login to all available platforms"""
        login_results = {}
        
        for platform, scraper in self.scrapers.items():
            try:
                logger.info(f"Attempting to login to {platform}")
                success = scraper.login()
                login_results[platform] = success
                
                if success:
                    logger.info(f"Successfully logged into {platform}")
                else:
                    logger.error(f"Failed to login to {platform}")
                    
            except Exception as e:
                logger.error(f"Error logging into {platform}: {e}")
                login_results[platform] = False
        
        return login_results
    
    def search_and_apply_jobs(self, platforms: List[str] = None) -> Dict:
        """Main method to search and apply to jobs"""
        if platforms is None:
            platforms = list(self.scrapers.keys())
        
        results = {
            'total_jobs_found': 0,
            'suitable_jobs': 0,
            'applications_sent': 0,
            'applications_failed': 0,
            'platform_results': {}
        }
        
        # Update application counts for today
        self._update_application_counts()
        
        for platform in platforms:
            if platform not in self.scrapers:
                logger.warning(f"Scraper for {platform} not available")
                continue
            
            platform_result = self._process_platform(platform)
            results['platform_results'][platform] = platform_result
            
            # Update totals
            results['total_jobs_found'] += platform_result.get('jobs_found', 0)
            results['suitable_jobs'] += platform_result.get('suitable_jobs', 0)
            results['applications_sent'] += platform_result.get('applications_sent', 0)
            results['applications_failed'] += platform_result.get('applications_failed', 0)
        
        logger.info(f"Session complete - Found: {results['total_jobs_found']}, "
                   f"Suitable: {results['suitable_jobs']}, "
                   f"Applied: {results['applications_sent']}")
        
        return results
    
    def _process_platform(self, platform: str) -> Dict:
        """Process jobs from a specific platform"""
        logger.info(f"Processing jobs from {platform}")
        
        scraper = self.scrapers[platform]
        session_id = self.db.start_scraping_session(platform)
        
        result = {
            'jobs_found': 0,
            'suitable_jobs': 0,
            'applications_sent': 0,
            'applications_failed': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            # Search for jobs
            jobs = self._search_jobs_on_platform(scraper, platform)
            result['jobs_found'] = len(jobs)
            
            if not jobs:
                logger.warning(f"No jobs found on {platform}")
                return result
            
            # Filter suitable jobs
            suitable_jobs = self.job_filter.filter_jobs(jobs)
            result['suitable_jobs'] = len(suitable_jobs)
            
            if not suitable_jobs:
                logger.info(f"No suitable jobs found on {platform}")
                return result
            
            # Apply to jobs
            for job in suitable_jobs:
                if self._should_stop_applications():
                    logger.info("Application limit reached, stopping")
                    break
                
                if self._apply_to_job(scraper, job, platform):
                    result['applications_sent'] += 1
                else:
                    result['applications_failed'] += 1
                
                # Add delay between applications
                self._add_application_delay()
            
        except Exception as e:
            logger.error(f"Error processing {platform}: {e}")
            result['errors'].append(str(e))
        
        finally:
            # End scraping session
            duration = time.time() - start_time
            self.db.end_scraping_session(session_id, {
                'jobs_found': result['jobs_found'],
                'jobs_suitable': result['suitable_jobs'],
                'applications_sent': result['applications_sent'],
                'errors_encountered': len(result['errors']),
                'success': len(result['errors']) == 0
            })
            
            log_scraping_session(platform, result['jobs_found'], 
                               result['applications_sent'], duration)
        
        return result
    
    def _search_jobs_on_platform(self, scraper, platform: str) -> List[Dict]:
        """Search for jobs on a specific platform"""
        try:
            # Search with different location/keyword combinations
            all_jobs = []
            
            # Primary search with preferred locations
            for location in self.profile['preferred_locations'][:3]:  # Try top 3 locations
                for role in self.profile['target_roles'][:2]:  # Try top 2 roles
                    try:
                        jobs = scraper.search_jobs(location=location, keywords=role)
                        if jobs:
                            all_jobs.extend(jobs)
                            logger.info(f"Found {len(jobs)} jobs for {role} in {location}")
                        
                        # Add delay between searches
                        time.sleep(random.uniform(2, 5))
                        
                    except Exception as e:
                        logger.warning(f"Error searching {role} in {location}: {e}")
                        continue
            
            # Remove duplicates based on job URL
            unique_jobs = []
            seen_urls = set()
            
            for job in all_jobs:
                job_url = job.get('job_url', '')
                if job_url and job_url not in seen_urls:
                    seen_urls.add(job_url)
                    unique_jobs.append(job)
            
            logger.info(f"Found {len(unique_jobs)} unique jobs on {platform}")
            return unique_jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs on {platform}: {e}")
            return []
    
    def _apply_to_job(self, scraper, job: Dict, platform: str) -> bool:
        """Apply to a specific job"""
        job_url = job.get('job_url')
        job_title = job.get('title', 'Unknown')
        company = job.get('company', 'Unknown')
        
        if not job_url:
            logger.warning(f"No URL for job: {job_title} at {company}")
            return False
        
        # Check if already applied
        if self.db.is_job_applied(job_url):
            logger.info(f"Already applied to: {job_title} at {company}")
            return False
        
        try:
            logger.info(f"Applying to: {job_title} at {company}")
            
            # Get detailed job description if needed
            job_details = scraper.get_job_details(job_url)
            if job_details:
                job.update(job_details)
            
            # Save job to database
            job_id = self.db.add_job({
                'title': job_title,
                'company': company,
                'location': job.get('location'),
                'description': job.get('description', ''),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'experience_required': job.get('experience_required'),
                'job_url': job_url,
                'platform': platform,
                'posted_date': job.get('posted_date'),
                'is_suitable': True,
                'suitability_score': job.get('suitability_score', 0)
            })
            
            # Apply to the job
            application_success = scraper.apply_to_job(job_url)
            
            # Record application attempt
            application_data = {
                'job_id': job_id,
                'job_title': job_title,
                'company': company,
                'platform': platform,
                'job_url': job_url,
                'status': 'applied' if application_success else 'failed',
                'application_method': 'automated'
            }
            
            self.db.add_application(application_data)
            
            if application_success:
                log_application_sent(job_title, company, platform)
                self.applications_today += 1
                self.applications_this_hour += 1
                self.last_application_time = datetime.now()
                return True
            else:
                log_application_failed(job_title, company, platform, "Application failed")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to job {job_title} at {company}: {e}")
            log_application_failed(job_title, company, platform, str(e))
            return False
    
    def _should_stop_applications(self) -> bool:
        """Check if we should stop sending applications"""
        # Check daily limit
        if self.applications_today >= self.config.get('max_applications_per_day', 50):
            logger.info(f"Daily application limit reached: {self.applications_today}")
            return True
        
        # Check hourly limit
        if self.applications_this_hour >= self.config.get('max_applications_per_hour', 10):
            logger.info(f"Hourly application limit reached: {self.applications_this_hour}")
            return True
        
        return False
    
    def _add_application_delay(self):
        """Add delay between applications to avoid being flagged"""
        delay = random.uniform(30, 90)  # 30-90 seconds between applications
        logger.info(f"Waiting {delay:.1f} seconds before next application")
        time.sleep(delay)
    
    def _update_application_counts(self):
        """Update application counts for rate limiting"""
        try:
            # Get applications from today
            today_applications = self.db.get_applied_jobs(hours=24)
            self.applications_today = len(today_applications)
            
            # Get applications from this hour
            hour_applications = self.db.get_applied_jobs(hours=1)
            self.applications_this_hour = len(hour_applications)
            
            logger.info(f"Applications today: {self.applications_today}, "
                       f"this hour: {self.applications_this_hour}")
            
        except Exception as e:
            logger.error(f"Error updating application counts: {e}")
    
    def get_application_statistics(self) -> Dict:
        """Get application statistics"""
        try:
            stats = self.db.get_application_stats(days=7)
            stats['applications_today'] = self.applications_today
            stats['applications_this_hour'] = self.applications_this_hour
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close all scrapers and database connections"""
        logger.info("Closing job applicator")
        
        for platform, scraper in self.scrapers.items():
            try:
                scraper.close()
                logger.info(f"Closed {platform} scraper")
            except Exception as e:
                logger.error(f"Error closing {platform} scraper: {e}")
        
        try:
            self.db.close()
            logger.info("Closed database connection")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

class JobApplicationSession:
    """Context manager for job application sessions"""
    
    def __init__(self, platforms: List[str] = None):
        self.platforms = platforms
        self.applicator = None
        
    def __enter__(self):
        self.applicator = JobApplicator()
        
        # Login to platforms
        login_results = self.applicator.login_to_platforms()
        
        # Remove platforms that failed to login
        if self.platforms:
            self.platforms = [p for p in self.platforms if login_results.get(p, False)]
        
        return self.applicator
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.applicator:
            self.applicator.close()
        
        if exc_type:
            logger.error(f"Session ended with error: {exc_val}")
        else:
            logger.info("Job application session completed successfully")