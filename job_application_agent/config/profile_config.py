# Profile Configuration based on Resume
USER_PROFILE = {
    "name": "Prabhat Dhokade",
    "email": "prabhatdhokade@gmail.com",
    "phone": "+91 8275813838",
    "location": "Pune, Maharashtra",
    "linkedin": "LinkedIn",  # Add your LinkedIn URL
    
    # Job Preferences
    "preferred_locations": [
        "Pune", "Mumbai", "Bangalore", "Hyderabad", "Delhi", "Gurgaon", 
        "Noida", "Chennai", "Kolkata", "Ahmedabad", "Remote", "Work from Home"
    ],
    
    "target_roles": [
        "Python Developer", "Software Engineer", "Software Developer",
        "Backend Developer", "Full Stack Developer", "Data Engineer",
        "Cloud Engineer", "DevOps Engineer", "Senior Software Engineer"
    ],
    
    "skills": [
        "Python", "C++", "C", "Flask", "Streamlit", "MySQL", "Snowflake", 
        "PostgreSQL", "Salesforce", "S3", "DynamoDB", "Azure", "AWS", 
        "EC2", "Lambda", "SQS", "RabbitMQ", "Git", "MLflow", "Docker", 
        "Matillion", "SonarQube", "Linux", "OpenCV", "scikit-learn", "Pillow"
    ],
    
    "experience_years": 2,  # Based on 2022-Present
    
    # Education
    "education": {
        "degree": "Bachelor of Engineering in Information Technology",
        "college": "JSPM Rajarshi Shahu College Of Engineering, Tathawade",
        "cgpa": "8.78",
        "graduation_year": "2022"
    },
    
    # Keywords to avoid in job descriptions
    "avoid_keywords": [
        "manual testing", "sales", "marketing", "cold calling", 
        "business development", "non-technical"
    ],
    
    # Minimum salary expectation (in LPA)
    "min_salary_lpa": 3,
    "max_salary_lpa": 15,
    
    # Company preferences
    "preferred_company_types": [
        "Product", "Service", "Startup", "MNC", "IT Services"
    ]
}

# Platform Configurations
PLATFORM_CONFIG = {
    "naukri": {
        "base_url": "https://www.naukri.com",
        "search_url": "https://www.naukri.com/jobs-in-{location}",
        "login_required": True,
        "rate_limit": 2  # seconds between requests
    },
    
    "linkedin": {
        "base_url": "https://www.linkedin.com",
        "jobs_url": "https://www.linkedin.com/jobs/search/",
        "login_required": True,
        "rate_limit": 3  # seconds between requests
    },
    
    "indeed": {
        "base_url": "https://www.indeed.co.in",
        "search_url": "https://www.indeed.co.in/jobs",
        "login_required": False,
        "rate_limit": 2
    }
}

# Application Settings
APPLICATION_CONFIG = {
    "max_applications_per_hour": 10,
    "max_applications_per_day": 50,
    "check_interval_hours": 1,
    "retry_failed_applications": True,
    "save_job_descriptions": True,
    "screenshot_applications": True
}

# Browser Settings
BROWSER_CONFIG = {
    "headless": False,  # Set to True for background operation
    "window_size": (1920, 1080),
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "implicit_wait": 10,
    "page_load_timeout": 30
}