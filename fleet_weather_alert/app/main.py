"""Main FastAPI application for Fleet Weather Alert System."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import os

from app.database import get_db, create_tables
from app.routes import alerts, fleet, hot_topics
from app.schemas import HealthCheckResponse
from app.config import settings
from app.services.scheduler import SchedulerService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fleet_weather.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Fleet Weather Alert System",
    description="A comprehensive weather monitoring and alert system for fleet management",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alerts.router, prefix="/api")
app.include_router(fleet.router, prefix="/api")
app.include_router(hot_topics.router, prefix="/api")

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Fleet Weather Alert System...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Initialize sample data if database is empty
    await initialize_sample_data()
    
    # Start scheduler
    scheduler = SchedulerService()
    scheduler.start()
    app.state.scheduler = scheduler
    logger.info("Scheduler started")
    
    logger.info("Application startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Fleet Weather Alert System...")
    
    # Stop scheduler
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.stop()
        logger.info("Scheduler stopped")
    
    logger.info("Application shutdown completed")


async def initialize_sample_data():
    """Initialize sample data if database is empty."""
    from app.models import Operator, Truck
    from app.services.data_loader import DataLoader
    
    db = next(get_db())
    try:
        # Check if we have any operators
        if db.query(Operator).count() == 0:
            logger.info("Initializing sample data...")
            data_loader = DataLoader(db)
            data_loader.load_sample_data()
            logger.info("Sample data loaded successfully")
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fleet Weather Alert System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4rem 0; }
            .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .alert-card { border-left: 4px solid #dc3545; }
            .truck-card { border-left: 4px solid #28a745; }
            .operator-card { border-left: 4px solid #17a2b8; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="#"><i class="fas fa-truck"></i> Fleet Weather Alert</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/api/docs">API Docs</a>
                </div>
            </div>
        </nav>

        <div class="hero-section">
            <div class="container text-center">
                <h1 class="display-4 mb-4"><i class="fas fa-cloud-rain"></i> Fleet Weather Alert System</h1>
                <p class="lead">Real-time weather monitoring and alerting for your fleet</p>
                <a href="/api/docs" class="btn btn-light btn-lg">View API Documentation</a>
            </div>
        </div>

        <div class="container my-5">
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card alert-card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-exclamation-triangle"></i> Active Alerts</h5>
                            <p class="card-text">Monitor real-time weather alerts for your fleet</p>
                            <a href="/api/alerts" class="btn btn-outline-danger">View Alerts</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card truck-card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-truck"></i> Fleet Management</h5>
                            <p class="card-text">Track trucks, operators, and maintenance records</p>
                            <a href="/api/fleet" class="btn btn-outline-success">View Fleet</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card operator-card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-user"></i> Operators</h5>
                            <p class="card-text">Manage driver information and notification preferences</p>
                            <a href="/api/fleet/operators" class="btn btn-outline-info">View Operators</a>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-5">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i> System Status</h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-md-3">
                                    <h3 class="text-success" id="active-trucks">-</h3>
                                    <p>Active Trucks</p>
                                </div>
                                <div class="col-md-3">
                                    <h3 class="text-warning" id="pending-alerts">-</h3>
                                    <p>Pending Alerts</p>
                                </div>
                                <div class="col-md-3">
                                    <h3 class="text-info" id="total-operators">-</h3>
                                    <p>Operators</p>
                                </div>
                                <div class="col-md-3">
                                    <h3 class="text-primary" id="system-status">Online</h3>
                                    <p>System Status</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="bg-dark text-white text-center py-3">
            <p>&copy; 2024 Fleet Weather Alert System. Built with FastAPI and Python.</p>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Load dashboard data
            async function loadDashboardData() {
                try {
                    const [fleetResponse, alertsResponse] = await Promise.all([
                        fetch('/api/fleet/summary'),
                        fetch('/api/alerts/stats/summary')
                    ]);
                    
                    const fleetData = await fleetResponse.json();
                    const alertsData = await alertsResponse.json();
                    
                    document.getElementById('active-trucks').textContent = fleetData.active_trucks;
                    document.getElementById('pending-alerts').textContent = alertsData.pending_alerts;
                    document.getElementById('total-operators').textContent = fleetData.total_operators;
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                }
            }
            
            // Load data on page load
            loadDashboardData();
            
            // Refresh data every 30 seconds
            setInterval(loadDashboardData, 30000);
        </script>
    </body>
    </html>
    """


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Check database connection
        db.execute("SELECT 1")
        database_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "unhealthy"
    
    # Check weather service (simplified)
    weather_service_status = "healthy"  # In a real app, you'd check the actual service
    
    return HealthCheckResponse(
        status="healthy" if database_status == "healthy" else "unhealthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database_status=database_status,
        weather_service_status=weather_service_status
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )