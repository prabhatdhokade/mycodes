"""Fleet management API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Truck, Operator, TruckStatus
from app.schemas import TruckResponse, OperatorResponse, FleetSummary

router = APIRouter(prefix="/fleet", tags=["fleet"])


@router.get("/trucks", response_model=List[TruckResponse])
async def get_trucks(
    status: Optional[TruckStatus] = Query(None, description="Filter by truck status"),
    operator_id: Optional[int] = Query(None, description="Filter by operator ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of trucks to return"),
    offset: int = Query(0, ge=0, description="Number of trucks to skip"),
    db: Session = Depends(get_db)
):
    """Get all trucks with optional filtering."""
    query = db.query(Truck)
    
    if status:
        query = query.filter(Truck.status == status)
    if operator_id:
        query = query.filter(Truck.operator_id == operator_id)
    
    trucks = query.offset(offset).limit(limit).all()
    
    return [TruckResponse.from_orm(truck) for truck in trucks]


@router.get("/trucks/{truck_id}", response_model=TruckResponse)
async def get_truck(truck_id: int, db: Session = Depends(get_db)):
    """Get a specific truck by ID."""
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    
    return TruckResponse.from_orm(truck)


@router.get("/operators", response_model=List[OperatorResponse])
async def get_operators(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of operators to return"),
    offset: int = Query(0, ge=0, description="Number of operators to skip"),
    db: Session = Depends(get_db)
):
    """Get all operators."""
    operators = db.query(Operator).offset(offset).limit(limit).all()
    
    return [OperatorResponse.from_orm(operator) for operator in operators]


@router.get("/operators/{operator_id}", response_model=OperatorResponse)
async def get_operator(operator_id: int, db: Session = Depends(get_db)):
    """Get a specific operator by ID."""
    operator = db.query(Operator).filter(Operator.operator_id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    return OperatorResponse.from_orm(operator)


@router.get("/operators/{operator_id}/trucks", response_model=List[TruckResponse])
async def get_operator_trucks(operator_id: int, db: Session = Depends(get_db)):
    """Get all trucks assigned to a specific operator."""
    operator = db.query(Operator).filter(Operator.operator_id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    trucks = db.query(Truck).filter(Truck.operator_id == operator_id).all()
    
    return [TruckResponse.from_orm(truck) for truck in trucks]


@router.get("/summary", response_model=FleetSummary)
async def get_fleet_summary(db: Session = Depends(get_db)):
    """Get fleet summary statistics."""
    total_trucks = db.query(Truck).count()
    active_trucks = db.query(Truck).filter(Truck.status == TruckStatus.ACTIVE).count()
    maintenance_trucks = db.query(Truck).filter(Truck.status == TruckStatus.MAINTENANCE).count()
    inactive_trucks = db.query(Truck).filter(Truck.status == TruckStatus.INACTIVE).count()
    emergency_trucks = db.query(Truck).filter(Truck.status == TruckStatus.EMERGENCY).count()
    
    total_operators = db.query(Operator).count()
    
    return FleetSummary(
        total_trucks=total_trucks,
        active_trucks=active_trucks,
        maintenance_trucks=maintenance_trucks,
        inactive_trucks=inactive_trucks,
        emergency_trucks=emergency_trucks,
        total_operators=total_operators
    )


@router.put("/trucks/{truck_id}/status")
async def update_truck_status(
    truck_id: int,
    status: TruckStatus,
    db: Session = Depends(get_db)
):
    """Update truck status."""
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    
    truck.status = status
    db.commit()
    
    return {"message": "Truck status updated successfully", "truck_id": truck_id, "status": status}


@router.put("/trucks/{truck_id}/location")
async def update_truck_location(
    truck_id: int,
    lat: float,
    lng: float,
    db: Session = Depends(get_db)
):
    """Update truck location."""
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    
    truck.location_lat = lat
    truck.location_lng = lng
    db.commit()
    
    return {"message": "Truck location updated successfully", "truck_id": truck_id, "location": {"lat": lat, "lng": lng}}