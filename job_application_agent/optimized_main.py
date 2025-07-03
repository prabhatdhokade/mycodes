#!/usr/bin/env python3
"""
Optimized Job Application Agent - Smart Job Hunter with Dynamic Form Handling
Enhanced version with single platform focus, intelligent form filling, and advanced automation
Author: AI Assistant
"""

import argparse
import sys
import os
import signal
import time
from datetime import datetime
from typing import Optional, Dict

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduler.job_scheduler import (
    start_job_scheduler, 
    stop_job_scheduler, 
    get_scheduler_status,
    run_job_session_now,
    JobSchedulerManager
)
from automation.optimized_job_applicator import OptimizedJobSession
from utils.logger import get_logger, log_info
from config.enhanced_profile_config import (
    USER_PROFILE, 
    APPLICATION_CONFIG,
    PLATFORM_CONFIG,
    SMART_FORM_ANSWERS
)

logger = get_logger('OptimizedMain')

class OptimizedJobApplicationAgent:
    """Enhanced job application agent with smart form handling and platform optimization"""
    
    def __init__(self):
        self.scheduler = None
        self.running = False
        self.preferred_platform = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def set_platform_preference(self, platform: str):
        """Set preferred platform for this session"""
        if platform in PLATFORM_CONFIG:
            self.preferred_platform = platform
            logger.info(f"Platform preference set to: {platform}")
        else:
            logger.warning(f"Invalid platform: {platform}")
    
    def start_intelligent_hunting(self):
        """Start the intelligent job hunting scheduler"""
        try:
            logger.info("🎯 Starting Optimized Job Application Agent...")
            self._print_hunter_profile()
            
            self.scheduler = start_job_scheduler()
            self.running = True
            
            logger.info("✅ Intelligent job hunter started successfully!")
            logger.info("🤖 Your AI assistant is now actively hunting for opportunities...")
            logger.info("⚡ Features enabled: Smart form filling, Dynamic question answering")
            logger.info("🛡️ Safety: Rate limiting, Human-like behavior, Account protection")
            logger.info("📊 Press Ctrl+C to stop and view statistics.")
            
            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(10)
                    
                    # Print status every 15 minutes
                    if int(time.time()) % 900 == 0:
                        self._print_intelligent_status()
            
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                self.stop()
        
        except Exception as e:
            logger.error(f"Error starting intelligent hunting: {e}")
            sys.exit(1)
    
    def run_single_hunt(self, platform: str = None) -> Dict:
        """Run a single intelligent hunting session"""
        try:
            target_platform = platform or self.preferred_platform
            
            if target_platform:
                logger.info(f"🎯 Starting single hunt on {target_platform.title()}...")
            else:
                logger.info("🎯 Starting single hunt with intelligent platform selection...")
            
            with OptimizedJobSession(platform=target_platform) as applicator:
                results = applicator.run_optimized_session()
                
                self._print_hunt_results(results)
                return results
        
        except Exception as e:
            logger.error(f"Error in single hunt session: {e}")
            return {}
    
    def get_hunter_status(self):
        """Get and display intelligent hunter status"""
        status = get_scheduler_status()
        self._print_intelligent_status(status)
        return status
    
    def pause_hunting(self):
        """Pause the hunting scheduler"""
        logger.info("⏸️ Pausing intelligent job hunting...")
        self.running = False
        
        if self.scheduler:
            stop_job_scheduler()
        
        logger.info("⏸️ Job hunting paused successfully")
    
    def stop(self):
        """Stop the job application agent"""
        logger.info("🛑 Stopping Optimized Job Application Agent...")
        self.running = False
        
        if self.scheduler:
            stop_job_scheduler()
        
        logger.info("🛑 Job hunting stopped successfully")
    
    def _print_hunter_profile(self):
        """Print hunter profile information"""
        print("\n" + "="*70)
        print("🎯 OPTIMIZED JOB HUNTER - PROFILE ACTIVE")
        print("="*70)
        print(f"👤 Hunter: {USER_PROFILE['name']}")
        print(f"📧 Contact: {USER_PROFILE['email']}")
        print(f"🎯 Experience: {USER_PROFILE['total_experience_years']} years")
        print(f"💼 Current CTC: {USER_PROFILE['current_ctc']} LPA")
        print(f"💰 Expected CTC: {USER_PROFILE['expected_ctc']} LPA")
        print(f"📅 Available from: {USER_PROFILE['last_working_day']}")
        
        print(f"\n🎯 Target Roles:")
        for role in USER_PROFILE['target_roles'][:4]:
            print(f"   • {role}")
        
        print(f"\n📍 Hunting Zones:")
        for location in USER_PROFILE['preferred_locations'][:5]:
            print(f"   • {location}")
        
        print(f"\n🛠️ Core Skills:")
        skills_display = ', '.join(USER_PROFILE['skills'][:8])
        print(f"   {skills_display}")
        
        print(f"\n⚡ Intelligence Features:")
        print(f"   • Smart Form Handling: {APPLICATION_CONFIG.get('auto_fill_forms', True)}")
        print(f"   • Dynamic Questions: {APPLICATION_CONFIG.get('smart_question_detection', True)}")
        print(f"   • Single Platform Focus: {APPLICATION_CONFIG.get('single_platform_mode', True)}")
        print(f"   • Human-like Behavior: {APPLICATION_CONFIG.get('human_like_behavior', True)}")
        print(f"   • Quality Over Quantity: {APPLICATION_CONFIG.get('quality_over_quantity', True)}")
        
        print(f"\n🛡️ Safety Limits:")
        print(f"   • Max per hour: {APPLICATION_CONFIG['max_applications_per_hour']}")
        print(f"   • Max per day: {APPLICATION_CONFIG['max_applications_per_day']}")
        print("="*70)
    
    def _print_intelligent_status(self, status: Optional[Dict] = None):
        """Print intelligent hunter status"""
        if status is None:
            status = get_scheduler_status()
        
        print("\n" + "="*70)
        print("🤖 INTELLIGENT JOB HUNTER STATUS")
        print("="*70)
        
        is_running = status.get('is_running', False)
        print(f"🔄 Hunting Status: {'🟢 ACTIVE' if is_running else '🔴 INACTIVE'}")
        print(f"⏰ Last Hunt: {status.get('last_run_time', 'Never')}")
        print(f"📅 Next Hunt: {status.get('next_run_time', 'Not scheduled')}")
        print(f"📊 Total Sessions: {status.get('run_count', 0)}")
        print(f"🎯 Total Applications: {status.get('total_applications', 0)}")
        
        today_stats = status.get('today_stats', {})
        print(f"\n📈 Today's Hunting Results:")
        print(f"   🔍 Sessions: {today_stats.get('sessions', 0)}")
        print(f"   💼 Jobs Found: {today_stats.get('jobs_found', 0)}")
        print(f"   📝 Applications Sent: {today_stats.get('applications_sent', 0)}")
        print(f"   🎯 Success Rate: {self._calculate_success_rate(today_stats)}%")
        
        # Platform status
        print(f"\n🌐 Platform Status:")
        for platform, config in PLATFORM_CONFIG.items():
            status_emoji = "🟢" if config['enabled'] else "🔴"
            priority = config['priority']
            print(f"   {status_emoji} {platform.title()}: Priority {priority}")
        
        print("="*70)
    
    def _print_hunt_results(self, results: Dict):
        """Print hunting session results"""
        print("\n" + "="*70)
        print("🎯 INTELLIGENT HUNTING SESSION RESULTS")
        print("="*70)
        
        platform = results.get('platform', 'Unknown').title()
        duration = results.get('duration_seconds', 0)
        
        print(f"🌐 Platform: {platform}")
        print(f"⏱️ Duration: {duration/60:.1f} minutes")
        print(f"🔍 Jobs Found: {results.get('jobs_found', 0)}")
        print(f"🎯 Jobs Filtered: {results.get('jobs_filtered', 0)}")
        print(f"📝 Applications Attempted: {results.get('applications_attempted', 0)}")
        print(f"✅ Applications Successful: {results.get('applications_successful', 0)}")
        print(f"❌ Applications Failed: {results.get('applications_failed', 0)}")
        print(f"🤖 Forms Handled: {results.get('forms_handled', 0)}")
        print(f"📊 Success Rate: {results.get('success_rate', 0):.1f}%")
        
        rate_limits = results.get('rate_limits', {})
        print(f"\n🛡️ Rate Limit Status:")
        print(f"   Today: {rate_limits.get('today', 0)}/{APPLICATION_CONFIG['max_applications_per_day']}")
        print(f"   This Hour: {rate_limits.get('hour', 0)}/{APPLICATION_CONFIG['max_applications_per_hour']}")
        
        if results.get('resume_path'):
            print(f"\n📄 Resume: {os.path.basename(results.get('resume_path'))}")
        
        print("="*70)
    
    def _calculate_success_rate(self, stats: Dict) -> float:
        """Calculate success rate from stats"""
        applications = stats.get('applications_sent', 0)
        sessions = stats.get('sessions', 0)
        
        if sessions > 0:
            return (applications / sessions) * 100
        return 0.0

def main():
    """Main entry point for optimized job hunter"""
    parser = argparse.ArgumentParser(
        description="🎯 Optimized Job Application Agent - Smart Job Hunter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 ENHANCED FEATURES:
  • Smart Form Handling: Automatically detects and fills dynamic questions
  • Intelligent Platform Selection: Focuses on one platform per session
  • Dynamic Question Answering: Handles experience, salary, notice period questions
  • Human-like Behavior: Anti-detection with natural delays and patterns
  • Quality Over Quantity: AI-powered job matching and filtering

🎯 EXAMPLES:
  python optimized_main.py --hunt                    # Start intelligent hunting
  python optimized_main.py --hunt-once               # Single hunting session  
  python optimized_main.py --hunt-once --platform naukri   # Hunt on specific platform
  python optimized_main.py --status                  # Check hunter status
  python optimized_main.py --profile                 # Show hunter profile
  python optimized_main.py --pause                   # Pause hunting
  python optimized_main.py --diagnose                # System diagnostics

🤖 SMART ANSWERS:
  The system automatically answers questions like:
  • Years of Python experience: 3.5 years
  • Current CTC: 7 LPA  
  • Expected CTC: 15 LPA
  • Last working day: End of July 2024
  • Notice period: 1 Month
  • Preferred location: Pune, Mumbai, Bangalore
        """
    )
    
    # Core hunting commands
    parser.add_argument('--hunt', action='store_true',
                       help='🎯 Start intelligent job hunting (optimized scheduler)')
    
    parser.add_argument('--hunt-once', action='store_true',
                       help='🔍 Run single hunting session with smart form handling')
    
    parser.add_argument('--platform', choices=['naukri', 'linkedin'], 
                       help='🌐 Specify platform for focused hunting (naukri or linkedin)')
    
    # Status and monitoring
    parser.add_argument('--status', action='store_true',
                       help='📊 Show intelligent hunter status and statistics')
    
    parser.add_argument('--profile', action='store_true',
                       help='👤 Show hunter profile and configuration')
    
    # Control commands
    parser.add_argument('--pause', action='store_true',
                       help='⏸️ Pause the hunting scheduler')
    
    parser.add_argument('--stop', action='store_true',
                       help='🛑 Stop the hunting scheduler')
    
    # Diagnostics and testing
    parser.add_argument('--diagnose', action='store_true',
                       help='🔧 Run system diagnostics and troubleshooting')
    
    parser.add_argument('--test-forms', action='store_true',
                       help='🧪 Test smart form handling capabilities')
    
    # Legacy support (hidden from help)
    parser.add_argument('--start', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--run-once', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--config', action='store_true', help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    # Create optimized agent instance
    agent = OptimizedJobApplicationAgent()
    
    try:
        # Handle platform preference
        if args.platform:
            agent.set_platform_preference(args.platform)
        
        # Command routing
        if args.profile or args.config:
            print_hunter_profile()
        
        elif args.status:
            agent.get_hunter_status()
        
        elif args.pause:
            agent.pause_hunting()
        
        elif args.stop:
            stop_job_scheduler()
            print("🛑 Hunting scheduler stopped successfully")
        
        elif args.diagnose:
            from utils.diagnostics import main as run_diagnostics
            run_diagnostics()
        
        elif args.test_forms:
            print("🧪 Testing smart form handling capabilities...")
            test_smart_form_answers()
        
        elif args.hunt_once or args.run_once:
            results = agent.run_single_hunt(args.platform)
            if results.get('applications_successful', 0) > 0:
                print(f"\n🎉 Successfully applied to {results['applications_successful']} positions!")
            elif results.get('jobs_found', 0) == 0:
                print("\n🔍 No suitable positions found this time. Try again later!")
            else:
                print("\n⚠️ Found positions but applications encountered issues. Check logs for details.")
        
        elif args.hunt or args.start:
            agent.start_intelligent_hunting()
        
        else:
            # Interactive mode
            run_interactive_hunting_mode(agent)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        agent.stop()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")
        print("💡 Try running with --diagnose to troubleshoot issues")
        sys.exit(1)

def print_hunter_profile():
    """Print the hunter profile configuration"""
    agent = OptimizedJobApplicationAgent()
    agent._print_hunter_profile()

def test_smart_form_answers():
    """Test and display smart form answers"""
    print("\n" + "="*70)
    print("🧪 SMART FORM ANSWERS - TEST MODE")
    print("="*70)
    
    print("📝 Sample Questions and Automatic Answers:")
    
    sample_questions = [
        ("Years of Python experience?", SMART_FORM_ANSWERS.get('python_experience')),
        ("Current CTC?", SMART_FORM_ANSWERS.get('current_ctc')),
        ("Expected salary?", SMART_FORM_ANSWERS.get('expected_ctc')),
        ("Notice period?", SMART_FORM_ANSWERS.get('notice_period')),
        ("Last working day?", SMART_FORM_ANSWERS.get('last_working_day')),
        ("Preferred location?", SMART_FORM_ANSWERS.get('preferred_location')),
        ("Total experience?", SMART_FORM_ANSWERS.get('total_experience')),
        ("Remote work?", SMART_FORM_ANSWERS.get('remote_work')),
        ("Immediate joiner?", SMART_FORM_ANSWERS.get('immediate_joiner')),
        ("Highest qualification?", SMART_FORM_ANSWERS.get('highest_qualification'))
    ]
    
    for question, answer in sample_questions:
        print(f"   ❓ {question:<25} ➜ {answer}")
    
    print(f"\n🔧 Pattern Recognition: {len(SMART_FORM_ANSWERS)} predefined answers")
    print(f"🤖 Skill Experience: {len(USER_PROFILE.get('skill_experience', {}))} technologies mapped")
    print("="*70)

def run_interactive_hunting_mode(agent: OptimizedJobApplicationAgent):
    """Run in interactive hunting mode"""
    print("\n" + "="*70)
    print("🎯 OPTIMIZED JOB HUNTER - INTERACTIVE MODE")
    print("="*70)
    print("Welcome to your intelligent job hunting assistant!")
    print(f"Profile: {USER_PROFILE['name']} - {USER_PROFILE['total_experience_years']} years experience")
    
    print("\n🚀 Available Commands:")
    print("1. 🎯 Start intelligent hunting (automated)")
    print("2. 🔍 Run single hunt session")
    print("3. 📊 Check hunter status")
    print("4. 👤 Show hunter profile")
    print("5. 🌐 Select platform (Naukri/LinkedIn)")
    print("6. ⏸️ Pause hunting")
    print("0. 🚪 Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == '0':
                print("🎯 Happy hunting! Your AI assistant is ready when you need it.")
                break
            
            elif choice == '1':
                print("🎯 Starting intelligent hunting...")
                agent.start_intelligent_hunting()
                break
            
            elif choice == '2':
                platform_choice = input("Select platform (1: Naukri, 2: LinkedIn, Enter: Auto): ").strip()
                
                platform = None
                if platform_choice == '1':
                    platform = 'naukri'
                elif platform_choice == '2':
                    platform = 'linkedin'
                
                results = agent.run_single_hunt(platform)
                
                if results.get('applications_successful', 0) > 0:
                    print(f"\n🎉 Great! Applied to {results['applications_successful']} positions successfully!")
                
            elif choice == '3':
                agent.get_hunter_status()
            
            elif choice == '4':
                print_hunter_profile()
            
            elif choice == '5':
                print("\n🌐 Platform Selection:")
                print("1. Naukri.com (Priority 1)")
                print("2. LinkedIn (Priority 2)")
                print("3. Auto-select")
                
                platform_choice = input("Choose platform (1-3): ").strip()
                
                if platform_choice == '1':
                    agent.set_platform_preference('naukri')
                elif platform_choice == '2':
                    agent.set_platform_preference('linkedin')
                else:
                    agent.preferred_platform = None
                    print("🤖 Platform set to auto-selection")
            
            elif choice == '6':
                agent.pause_hunting()
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n🚪 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()