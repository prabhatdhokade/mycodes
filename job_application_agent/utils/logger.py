import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class JobApplicationLogger:
    def __init__(self, log_level="INFO", log_dir="logs"):
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup main logger
        self.logger = logging.getLogger('JobApplicationAgent')
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for general logs
        general_log_file = os.path.join(self.log_dir, 'job_agent.log')
        file_handler = RotatingFileHandler(
            general_log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error log file
        error_log_file = os.path.join(self.log_dir, 'errors.log')
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Application log file
        app_log_file = os.path.join(self.log_dir, 'applications.log')
        app_handler = RotatingFileHandler(
            app_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(formatter)
        
        # Create application-specific logger
        self.app_logger = logging.getLogger('Applications')
        self.app_logger.setLevel(logging.INFO)
        self.app_logger.addHandler(app_handler)
        self.app_logger.addHandler(console_handler)
    
    def get_logger(self, name=None):
        """Get a logger instance"""
        if name:
            return logging.getLogger(f'JobApplicationAgent.{name}')
        return self.logger
    
    def get_application_logger(self):
        """Get the application-specific logger"""
        return self.app_logger
    
    def log_job_found(self, job_title, company, platform, url):
        """Log when a new job is found"""
        self.logger.info(f"Job found: {job_title} at {company} on {platform} - {url}")
    
    def log_application_sent(self, job_title, company, platform):
        """Log when an application is sent"""
        self.app_logger.info(f"Application sent: {job_title} at {company} via {platform}")
    
    def log_application_failed(self, job_title, company, platform, error):
        """Log when an application fails"""
        self.app_logger.error(f"Application failed: {job_title} at {company} via {platform} - Error: {error}")
    
    def log_scraping_session(self, platform, jobs_found, applications_sent, duration):
        """Log scraping session summary"""
        self.logger.info(
            f"Scraping session completed - Platform: {platform}, "
            f"Jobs found: {jobs_found}, Applications sent: {applications_sent}, "
            f"Duration: {duration:.2f} seconds"
        )
    
    def log_rate_limit(self, platform, delay):
        """Log rate limiting events"""
        self.logger.warning(f"Rate limit applied for {platform}, waiting {delay} seconds")
    
    def log_login_status(self, platform, success):
        """Log login attempts"""
        status = "successful" if success else "failed"
        self.logger.info(f"Login to {platform} {status}")
    
    def log_browser_action(self, action, details=""):
        """Log browser actions"""
        self.logger.debug(f"Browser action: {action} {details}")
    
    def log_error(self, error_msg, exception=None):
        """Log errors with optional exception details"""
        if exception:
            self.logger.error(f"{error_msg} - Exception: {str(exception)}", exc_info=True)
        else:
            self.logger.error(error_msg)
    
    def log_warning(self, warning_msg):
        """Log warnings"""
        self.logger.warning(warning_msg)
    
    def log_info(self, info_msg):
        """Log information"""
        self.logger.info(info_msg)
    
    def log_debug(self, debug_msg):
        """Log debug information"""
        self.logger.debug(debug_msg)

# Create global logger instance
job_logger = JobApplicationLogger()

# Convenience functions
def get_logger(name=None):
    return job_logger.get_logger(name)

def get_application_logger():
    return job_logger.get_application_logger()

def log_job_found(job_title, company, platform, url):
    job_logger.log_job_found(job_title, company, platform, url)

def log_application_sent(job_title, company, platform):
    job_logger.log_application_sent(job_title, company, platform)

def log_application_failed(job_title, company, platform, error):
    job_logger.log_application_failed(job_title, company, platform, error)

def log_scraping_session(platform, jobs_found, applications_sent, duration):
    job_logger.log_scraping_session(platform, jobs_found, applications_sent, duration)

def log_error(error_msg, exception=None):
    job_logger.log_error(error_msg, exception)

def log_warning(warning_msg):
    job_logger.log_warning(warning_msg)

def log_info(info_msg):
    job_logger.log_info(info_msg)

def log_debug(debug_msg):
    job_logger.log_debug(debug_msg)