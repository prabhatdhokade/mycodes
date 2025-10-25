"""Database models for the Fleet Weather Alert System."""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class AlertStatus(str, enum.Enum):
    """Alert status enumeration."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertSeverity(str, enum.Enum):
    """Alert severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, enum.Enum):
    """Alert type enumeration."""
    HEAVY_RAIN = "heavy_rain"
    STORM = "storm"
    FOG = "fog"
    HIGH_WIND = "high_wind"
    EXTREME_TEMP = "extreme_temp"
    CYCLONE = "cyclone"


class OperatorPreference(str, enum.Enum):
    """Operator notification preference."""
    SMS = "sms"
    EMAIL = "email"
    DASHBOARD = "dashboard"
    ALL = "all"


class TruckStatus(str, enum.Enum):
    """Truck status enumeration."""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    EMERGENCY = "emergency"


class Operator(Base):
    """Operator model representing truck drivers."""
    __tablename__ = "operators"
    
    operator_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_info = Column(String(200), nullable=False)  # Phone or email
    alert_preference = Column(Enum(OperatorPreference), default=OperatorPreference.DASHBOARD)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trucks = relationship("Truck", back_populates="operator")


class Truck(Base):
    """Truck model representing fleet vehicles."""
    __tablename__ = "trucks"
    
    truck_id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.operator_id"), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    status = Column(Enum(TruckStatus), default=TruckStatus.ACTIVE)
    last_maintenance_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    operator = relationship("Operator", back_populates="trucks")
    alerts = relationship("Alert", back_populates="truck")


class Alert(Base):
    """Alert model representing weather alerts for trucks."""
    __tablename__ = "alerts"
    
    alert_id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.truck_id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    weather_data = Column(Text)  # JSON string of weather conditions
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    truck = relationship("Truck", back_populates="alerts")


class WeatherCache(Base):
    """Weather cache model for storing recent weather data."""
    __tablename__ = "weather_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    weather_data = Column(Text, nullable=False)  # JSON string
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)