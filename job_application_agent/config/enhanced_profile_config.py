# Enhanced Profile Configuration with Smart Question Handling
# Optimized for Automated Job Applications with Dynamic Form Support

USER_PROFILE = {
    "name": "Prabhat Dhokade",
    "email": "prabhatdhokade@gmail.com",
    "phone": "+91 8275813838",
    "location": "Pune, Maharashtra",
    "linkedin": "https://linkedin.com/in/prabhatdhokade",
    
    # Professional Details
    "current_designation": "Software Engineer",
    "total_experience_years": 2.5,
    "relevant_experience_years": 2.5,
    "notice_period": "1 Month",
    "last_working_day": "End of July 2024",
    "current_ctc": 7.0,  # In LPA
    "expected_ctc": 15.0,  # In LPA
    "preferred_work_mode": "Hybrid",  # Remote, Hybrid, Office
    "immediate_joiner": False,
    
    # Skill-specific Experience (in years)
    "skill_experience": {
        "Python": 3.5,
        "Flask": 2.0,
        "Streamlit": 1.5,
        "AWS": 2.0,
        "MySQL": 2.5,
        "PostgreSQL": 1.5,
        "C++": 3.0,
        "Git": 2.5,
        "Docker": 1.0,
        "Linux": 2.0,
        "Machine Learning": 1.0,
        "Data Analysis": 1.5,
        "REST API": 2.0,
        "Microservices": 1.0
    },
    
    # Job Preferences
    "preferred_locations": [
        "Pune", "Mumbai", "Bangalore", "Hyderabad", "Remote", 
        "Work from Home", "Delhi", "Gurgaon", "Noida", "Chennai"
    ],
    
    "target_roles": [
        "Python Developer", "Software Engineer", "Backend Developer",
        "Software Developer", "Full Stack Developer", "Senior Software Engineer",
        "Python Software Engineer", "Application Developer"
    ],
    
    "skills": [
        "Python", "C++", "Flask", "Streamlit", "MySQL", "PostgreSQL", 
        "AWS", "EC2", "Lambda", "S3", "DynamoDB", "Git", "Docker", 
        "Linux", "REST API", "Microservices", "Data Analysis"
    ],
    
    # Education Details
    "education": {
        "highest_qualification": "Bachelor of Engineering",
        "degree": "B.E. in Information Technology",
        "college": "JSPM Rajarshi Shahu College Of Engineering",
        "university": "Pune University",
        "graduation_year": "2022",
        "cgpa": "8.78",
        "percentage": "87.8%"
    },
    
    # Work Authorization
    "work_authorization": {
        "indian_citizen": True,
        "require_visa_sponsorship": False,
        "authorized_to_work_in_india": True,
        "require_relocation_assistance": False
    }
}

# Smart Form Question Mapping
# This maps common form questions to appropriate answers
SMART_FORM_ANSWERS = {
    # Experience Questions
    "total_experience": "2.5",
    "relevant_experience": "2.5", 
    "years_of_experience": "2.5",
    "experience_years": "2.5",
    "work_experience": "2.5",
    "professional_experience": "2.5",
    
    # Technology-specific Experience
    "python_experience": "3.5",
    "python_years": "3.5",
    "experience_in_python": "3.5",
    "flask_experience": "2.0",
    "aws_experience": "2.0",
    "mysql_experience": "2.5",
    "cpp_experience": "3.0",
    "c++_experience": "3.0",
    "git_experience": "2.5",
    "linux_experience": "2.0",
    
    # Current Job Details
    "current_ctc": "7",
    "current_salary": "7",
    "present_ctc": "7",
    "current_package": "7 LPA",
    "last_drawn_salary": "7",
    
    # Expected Salary
    "expected_ctc": "15",
    "expected_salary": "15",
    "salary_expectation": "15",
    "expected_package": "15 LPA",
    "desired_salary": "15",
    
    # Notice Period
    "notice_period": "1 Month",
    "current_notice_period": "1 Month",
    "serving_notice_period": "No",
    "notice_period_days": "30",
    "notice_period_months": "1",
    "last_working_day": "End of July 2024",
    "last_date_of_employment": "End of July 2024",
    "relieving_date": "End of July 2024",
    
    # Location Preferences
    "preferred_location": "Pune",
    "work_location": "Pune",
    "willing_to_relocate": "Yes",
    "open_to_relocation": "Yes",
    "preferred_work_location": "Pune, Mumbai, Bangalore",
    
    # Work Mode
    "work_from_home": "Yes",
    "remote_work": "Yes", 
    "work_mode": "Hybrid",
    "preferred_work_mode": "Hybrid",
    "open_to_remote_work": "Yes",
    
    # Immediate Joining
    "immediate_joiner": "No",
    "can_join_immediately": "No",
    "earliest_joining_date": "End of July 2024",
    "when_can_you_join": "After July 2024",
    
    # Education
    "highest_qualification": "Bachelor of Engineering",
    "education_level": "Graduate",
    "degree": "B.E. Information Technology",
    "graduation_year": "2022",
    "college_name": "JSPM Rajarshi Shahu College Of Engineering",
    "university": "Pune University",
    "cgpa": "8.78",
    "percentage": "87.8",
    
    # Work Authorization
    "indian_citizen": "Yes",
    "work_authorization": "Yes",
    "visa_sponsorship_required": "No",
    "authorized_to_work": "Yes",
    "require_sponsorship": "No",
    
    # Other Common Questions
    "gender": "Male",
    "marital_status": "Single",
    "date_of_birth": "1999-01-01",  # Generic DOB
    "age": "25",
    "languages_known": "English, Hindi, Marathi",
    "cover_letter": "I am excited to apply for this position as it aligns perfectly with my skills in Python development and my career goals.",
    
    # Technical Proficiency
    "python_proficiency": "Expert",
    "database_skills": "MySQL, PostgreSQL",
    "cloud_experience": "AWS",
    "framework_experience": "Flask, Streamlit",
    "version_control": "Git",
    "operating_system": "Linux, Windows"
}

# Question Pattern Recognition
# Regex patterns to identify common form questions
QUESTION_PATTERNS = {
    # Experience patterns
    r".*(?:total|overall|years?.*of|work).*experience.*": "total_experience",
    r".*python.*(?:experience|years?).*": "python_experience", 
    r".*(?:relevant|related).*experience.*": "relevant_experience",
    r".*(?:c\+\+|cpp).*(?:experience|years?).*": "cpp_experience",
    r".*(?:aws|cloud).*(?:experience|years?).*": "aws_experience",
    r".*(?:mysql|database).*(?:experience|years?).*": "mysql_experience",
    
    # Salary patterns
    r".*(?:current|present).*(?:ctc|salary|package).*": "current_ctc",
    r".*(?:expected|desired).*(?:ctc|salary|package).*": "expected_ctc",
    r".*last.*drawn.*salary.*": "current_ctc",
    
    # Notice period patterns
    r".*notice.*period.*": "notice_period",
    r".*last.*working.*day.*": "last_working_day",
    r".*(?:serving|current).*notice.*": "serving_notice_period",
    r".*(?:earliest|when.*can).*join.*": "earliest_joining_date",
    
    # Location patterns
    r".*(?:preferred|work).*location.*": "preferred_location", 
    r".*(?:willing|open).*relocat.*": "willing_to_relocate",
    r".*(?:remote|work.*from.*home|wfh).*": "work_from_home",
    
    # Education patterns
    r".*(?:highest|education).*qualification.*": "highest_qualification",
    r".*graduation.*year.*": "graduation_year",
    r".*(?:cgpa|gpa|grade).*": "cgpa",
    r".*percentage.*": "percentage",
    
    # Authorization patterns
    r".*(?:visa|sponsorship).*(?:required|need).*": "visa_sponsorship_required",
    r".*(?:authorized|eligible).*work.*": "work_authorization",
    r".*indian.*citizen.*": "indian_citizen"
}

# Platform-specific Configuration
PLATFORM_CONFIG = {
    "naukri": {
        "base_url": "https://www.naukri.com",
        "enabled": True,
        "priority": 1,
        "rate_limit": 2,
        "max_applications_per_session": 15,
        "search_parameters": {
            "experience": "2-4",
            "salary": "5-15",
            "job_type": "full-time"
        }
    },
    
    "linkedin": {
        "base_url": "https://www.linkedin.com",
        "enabled": True, 
        "priority": 2,
        "rate_limit": 3,
        "max_applications_per_session": 10,
        "search_parameters": {
            "experience_level": "mid-level",
            "job_type": "full-time",
            "remote": "hybrid"
        }
    }
}

# Enhanced Application Settings
APPLICATION_CONFIG = {
    "max_applications_per_hour": 12,
    "max_applications_per_day": 40,
    "check_interval_hours": 1,
    "retry_failed_applications": True,
    "save_job_descriptions": True,
    "screenshot_applications": True,
    
    # Smart form handling
    "auto_fill_forms": True,
    "smart_question_detection": True,
    "form_submission_delay": (2, 5),  # seconds
    "typing_speed": (0.1, 0.3),  # seconds per character
    
    # Application strategy
    "single_platform_mode": True,  # Focus on one platform per session
    "platform_rotation": True,  # Rotate between platforms
    "quality_over_quantity": True,  # Prioritize job match quality
    
    # Safety settings
    "human_like_behavior": True,
    "random_delays": True,
    "mouse_movements": True,
    "anti_detection": True
}

# Browser Configuration  
BROWSER_CONFIG = {
    "headless": False,
    "window_size": (1920, 1080),
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "script_timeout": 30,
    
    # Anti-detection features
    "disable_images": False,
    "disable_javascript": False,
    "disable_plugins": False,
    "disable_extensions": True,
    "disable_dev_shm_usage": True,
    "no_sandbox": True
}

# Job Filtering Configuration
JOB_FILTER_CONFIG = {
    "min_salary_lpa": 5,
    "max_salary_lpa": 25,
    "required_keywords": ["python", "software", "developer", "engineer"],
    "avoid_keywords": ["manual testing", "sales", "marketing", "cold calling"],
    "max_experience_required": 5,
    "preferred_company_types": ["Product", "Service", "Startup", "MNC"],
    "minimum_match_score": 0.6,
    
    # Smart filtering
    "ai_powered_matching": True,
    "description_analysis": True,
    "requirement_matching": True,
    "company_research": False  # Can be enabled for deeper analysis
}