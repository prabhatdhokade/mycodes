"""Configuration management for the Fleet Weather Alert System."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(default="sqlite:///./fleet_weather.db", env="DATABASE_URL")
    
    # Weather API
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    weather_api_base_url: str = Field(default="https://api.openweathermap.org/data/2.5", env="WEATHER_API_BASE_URL")
    weather_poll_interval: int = Field(default=300, env="WEATHER_POLL_INTERVAL")
    
    # Notifications
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    from_email: str = Field(default="noreply@fleetweather.com", env="FROM_EMAIL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Application
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Weather Alert Thresholds
    heavy_rain_threshold: float = Field(default=10.0, env="HEAVY_RAIN_THRESHOLD")
    wind_speed_threshold: float = Field(default=25.0, env="WIND_SPEED_THRESHOLD")
    visibility_threshold: int = Field(default=1000, env="VISIBILITY_THRESHOLD")
    extreme_temp_high: float = Field(default=40.0, env="EXTREME_TEMP_HIGH")
    extreme_temp_low: float = Field(default=-20.0, env="EXTREME_TEMP_LOW")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()