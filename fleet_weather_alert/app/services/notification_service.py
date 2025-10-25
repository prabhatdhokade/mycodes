"""Notification service for sending alerts to operators."""

import logging
import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Alert, Operator, OperatorPreference
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications to operators."""
    
    def __init__(self, db: Session):
        self.db = db
        self.twilio_client = None
        self.sendgrid_client = None
        
        # Initialize Twilio if configured
        if settings.twilio_account_sid and settings.twilio_auth_token:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                logger.info("Twilio client initialized")
            except ImportError:
                logger.warning("Twilio not installed, SMS notifications disabled")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
        
        # Initialize SendGrid if configured
        if settings.sendgrid_api_key:
            try:
                import sendgrid
                from sendgrid.helpers.mail import Mail
                self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
                logger.info("SendGrid client initialized")
            except ImportError:
                logger.warning("SendGrid not installed, email notifications disabled")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid: {e}")
    
    def send_alert_notification(self, alert: Alert) -> bool:
        """Send notification for a specific alert."""
        try:
            truck = alert.truck
            operator = truck.operator
            
            if not operator:
                logger.error(f"No operator found for truck {truck.truck_id}")
                return False
            
            # Determine notification methods based on operator preference
            methods = self._get_notification_methods(operator.alert_preference)
            
            success = True
            for method in methods:
                if method == "sms":
                    success &= self._send_sms(operator, alert)
                elif method == "email":
                    success &= self._send_email(operator, alert)
                elif method == "dashboard":
                    # Dashboard notifications are handled by the API
                    logger.info(f"Dashboard notification queued for operator {operator.operator_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
            return False
    
    def _get_notification_methods(self, preference: OperatorPreference) -> List[str]:
        """Get notification methods based on operator preference."""
        if preference == OperatorPreference.ALL:
            return ["sms", "email", "dashboard"]
        elif preference == OperatorPreference.SMS:
            return ["sms", "dashboard"]
        elif preference == OperatorPreference.EMAIL:
            return ["email", "dashboard"]
        else:
            return ["dashboard"]
    
    def _send_sms(self, operator: Operator, alert: Alert) -> bool:
        """Send SMS notification."""
        if not self.twilio_client:
            logger.info(f"SMS simulation for {operator.name}: {alert.message}")
            return True
        
        try:
            message = self.twilio_client.messages.create(
                body=f"WEATHER ALERT: {alert.message}",
                from_=settings.twilio_phone_number,  # You'd need to add this to config
                to=operator.contact_info
            )
            logger.info(f"SMS sent to {operator.name}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {operator.name}: {e}")
            return False
    
    def _send_email(self, operator: Operator, alert: Alert) -> bool:
        """Send email notification."""
        if not self.sendgrid_client:
            logger.info(f"Email simulation for {operator.name}: {alert.message}")
            return True
        
        try:
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            subject = f"Weather Alert - {alert.alert_type.value.upper()}"
            content = self._generate_email_content(operator, alert)
            
            mail = Mail(
                from_email=settings.from_email,
                to_emails=operator.contact_info,
                subject=subject,
                plain_text_content=content
            )
            
            response = self.sendgrid_client.send(mail)
            logger.info(f"Email sent to {operator.name}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {operator.name}: {e}")
            return False
    
    def _generate_email_content(self, operator: Operator, alert: Alert) -> str:
        """Generate email content for alert notification."""
        truck = alert.truck
        
        content = f"""
Dear {operator.name},

A weather alert has been triggered for your assigned truck.

ALERT DETAILS:
- Alert Type: {alert.alert_type.value.upper()}
- Severity: {alert.severity.value.upper()}
- Message: {alert.message}
- Truck ID: {truck.truck_id}
- License Plate: {truck.license_plate}
- Location: {alert.location_lat}, {alert.location_lng}
- Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Please acknowledge this alert through the fleet management dashboard or contact dispatch immediately.

Stay safe!

Fleet Weather Alert System
        """
        return content.strip()
    
    def process_pending_alerts(self) -> int:
        """Process all pending alerts and send notifications."""
        processed = 0
        
        try:
            # Get all pending alerts
            pending_alerts = self.db.query(Alert).filter(Alert.status == "pending").all()
            
            for alert in pending_alerts:
                if self.send_alert_notification(alert):
                    processed += 1
                    logger.info(f"Processed alert {alert.alert_id} for truck {alert.truck_id}")
            
            logger.info(f"Processed {processed} pending alerts")
            
        except Exception as e:
            logger.error(f"Error processing pending alerts: {e}")
        
        return processed