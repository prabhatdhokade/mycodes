#!/usr/bin/env python3
"""
Job Application Agent - Automated Job Search and Application System
Author: AI Assistant
Description: Automatically searches and applies to jobs on platforms like Naukri.com and LinkedIn
"""

import argparse
import sys
import os
import signal
import time
from datetime import datetime
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduler.job_scheduler import (
    start_job_scheduler, 
    stop_job_scheduler, 
    get_scheduler_status,
    run_job_session_now,
    JobSchedulerManager
)
from automation.job_applicator import JobApplicationSession
from utils.logger import get_logger, log_info
from config.profile_config import USER_PROFILE, APPLICATION_CONFIG

logger = get_logger('Main')

class JobApplicationAgent:
    def __init__(self):
        self.scheduler = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def start_scheduler(self):
        """Start the job application scheduler"""
        try:
            logger.info("Starting Job Application Agent Scheduler...")
            logger.info(f"Profile: {USER_PROFILE['name']} - {USER_PROFILE['email']}")
            logger.info(f"Target roles: {', '.join(USER_PROFILE['target_roles'][:3])}")
            logger.info(f"Preferred locations: {', '.join(USER_PROFILE['preferred_locations'][:3])}")
            
            self.scheduler = start_job_scheduler()
            self.running = True
            
            logger.info("Scheduler started successfully!")
            logger.info("The agent will now run automatically at scheduled intervals.")
            logger.info("Press Ctrl+C to stop the agent.")
            
            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(10)
                    
                    # Print status every 10 minutes
                    if int(time.time()) % 600 == 0:
                        self._print_status()
            
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                self.stop()
        
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            sys.exit(1)
    
    def run_single_session(self, platforms: Optional[list] = None):
        """Run a single job application session"""
        try:
            logger.info("Starting single job application session...")
            
            with JobApplicationSession(platforms=platforms) as applicator:
                results = applicator.search_and_apply_jobs(platforms=platforms)
                
                self._print_session_results(results)
                return results
        
        except Exception as e:
            logger.error(f"Error in single session: {e}")
            return None
    
    def get_status(self):
        """Get and display current status"""
        status = get_scheduler_status()
        self._print_status(status)
        return status
    
    def stop(self):
        """Stop the job application agent"""
        logger.info("Stopping Job Application Agent...")
        self.running = False
        
        if self.scheduler:
            stop_job_scheduler()
        
        logger.info("Job Application Agent stopped successfully")
    
    def _print_status(self, status: Optional[dict] = None):
        """Print current status"""
        if status is None:
            status = get_scheduler_status()
        
        print("\n" + "="*60)
        print("JOB APPLICATION AGENT STATUS")
        print("="*60)
        print(f"Running: {'Yes' if status.get('is_running') else 'No'}")
        print(f"Last Run: {status.get('last_run_time', 'Never')}")
        print(f"Next Run: {status.get('next_run_time', 'Not scheduled')}")
        print(f"Total Sessions: {status.get('run_count', 0)}")
        print(f"Total Applications: {status.get('total_applications', 0)}")
        
        today_stats = status.get('today_stats', {})
        print(f"\nToday's Statistics:")
        print(f"  Sessions: {today_stats.get('sessions', 0)}")
        print(f"  Jobs Found: {today_stats.get('jobs_found', 0)}")
        print(f"  Applications Sent: {today_stats.get('applications_sent', 0)}")
        print("="*60)
    
    def _print_session_results(self, results: dict):
        """Print session results"""
        print("\n" + "="*60)
        print("JOB APPLICATION SESSION RESULTS")
        print("="*60)
        print(f"Total Jobs Found: {results.get('total_jobs_found', 0)}")
        print(f"Suitable Jobs: {results.get('suitable_jobs', 0)}")
        print(f"Applications Sent: {results.get('applications_sent', 0)}")
        print(f"Applications Failed: {results.get('applications_failed', 0)}")
        
        platform_results = results.get('platform_results', {})
        if platform_results:
            print(f"\nPlatform Breakdown:")
            for platform, result in platform_results.items():
                print(f"  {platform.title()}:")
                print(f"    Jobs Found: {result.get('jobs_found', 0)}")
                print(f"    Applications: {result.get('applications_sent', 0)}")
        print("="*60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automated Job Application Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --start               # Start the scheduler
  python main.py --run-once            # Run a single session
  python main.py --run-once --platform naukri  # Run on specific platform
  python main.py --status              # Check status
  python main.py --stop                # Stop the scheduler
        """
    )
    
    parser.add_argument('--start', action='store_true',
                       help='Start the job application scheduler')
    
    parser.add_argument('--run-once', action='store_true',
                       help='Run a single job application session')
    
    parser.add_argument('--platform', choices=['naukri', 'linkedin'], 
                       action='append',
                       help='Specify platform(s) to use (can be used multiple times)')
    
    parser.add_argument('--status', action='store_true',
                       help='Show current status')
    
    parser.add_argument('--stop', action='store_true',
                       help='Stop the scheduler')
    
    parser.add_argument('--config', action='store_true',
                       help='Show current configuration')
    
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (no actual applications)')
    
    args = parser.parse_args()
    
    # Create agent instance
    agent = JobApplicationAgent()
    
    try:
        if args.config:
            print_configuration()
        
        elif args.status:
            agent.get_status()
        
        elif args.stop:
            stop_job_scheduler()
            print("Scheduler stopped successfully")
        
        elif args.run_once:
            platforms = args.platform if args.platform else None
            agent.run_single_session(platforms=platforms)
        
        elif args.start:
            agent.start_scheduler()
        
        else:
            # Interactive mode
            run_interactive_mode(agent)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        agent.stop()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

def print_configuration():
    """Print current configuration"""
    print("\n" + "="*60)
    print("JOB APPLICATION AGENT CONFIGURATION")
    print("="*60)
    print(f"Name: {USER_PROFILE['name']}")
    print(f"Email: {USER_PROFILE['email']}")
    print(f"Location: {USER_PROFILE['location']}")
    print(f"Experience: {USER_PROFILE['experience_years']} years")
    print(f"\nTarget Roles:")
    for role in USER_PROFILE['target_roles'][:5]:
        print(f"  - {role}")
    print(f"\nPreferred Locations:")
    for location in USER_PROFILE['preferred_locations'][:5]:
        print(f"  - {location}")
    print(f"\nKey Skills:")
    for skill in USER_PROFILE['skills'][:10]:
        print(f"  - {skill}")
    print(f"\nApplication Settings:")
    print(f"  Max per hour: {APPLICATION_CONFIG['max_applications_per_hour']}")
    print(f"  Max per day: {APPLICATION_CONFIG['max_applications_per_day']}")
    print(f"  Check interval: {APPLICATION_CONFIG['check_interval_hours']} hours")
    print("="*60)

def run_interactive_mode(agent: JobApplicationAgent):
    """Run in interactive mode"""
    print("\n" + "="*60)
    print("JOB APPLICATION AGENT - INTERACTIVE MODE")
    print("="*60)
    print("Welcome to the Job Application Agent!")
    print(f"Profile: {USER_PROFILE['name']}")
    print("\nAvailable commands:")
    print("1. Start scheduler")
    print("2. Run single session")
    print("3. Check status")
    print("4. Show configuration")
    print("5. Stop")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            
            elif choice == '1':
                print("Starting scheduler...")
                agent.start_scheduler()
                break
            
            elif choice == '2':
                platforms = []
                use_naukri = input("Include Naukri.com? (y/n): ").lower().startswith('y')
                use_linkedin = input("Include LinkedIn? (y/n): ").lower().startswith('y')
                
                if use_naukri:
                    platforms.append('naukri')
                if use_linkedin:
                    platforms.append('linkedin')
                
                if not platforms:
                    platforms = None  # Use all available
                
                agent.run_single_session(platforms=platforms)
            
            elif choice == '3':
                agent.get_status()
            
            elif choice == '4':
                print_configuration()
            
            elif choice == '5':
                agent.stop()
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()