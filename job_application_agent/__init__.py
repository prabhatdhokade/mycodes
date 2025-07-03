"""
Job Application Agent - Automated Job Search and Application System

A comprehensive Python package for automatically searching and applying to jobs
on various platforms like Naukri.com and LinkedIn.

Author: AI Assistant
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "Automated Job Application Agent"

from .main import JobApplicationAgent
from .scheduler.job_scheduler import start_job_scheduler, stop_job_scheduler, get_scheduler_status
from .automation.job_applicator import JobApplicationSession

__all__ = [
    'JobApplicationAgent',
    'start_job_scheduler',
    'stop_job_scheduler', 
    'get_scheduler_status',
    'JobApplicationSession'
]