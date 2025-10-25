# 🛰️ Fleet Weather Alert System

A comprehensive weather monitoring and alert system for fleet management, built with FastAPI and Python. This system automatically detects critical weather events and notifies truck drivers immediately through multiple channels.

## 🌟 Features

### Core Functionality
- **Real-time Weather Monitoring**: Continuous monitoring of weather conditions for all active trucks
- **Intelligent Alert System**: Automatic detection of critical weather events (heavy rain, storms, fog, high winds, extreme temperatures)
- **Multi-channel Notifications**: SMS, email, and dashboard notifications based on operator preferences
- **Fleet Management**: Complete truck and operator management with location tracking
- **RESTful API**: Comprehensive API for all system operations
- **Web Dashboard**: Modern, responsive web interface for monitoring

### Advanced Features
- **Scheduled Monitoring**: Automated weather checks every 5 minutes (configurable)
- **Alert Acknowledgment**: Drivers can acknowledge alerts through the API
- **Weather Caching**: Intelligent caching to reduce API calls
- **Comprehensive Logging**: Structured logging with file rotation
- **Health Monitoring**: System health checks and status monitoring
- **Hot Topics System**: Bonus social media trending analysis system

## 🏗️ Architecture

```
fleet_weather_alert/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── database.py            # Database setup
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── alerts.py          # Alert management API
│   │   ├── fleet.py           # Fleet management API
│   │   └── hot_topics.py      # Hot topics API
│   └── services/
│       ├── __init__.py
│       ├── weather_service.py     # Weather monitoring
│       ├── notification_service.py # Notification handling
│       ├── data_loader.py         # Sample data loader
│       └── scheduler.py           # Task scheduling
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or poetry
- (Optional) Redis for caching
- (Optional) PostgreSQL for production

### Installation

1. **Clone and setup the project:**
```bash
cd /workspace/fleet_weather_alert
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the application:**
```bash
python -m app.main
```

4. **Access the system:**
- Web Dashboard: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./fleet_weather.db` |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | None (uses mock data) |
| `WEATHER_POLL_INTERVAL` | Weather check interval (seconds) | 300 |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | None |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | None |
| `SENDGRID_API_KEY` | SendGrid API key | None |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |

### Weather Alert Thresholds

| Threshold | Default | Description |
|-----------|---------|-------------|
| `HEAVY_RAIN_THRESHOLD` | 10.0 mm/h | Heavy rain detection |
| `WIND_SPEED_THRESHOLD` | 25.0 m/s | High wind detection |
| `VISIBILITY_THRESHOLD` | 1000 m | Fog detection |
| `EXTREME_TEMP_HIGH` | 40.0°C | Extreme high temperature |
| `EXTREME_TEMP_LOW` | -20.0°C | Extreme low temperature |

## 📡 API Endpoints

### Alerts
- `GET /api/alerts` - List all alerts with filtering
- `GET /api/alerts/{alert_id}` - Get specific alert
- `POST /api/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `POST /api/alerts/{alert_id}/resolve` - Resolve alert
- `GET /api/alerts/stats/summary` - Alert statistics

### Fleet Management
- `GET /api/fleet/trucks` - List all trucks
- `GET /api/fleet/trucks/{truck_id}` - Get specific truck
- `GET /api/fleet/operators` - List all operators
- `GET /api/fleet/operators/{operator_id}` - Get specific operator
- `GET /api/fleet/summary` - Fleet summary statistics

### Hot Topics (Bonus Feature)
- `GET /api/hot-topics/trending` - Get trending posts
- `GET /api/hot-topics/categories` - Get categories with trending posts
- `GET /api/hot-topics/categories/{category}` - Get trending posts by category
- `GET /api/hot-topics/stats` - Hot topics statistics

## 🗄️ Database Schema

### Core Tables
- **operators**: Driver information and notification preferences
- **trucks**: Fleet vehicles with location and status
- **alerts**: Weather alerts with severity and status
- **weather_cache**: Cached weather data for performance

### Sample Data
The system automatically loads sample data on first run:
- 8 sample operators with different notification preferences
- 15 sample trucks with random locations across the US
- Various truck statuses (active, maintenance, inactive)

## 🔧 Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Using Alembic (if configured)
alembic upgrade head
```

### Adding New Weather Conditions
1. Add new `AlertType` enum in `models.py`
2. Update `analyze_weather_conditions()` in `weather_service.py`
3. Add corresponding threshold in `config.py`

## 📊 Monitoring and Logging

### Log Files
- `fleet_weather.log` - Application logs with rotation
- Console output for development

### Health Checks
- `GET /api/health` - System health status
- Database connectivity check
- Service status monitoring

### Scheduler Jobs
- **Weather Monitoring**: Every 5 minutes (configurable)
- **Notification Processing**: Every 2 minutes
- **Daily Cleanup**: 2 AM daily

## 🌐 Web Dashboard

The system includes a modern web dashboard accessible at `http://localhost:8000`:

- **Real-time Statistics**: Active trucks, pending alerts, operators
- **Alert Management**: View and manage weather alerts
- **Fleet Overview**: Truck status and location tracking
- **API Integration**: Direct links to API documentation

## 🔔 Notification System

### Supported Channels
- **SMS**: Via Twilio integration
- **Email**: Via SendGrid integration
- **Dashboard**: Real-time web notifications

### Operator Preferences
- `ALL`: All notification channels
- `SMS`: SMS + Dashboard
- `EMAIL`: Email + Dashboard
- `DASHBOARD`: Dashboard only

## 🚛 Fleet Management

### Truck Statuses
- `ACTIVE`: Currently in operation
- `MAINTENANCE`: Under maintenance
- `INACTIVE`: Not in service
- `EMERGENCY`: Emergency status

### Location Tracking
- GPS coordinates (latitude/longitude)
- Real-time location updates via API
- Weather monitoring per location

## 🔥 Hot Topics System (Bonus)

A bonus social media trending analysis system:

- **Engagement Scoring**: `(likes*2 + views*0.5 + comments*3)`
- **Caching**: Redis-based caching with 1-minute TTL
- **Category Analysis**: Trending posts by category
- **Real-time Updates**: Automatic cache refresh

## 🛠️ Production Deployment

### Docker Support
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "app.main"]
```

### Environment Setup
1. Set production database URL
2. Configure real API keys (OpenWeatherMap, Twilio, SendGrid)
3. Set up Redis for caching
4. Configure logging levels
5. Set up process monitoring (systemd, supervisor, etc.)

## 📈 Performance Considerations

- **Weather Caching**: 10-minute cache to reduce API calls
- **Database Indexing**: Optimized queries with proper indexes
- **Background Processing**: Non-blocking scheduled tasks
- **Connection Pooling**: Efficient database connections

## 🔒 Security Features

- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Configurable cross-origin policies
- **Error Handling**: Comprehensive error management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/api/docs`
2. Review the logs in `fleet_weather.log`
3. Check the health endpoint at `/api/health`

## 🎯 Future Enhancements

- [ ] Machine learning for weather prediction
- [ ] Mobile app for drivers
- [ ] Integration with truck telematics
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support
- [ ] WebSocket real-time updates
- [ ] Advanced alert routing rules
- [ ] Historical weather data analysis

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Python**