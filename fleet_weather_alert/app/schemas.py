"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models import AlertStatus, AlertSeverity, AlertType, OperatorPreference, TruckStatus


class AlertResponse(BaseModel):
    """Alert response schema."""
    alert_id: int
    truck_id: int
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    status: AlertStatus
    location_lat: float
    location_lng: float
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    weather_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AlertAcknowledgeRequest(BaseModel):
    """Alert acknowledgment request schema."""
    operator_notes: Optional[str] = Field(None, description="Optional notes from operator")


class AlertCreateRequest(BaseModel):
    """Alert creation request schema."""
    truck_id: int
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    location_lat: float
    location_lng: float
    weather_data: Optional[Dict[str, Any]] = None


class TruckResponse(BaseModel):
    """Truck response schema."""
    truck_id: int
    operator_id: int
    license_plate: str
    location_lat: float
    location_lng: float
    status: TruckStatus
    last_maintenance_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OperatorResponse(BaseModel):
    """Operator response schema."""
    operator_id: int
    name: str
    contact_info: str
    alert_preference: OperatorPreference
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FleetSummary(BaseModel):
    """Fleet summary schema."""
    total_trucks: int
    active_trucks: int
    maintenance_trucks: int
    inactive_trucks: int
    emergency_trucks: int
    total_operators: int


class WeatherDataResponse(BaseModel):
    """Weather data response schema."""
    location_lat: float
    location_lng: float
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    wind_direction: float
    visibility: float
    weather_condition: str
    weather_description: str
    timestamp: datetime


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: datetime
    version: str
    database_status: str
    weather_service_status: str