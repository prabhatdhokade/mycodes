"""Alert management API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Alert, AlertStatus, AlertSeverity, AlertType
from app.schemas import AlertResponse, AlertAcknowledgeRequest, AlertCreateRequest
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[AlertStatus] = Query(None, description="Filter by alert status"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by alert severity"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type"),
    truck_id: Optional[int] = Query(None, description="Filter by truck ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of alerts to return"),
    offset: int = Query(0, ge=0, description="Number of alerts to skip"),
    db: Session = Depends(get_db)
):
    """Get all alerts with optional filtering."""
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if truck_id:
        query = query.filter(Alert.truck_id == truck_id)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
    
    return [AlertResponse.from_orm(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID."""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.from_orm(alert)


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    request: AlertAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert."""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status != AlertStatus.PENDING:
        raise HTTPException(status_code=400, detail="Alert is not pending")
    
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Alert acknowledged successfully", "alert_id": alert_id}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Resolve an alert."""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Alert resolved successfully", "alert_id": alert_id}


@router.get("/stats/summary")
async def get_alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics summary."""
    total_alerts = db.query(Alert).count()
    pending_alerts = db.query(Alert).filter(Alert.status == AlertStatus.PENDING).count()
    acknowledged_alerts = db.query(Alert).filter(Alert.status == AlertStatus.ACKNOWLEDGED).count()
    resolved_alerts = db.query(Alert).filter(Alert.status == AlertStatus.RESOLVED).count()
    
    # Alerts by severity
    critical_alerts = db.query(Alert).filter(Alert.severity == AlertSeverity.CRITICAL).count()
    high_alerts = db.query(Alert).filter(Alert.severity == AlertSeverity.HIGH).count()
    medium_alerts = db.query(Alert).filter(Alert.severity == AlertSeverity.MEDIUM).count()
    low_alerts = db.query(Alert).filter(Alert.severity == AlertSeverity.LOW).count()
    
    # Recent alerts (last 24 hours)
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_alerts = db.query(Alert).filter(Alert.created_at >= recent_cutoff).count()
    
    return {
        "total_alerts": total_alerts,
        "pending_alerts": pending_alerts,
        "acknowledged_alerts": acknowledged_alerts,
        "resolved_alerts": resolved_alerts,
        "severity_breakdown": {
            "critical": critical_alerts,
            "high": high_alerts,
            "medium": medium_alerts,
            "low": low_alerts
        },
        "recent_alerts_24h": recent_alerts
    }


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert (admin only)."""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully", "alert_id": alert_id}