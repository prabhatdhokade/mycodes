"""Data loader service for initializing sample data."""

import json
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Operator, Truck, OperatorPreference, TruckStatus

logger = logging.getLogger(__name__)


class DataLoader:
    """Service for loading sample data into the database."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def load_sample_data(self):
        """Load sample operators and trucks into the database."""
        try:
            # Create sample operators
            operators = self._create_sample_operators()
            self.db.add_all(operators)
            self.db.commit()
            
            # Create sample trucks
            trucks = self._create_sample_trucks(operators)
            self.db.add_all(trucks)
            self.db.commit()
            
            logger.info(f"Loaded {len(operators)} operators and {len(trucks)} trucks")
            
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
            self.db.rollback()
            raise
    
    def _create_sample_operators(self) -> List[Operator]:
        """Create sample operators."""
        operators_data = [
            {
                "name": "John Smith",
                "contact_info": "+1-555-0101",
                "alert_preference": OperatorPreference.ALL
            },
            {
                "name": "Sarah Johnson",
                "contact_info": "sarah.johnson@email.com",
                "alert_preference": OperatorPreference.EMAIL
            },
            {
                "name": "Mike Wilson",
                "contact_info": "+1-555-0102",
                "alert_preference": OperatorPreference.SMS
            },
            {
                "name": "Lisa Brown",
                "contact_info": "lisa.brown@email.com",
                "alert_preference": OperatorPreference.EMAIL
            },
            {
                "name": "David Lee",
                "contact_info": "+1-555-0103",
                "alert_preference": OperatorPreference.ALL
            },
            {
                "name": "Emma Davis",
                "contact_info": "emma.davis@email.com",
                "alert_preference": OperatorPreference.DASHBOARD
            },
            {
                "name": "Robert Taylor",
                "contact_info": "+1-555-0104",
                "alert_preference": OperatorPreference.SMS
            },
            {
                "name": "Jennifer Martinez",
                "contact_info": "jennifer.martinez@email.com",
                "alert_preference": OperatorPreference.EMAIL
            }
        ]
        
        operators = []
        for i, data in enumerate(operators_data, 1):
            operator = Operator(
                operator_id=i,
                name=data["name"],
                contact_info=data["contact_info"],
                alert_preference=data["alert_preference"]
            )
            operators.append(operator)
        
        return operators
    
    def _create_sample_trucks(self, operators: List[Operator]) -> List[Truck]:
        """Create sample trucks with random locations."""
        # Sample locations across different regions
        locations = [
            (40.7128, -74.0060),   # New York
            (34.0522, -118.2437),  # Los Angeles
            (41.8781, -87.6298),   # Chicago
            (29.7604, -95.3698),   # Houston
            (33.4484, -112.0740),  # Phoenix
            (39.7392, -104.9903),  # Denver
            (25.7617, -80.1918),   # Miami
            (47.6062, -122.3321),  # Seattle
            (32.7767, -96.7970),   # Dallas
            (42.3601, -71.0589),   # Boston
        ]
        
        truck_data = [
            {"license_plate": "TRK-001", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-002", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-003", "status": TruckStatus.MAINTENANCE},
            {"license_plate": "TRK-004", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-005", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-006", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-007", "status": TruckStatus.INACTIVE},
            {"license_plate": "TRK-008", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-009", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-010", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-011", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-012", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-013", "status": TruckStatus.MAINTENANCE},
            {"license_plate": "TRK-014", "status": TruckStatus.ACTIVE},
            {"license_plate": "TRK-015", "status": TruckStatus.ACTIVE},
        ]
        
        trucks = []
        for i, data in enumerate(truck_data, 1):
            # Assign random operator
            operator = random.choice(operators)
            
            # Assign random location with some variation
            base_lat, base_lng = random.choice(locations)
            lat = base_lat + random.uniform(-0.5, 0.5)
            lng = base_lng + random.uniform(-0.5, 0.5)
            
            # Random maintenance date (within last 6 months)
            maintenance_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
            
            truck = Truck(
                truck_id=i,
                operator_id=operator.operator_id,
                license_plate=data["license_plate"],
                location_lat=lat,
                location_lng=lng,
                status=data["status"],
                last_maintenance_date=maintenance_date
            )
            trucks.append(truck)
        
        return trucks