"""Weather monitoring service for detecting critical weather conditions."""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Truck, WeatherCache, Alert, AlertType, AlertSeverity
from app.config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for monitoring weather conditions and generating alerts."""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.openweather_api_key
        self.base_url = settings.weather_api_base_url
        
    def get_weather_data(self, lat: float, lng: float) -> Optional[Dict]:
        """Get weather data for a specific location."""
        try:
            # Check cache first
            cached_data = self._get_cached_weather(lat, lng)
            if cached_data:
                return cached_data
            
            # If no API key, use mock data
            if not self.api_key:
                return self._get_mock_weather_data(lat, lng)
            
            # Call OpenWeatherMap API
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lng,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            weather_data = response.json()
            
            # Cache the data
            self._cache_weather_data(lat, lng, weather_data)
            
            return weather_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch weather data for {lat}, {lng}: {e}")
            # Fallback to mock data
            return self._get_mock_weather_data(lat, lng)
        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {e}")
            return self._get_mock_weather_data(lat, lng)
    
    def _get_cached_weather(self, lat: float, lng: float) -> Optional[Dict]:
        """Get cached weather data if still valid."""
        cache = self.db.query(WeatherCache).filter(
            WeatherCache.location_lat == lat,
            WeatherCache.location_lng == lng,
            WeatherCache.expires_at > datetime.utcnow()
        ).first()
        
        if cache:
            return json.loads(cache.weather_data)
        return None
    
    def _cache_weather_data(self, lat: float, lng: float, weather_data: Dict):
        """Cache weather data for future use."""
        try:
            # Remove old cache entries
            self.db.query(WeatherCache).filter(
                WeatherCache.location_lat == lat,
                WeatherCache.location_lng == lng
            ).delete()
            
            # Add new cache entry
            cache = WeatherCache(
                location_lat=lat,
                location_lng=lng,
                weather_data=json.dumps(weather_data),
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            self.db.add(cache)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to cache weather data: {e}")
            self.db.rollback()
    
    def _get_mock_weather_data(self, lat: float, lng: float) -> Dict:
        """Generate mock weather data for testing."""
        import random
        
        # Simulate different weather conditions based on location
        base_temp = 20 + (lat * 0.5) + random.uniform(-10, 10)
        base_humidity = 60 + random.uniform(-20, 20)
        base_pressure = 1013 + random.uniform(-50, 50)
        
        # Simulate weather events
        weather_conditions = [
            {"main": "Clear", "description": "clear sky"},
            {"main": "Clouds", "description": "few clouds"},
            {"main": "Rain", "description": "light rain"},
            {"main": "Rain", "description": "heavy rain"},
            {"main": "Thunderstorm", "description": "thunderstorm"},
            {"main": "Fog", "description": "fog"},
            {"main": "Snow", "description": "light snow"}
        ]
        
        condition = random.choice(weather_conditions)
        
        return {
            "main": {
                "temp": base_temp,
                "humidity": base_humidity,
                "pressure": base_pressure
            },
            "weather": [condition],
            "wind": {
                "speed": random.uniform(0, 30),
                "deg": random.uniform(0, 360)
            },
            "visibility": random.uniform(100, 10000),
            "dt": int(datetime.utcnow().timestamp())
        }
    
    def analyze_weather_conditions(self, weather_data: Dict) -> List[Tuple[AlertType, AlertSeverity, str]]:
        """Analyze weather data and return critical conditions."""
        alerts = []
        
        try:
            main = weather_data.get("main", {})
            weather = weather_data.get("weather", [{}])[0]
            wind = weather_data.get("wind", {})
            visibility = weather_data.get("visibility", 10000)
            
            temp = main.get("temp", 20)
            humidity = main.get("humidity", 50)
            pressure = main.get("pressure", 1013)
            wind_speed = wind.get("speed", 0)
            weather_main = weather.get("main", "")
            weather_desc = weather.get("description", "")
            
            # Heavy rain detection
            if weather_main == "Rain" and "heavy" in weather_desc.lower():
                alerts.append((
                    AlertType.HEAVY_RAIN,
                    AlertSeverity.HIGH,
                    f"Heavy rain detected: {weather_desc}"
                ))
            elif weather_main == "Rain" and weather_desc:
                alerts.append((
                    AlertType.HEAVY_RAIN,
                    AlertSeverity.MEDIUM,
                    f"Rain detected: {weather_desc}"
                ))
            
            # Storm detection
            if weather_main == "Thunderstorm":
                alerts.append((
                    AlertType.STORM,
                    AlertSeverity.CRITICAL,
                    f"Thunderstorm detected: {weather_desc}"
                ))
            
            # Fog detection
            if weather_main == "Fog" or visibility < settings.visibility_threshold:
                severity = AlertSeverity.HIGH if visibility < 500 else AlertSeverity.MEDIUM
                alerts.append((
                    AlertType.FOG,
                    severity,
                    f"Fog detected - Visibility: {visibility}m"
                ))
            
            # High wind detection
            if wind_speed > settings.wind_speed_threshold:
                severity = AlertSeverity.CRITICAL if wind_speed > 40 else AlertSeverity.HIGH
                alerts.append((
                    AlertType.HIGH_WIND,
                    severity,
                    f"High wind detected: {wind_speed:.1f} m/s"
                ))
            
            # Extreme temperature detection
            if temp > settings.extreme_temp_high:
                alerts.append((
                    AlertType.EXTREME_TEMP,
                    AlertSeverity.HIGH,
                    f"Extreme high temperature: {temp:.1f}°C"
                ))
            elif temp < settings.extreme_temp_low:
                alerts.append((
                    AlertType.EXTREME_TEMP,
                    AlertSeverity.HIGH,
                    f"Extreme low temperature: {temp:.1f}°C"
                ))
            
            # Cyclone detection (simplified)
            if wind_speed > 30 and pressure < 1000:
                alerts.append((
                    AlertType.CYCLONE,
                    AlertSeverity.CRITICAL,
                    f"Cyclone conditions: Wind {wind_speed:.1f} m/s, Pressure {pressure:.1f} hPa"
                ))
                
        except Exception as e:
            logger.error(f"Error analyzing weather conditions: {e}")
        
        return alerts
    
    def check_fleet_weather(self) -> int:
        """Check weather conditions for all active trucks and create alerts."""
        alerts_created = 0
        
        try:
            # Get all active trucks
            trucks = self.db.query(Truck).filter(Truck.status == "active").all()
            
            for truck in trucks:
                # Get weather data for truck location
                weather_data = self.get_weather_data(truck.location_lat, truck.location_lng)
                
                if not weather_data:
                    continue
                
                # Analyze weather conditions
                weather_alerts = self.analyze_weather_conditions(weather_data)
                
                # Create alerts for critical conditions
                for alert_type, severity, message in weather_alerts:
                    # Check if similar alert already exists for this truck
                    existing_alert = self.db.query(Alert).filter(
                        Alert.truck_id == truck.truck_id,
                        Alert.alert_type == alert_type,
                        Alert.status == "pending",
                        Alert.created_at > datetime.utcnow() - timedelta(hours=1)
                    ).first()
                    
                    if not existing_alert:
                        alert = Alert(
                            truck_id=truck.truck_id,
                            alert_type=alert_type,
                            severity=severity,
                            message=message,
                            weather_data=json.dumps(weather_data),
                            location_lat=truck.location_lat,
                            location_lng=truck.location_lng
                        )
                        self.db.add(alert)
                        alerts_created += 1
                        logger.info(f"Created {severity} {alert_type} alert for truck {truck.truck_id}")
            
            self.db.commit()
            logger.info(f"Created {alerts_created} new weather alerts")
            
        except Exception as e:
            logger.error(f"Error checking fleet weather: {e}")
            self.db.rollback()
        
        return alerts_created