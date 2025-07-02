from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    salary_min = Column(Float)
    salary_max = Column(Float)
    experience_required = Column(String(50))
    job_url = Column(String(500), unique=True)
    platform = Column(String(50))  # naukri, linkedin, indeed
    posted_date = Column(DateTime)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    is_suitable = Column(Boolean, default=False)
    suitability_score = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', platform='{self.platform}')>"

class Application(Base):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer)  # Foreign key to Job
    job_title = Column(String(255))
    company = Column(String(255))
    platform = Column(String(50))
    job_url = Column(String(500))
    application_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='applied')  # applied, rejected, interview, hired
    cover_letter_used = Column(Text)
    resume_version = Column(String(100))
    application_method = Column(String(50))  # automated, manual
    response_received = Column(Boolean, default=False)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Application(job_title='{self.job_title}', company='{self.company}', status='{self.status}')>"

class ApplicationLog(Base):
    __tablename__ = 'application_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    platform = Column(String(50))
    action = Column(String(100))  # scrape_started, application_sent, error_occurred
    details = Column(Text)
    job_url = Column(String(500))
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<ApplicationLog(action='{self.action}', platform='{self.platform}', success={self.success})>"

class ScrapingSession(Base):
    __tablename__ = 'scraping_sessions'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    jobs_found = Column(Integer, default=0)
    jobs_suitable = Column(Integer, default=0)
    applications_sent = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    session_notes = Column(Text)
    
    def __repr__(self):
        return f"<ScrapingSession(platform='{self.platform}', jobs_found={self.jobs_found}, applications_sent={self.applications_sent})>"

class DatabaseManager:
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///job_applications.db')
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_job(self, job_data):
        """Add a new job to the database"""
        job = Job(**job_data)
        try:
            self.session.add(job)
            self.session.commit()
            return job.id
        except Exception as e:
            self.session.rollback()
            print(f"Error adding job: {e}")
            return None
    
    def add_application(self, application_data):
        """Add a new application to the database"""
        application = Application(**application_data)
        try:
            self.session.add(application)
            self.session.commit()
            return application.id
        except Exception as e:
            self.session.rollback()
            print(f"Error adding application: {e}")
            return None
    
    def add_log(self, log_data):
        """Add a log entry"""
        log = ApplicationLog(**log_data)
        try:
            self.session.add(log)
            self.session.commit()
            return log.id
        except Exception as e:
            self.session.rollback()
            print(f"Error adding log: {e}")
            return None
    
    def start_scraping_session(self, platform):
        """Start a new scraping session"""
        session = ScrapingSession(platform=platform)
        try:
            self.session.add(session)
            self.session.commit()
            return session.id
        except Exception as e:
            self.session.rollback()
            print(f"Error starting session: {e}")
            return None
    
    def end_scraping_session(self, session_id, session_data):
        """End a scraping session with results"""
        try:
            session = self.session.query(ScrapingSession).filter_by(id=session_id).first()
            if session:
                session.end_time = datetime.utcnow()
                for key, value in session_data.items():
                    setattr(session, key, value)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error ending session: {e}")
    
    def get_applied_jobs(self, hours=24):
        """Get jobs applied to in the last N hours"""
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return self.session.query(Application).filter(
            Application.application_date >= cutoff_time
        ).all()
    
    def is_job_applied(self, job_url):
        """Check if we've already applied to this job"""
        return self.session.query(Application).filter_by(job_url=job_url).first() is not None
    
    def get_application_stats(self, days=7):
        """Get application statistics for the last N days"""
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        total_applications = self.session.query(Application).filter(
            Application.application_date >= cutoff_time
        ).count()
        
        responses = self.session.query(Application).filter(
            Application.application_date >= cutoff_time,
            Application.response_received == True
        ).count()
        
        return {
            'total_applications': total_applications,
            'responses_received': responses,
            'response_rate': (responses / total_applications * 100) if total_applications > 0 else 0
        }
    
    def close(self):
        """Close the database session"""
        self.session.close()