import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, List
import os
from dotenv import load_dotenv

from automation.job_applicator import JobApplicationSession
from utils.logger import get_logger
from config.profile_config import APPLICATION_CONFIG

load_dotenv()
logger = get_logger('JobScheduler')

class JobApplicationScheduler:
    def __init__(self):
        self.config = APPLICATION_CONFIG
        self.is_running = False
        self.scheduler_thread = None
        self.last_run_time = None
        self.next_run_time = None
        self.run_count = 0
        self.total_applications = 0
        
        # Statistics
        self.session_stats = []
        
        # Setup schedule
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup the job application schedule"""
        interval_hours = self.config.get('check_interval_hours', 1)
        
        # Schedule job every N hours
        schedule.every(interval_hours).hours.do(self._run_job_application_session)
        
        # Also schedule at specific times if configured
        preferred_times = ['09:00', '14:00', '18:00']  # Morning, afternoon, evening
        
        for time_str in preferred_times:
            schedule.every().day.at(time_str).do(self._run_job_application_session)
        
        logger.info(f"Scheduled job application every {interval_hours} hours and at {preferred_times}")
        
        # Calculate next run time
        self._update_next_run_time()
    
    def _run_job_application_session(self):
        """Run a single job application session"""
        try:
            logger.info("Starting scheduled job application session")
            self.last_run_time = datetime.now()
            self.run_count += 1
            
            # Check if we should run based on daily limits
            if not self._should_run_session():
                logger.info("Skipping session due to daily limits")
                return
            
            # Run the job application session
            with JobApplicationSession() as applicator:
                results = applicator.search_and_apply_jobs()
                
                # Store session statistics
                session_stat = {
                    'timestamp': self.last_run_time,
                    'run_number': self.run_count,
                    'results': results
                }
                self.session_stats.append(session_stat)
                
                # Update total applications
                self.total_applications += results.get('applications_sent', 0)
                
                # Log session summary
                logger.info(f"Session {self.run_count} completed - "
                          f"Found: {results['total_jobs_found']}, "
                          f"Applied: {results['applications_sent']}")
                
                # Cleanup old statistics (keep last 50 sessions)
                if len(self.session_stats) > 50:
                    self.session_stats = self.session_stats[-50:]
            
        except Exception as e:
            logger.error(f"Error in scheduled job application session: {e}")
        
        finally:
            self._update_next_run_time()
    
    def _should_run_session(self) -> bool:
        """Check if we should run a session based on limits and conditions"""
        # Check if it's within working hours (9 AM to 9 PM)
        current_hour = datetime.now().hour
        if current_hour < 9 or current_hour > 21:
            logger.info(f"Outside working hours ({current_hour}:00), skipping session")
            return False
        
        # Check if it's a weekend (optional skip)
        if datetime.now().weekday() >= 5:  # Saturday = 5, Sunday = 6
            weekend_skip = os.getenv('SKIP_WEEKENDS', 'false').lower() == 'true'
            if weekend_skip:
                logger.info("Skipping weekend session")
                return False
        
        # Check daily application limits
        today_sessions = [s for s in self.session_stats 
                         if s['timestamp'].date() == datetime.now().date()]
        
        today_applications = sum(s['results'].get('applications_sent', 0) 
                               for s in today_sessions)
        
        max_daily = self.config.get('max_applications_per_day', 50)
        if today_applications >= max_daily:
            logger.info(f"Daily application limit reached: {today_applications}/{max_daily}")
            return False
        
        return True
    
    def _update_next_run_time(self):
        """Update the next scheduled run time"""
        try:
            self.next_run_time = schedule.next_run()
        except Exception:
            # If no jobs scheduled, set next run to next hour
            self.next_run_time = datetime.now() + timedelta(hours=1)
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Job application scheduler started")
        logger.info(f"Next run scheduled for: {self.next_run_time}")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.info("Stopping job application scheduler...")
            # The thread will stop on its own as it checks is_running
        
        schedule.clear()
        logger.info("Job application scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Scheduler thread started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue after error
        
        logger.info("Scheduler thread stopped")
    
    def run_now(self):
        """Run a job application session immediately"""
        logger.info("Running job application session immediately")
        threading.Thread(target=self._run_job_application_session, daemon=True).start()
    
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        status = {
            'is_running': self.is_running,
            'last_run_time': self.last_run_time,
            'next_run_time': self.next_run_time,
            'run_count': self.run_count,
            'total_applications': self.total_applications,
            'recent_sessions': self.session_stats[-5:] if self.session_stats else []
        }
        
        # Add today's statistics
        today_sessions = [s for s in self.session_stats 
                         if s['timestamp'].date() == datetime.now().date()]
        
        status['today_stats'] = {
            'sessions': len(today_sessions),
            'applications_sent': sum(s['results'].get('applications_sent', 0) 
                                   for s in today_sessions),
            'jobs_found': sum(s['results'].get('total_jobs_found', 0) 
                            for s in today_sessions)
        }
        
        return status
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict:
        """Get summary for a specific date"""
        if date is None:
            date = datetime.now().date()
        else:
            date = date.date() if isinstance(date, datetime) else date
        
        day_sessions = [s for s in self.session_stats 
                       if s['timestamp'].date() == date]
        
        summary = {
            'date': date.isoformat(),
            'total_sessions': len(day_sessions),
            'total_jobs_found': sum(s['results'].get('total_jobs_found', 0) 
                                  for s in day_sessions),
            'total_suitable_jobs': sum(s['results'].get('suitable_jobs', 0) 
                                     for s in day_sessions),
            'total_applications_sent': sum(s['results'].get('applications_sent', 0) 
                                         for s in day_sessions),
            'total_applications_failed': sum(s['results'].get('applications_failed', 0) 
                                           for s in day_sessions),
            'platform_breakdown': {}
        }
        
        # Calculate platform breakdown
        for session in day_sessions:
            platform_results = session['results'].get('platform_results', {})
            for platform, results in platform_results.items():
                if platform not in summary['platform_breakdown']:
                    summary['platform_breakdown'][platform] = {
                        'jobs_found': 0,
                        'applications_sent': 0,
                        'applications_failed': 0
                    }
                
                summary['platform_breakdown'][platform]['jobs_found'] += results.get('jobs_found', 0)
                summary['platform_breakdown'][platform]['applications_sent'] += results.get('applications_sent', 0)
                summary['platform_breakdown'][platform]['applications_failed'] += results.get('applications_failed', 0)
        
        return summary
    
    def add_custom_schedule(self, schedule_func: Callable, description: str = ""):
        """Add a custom schedule function"""
        try:
            schedule_func()
            logger.info(f"Added custom schedule: {description}")
        except Exception as e:
            logger.error(f"Error adding custom schedule: {e}")
    
    def reschedule(self, interval_hours: int):
        """Reschedule with a different interval"""
        schedule.clear()
        self.config['check_interval_hours'] = interval_hours
        self.setup_schedule()
        logger.info(f"Rescheduled with {interval_hours} hour interval")

class JobSchedulerManager:
    """Singleton manager for the job scheduler"""
    
    _instance = None
    _scheduler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_scheduler(cls) -> JobApplicationScheduler:
        """Get the global scheduler instance"""
        if cls._scheduler is None:
            cls._scheduler = JobApplicationScheduler()
        return cls._scheduler
    
    @classmethod
    def start_scheduler(cls):
        """Start the global scheduler"""
        scheduler = cls.get_scheduler()
        scheduler.start()
        return scheduler
    
    @classmethod
    def stop_scheduler(cls):
        """Stop the global scheduler"""
        if cls._scheduler:
            cls._scheduler.stop()
    
    @classmethod
    def get_status(cls) -> Dict:
        """Get scheduler status"""
        if cls._scheduler:
            return cls._scheduler.get_status()
        return {'is_running': False, 'message': 'Scheduler not initialized'}

# Convenience functions
def start_job_scheduler():
    """Start the job application scheduler"""
    return JobSchedulerManager.start_scheduler()

def stop_job_scheduler():
    """Stop the job application scheduler"""
    JobSchedulerManager.stop_scheduler()

def get_scheduler_status():
    """Get current scheduler status"""
    return JobSchedulerManager.get_status()

def run_job_session_now():
    """Run a job application session immediately"""
    scheduler = JobSchedulerManager.get_scheduler()
    scheduler.run_now()