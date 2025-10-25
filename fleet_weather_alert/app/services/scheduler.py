"""Scheduler service for periodic weather monitoring and alert processing."""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.weather_service import WeatherService
from app.services.notification_service import NotificationService
from app.config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler with all configured jobs."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Add weather monitoring job
            self.scheduler.add_job(
                func=self._weather_monitoring_job,
                trigger=IntervalTrigger(seconds=settings.weather_poll_interval),
                id='weather_monitoring',
                name='Weather Monitoring Job',
                replace_existing=True
            )
            
            # Add notification processing job (every 2 minutes)
            self.scheduler.add_job(
                func=self._notification_processing_job,
                trigger=IntervalTrigger(seconds=120),
                id='notification_processing',
                name='Notification Processing Job',
                replace_existing=True
            )
            
            # Add cleanup job (daily at 2 AM)
            self.scheduler.add_job(
                func=self._cleanup_job,
                trigger=CronTrigger(hour=2, minute=0),
                id='cleanup',
                name='Daily Cleanup Job',
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("Scheduler started successfully")
            logger.info(f"Weather monitoring interval: {settings.weather_poll_interval} seconds")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def _weather_monitoring_job(self):
        """Job to monitor weather conditions for all trucks."""
        logger.info("Starting weather monitoring job...")
        
        db = SessionLocal()
        try:
            weather_service = WeatherService(db)
            alerts_created = weather_service.check_fleet_weather()
            
            if alerts_created > 0:
                logger.info(f"Weather monitoring job completed - {alerts_created} alerts created")
            else:
                logger.debug("Weather monitoring job completed - no new alerts")
                
        except Exception as e:
            logger.error(f"Weather monitoring job failed: {e}")
        finally:
            db.close()
    
    def _notification_processing_job(self):
        """Job to process pending notifications."""
        logger.debug("Starting notification processing job...")
        
        db = SessionLocal()
        try:
            notification_service = NotificationService(db)
            processed = notification_service.process_pending_alerts()
            
            if processed > 0:
                logger.info(f"Notification processing job completed - {processed} notifications sent")
            else:
                logger.debug("Notification processing job completed - no pending notifications")
                
        except Exception as e:
            logger.error(f"Notification processing job failed: {e}")
        finally:
            db.close()
    
    def _cleanup_job(self):
        """Job to clean up old data."""
        logger.info("Starting daily cleanup job...")
        
        db = SessionLocal()
        try:
            from app.models import WeatherCache, Alert
            from datetime import datetime, timedelta
            
            # Clean up expired weather cache
            expired_cache = db.query(WeatherCache).filter(
                WeatherCache.expires_at < datetime.utcnow()
            ).delete()
            
            # Clean up old resolved alerts (older than 30 days)
            old_alerts = db.query(Alert).filter(
                Alert.status == "resolved",
                Alert.resolved_at < datetime.utcnow() - timedelta(days=30)
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleanup job completed - removed {expired_cache} cache entries and {old_alerts} old alerts")
            
        except Exception as e:
            logger.error(f"Cleanup job failed: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_job_status(self):
        """Get status of all scheduled jobs."""
        if not self.is_running:
            return {"status": "stopped", "jobs": []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": jobs
        }