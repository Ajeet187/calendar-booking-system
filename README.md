# Calendar Booking System

A robust, scalable calendar booking system built with FastAPI, featuring clean architecture, design patterns, and comprehensive testing.

## Features

- **User Availability Management** - Set and manage working hours
- **Appointment Booking** - Book time slots with validation
- **Slot Availability** - View available time slots for any date
- **Appointment Management** - List appointments
- **Input Validation** - Comprehensive validation with Pydantic
- **Error Handling** - Custom exception handling with proper HTTP status codes
- **Handle Concurrent Booking Requests** - Handle case when concurrent request try to book same slot for same date and same calendar owner

##  Architecture

This project follows clean architecture principles with the following design patterns:

- **Dependency Injection** - Services and repositories are injected
- **Repository Pattern** - Abstract data access layer
- **Factory Pattern** - Factory functions for creating instances
- **Singleton Pattern** - Configuration management
- **Strategy Pattern** - Swappable repository implementations

### Project Structure

```
assig/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── dependencies.py    # Dependency injection
│   │   └── exceptions.py      # Custom exceptions
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── repositories/
│   │   ├── base_repository.py # Abstract repository interface
│   │   └── booking_repo.py    # In-memory repository implementation
│   ├── routers/
│   │   └── booking_routes.py  # API endpoints
│   ├── services/
│   │   └── booking_service.py # Business logic layer
│   ├── utils/
│   │   └── time_utils.py      # Time utility functions
│   └── main.py                # FastAPI application
├── tests/
│   └── test_booking.py        # Comprehensive test suite
├── requirements.txt           # Python dependencies
└── Dockerfile                 # Docker File
└── quick_start                # run this file for quick start python quick_start.py
└── README.md                  # This file

```

##  Installation

### Prerequisites

- Python 3.12
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd assig
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```



The API will be available at `http://localhost:8000`




## Docker Setup

### Create Docker Image
```bash
docker build -t booking-api .
```

### Run Docker Container
```bash
docker run -p 8000:8000 booking-api
```

## API Documentation

Once the server is running, you can access:


## API Endpoints

### Base URL: `/api/v1`

#### Set User Availability
```http
POST /availability
Content-Type: application/json

{
    "calendar_owner_id": "user123",
    "start_time": "09:00",
    "end_time": "17:00"
}
```

#### Get Available Slots
```http
GET /slots?calendar_owner_id=user123&for_date=2024-01-15
```

#### Book Appointment
```http
POST /appointments
Content-Type: application/json

{
    "calendar_owner_id": "user123",
    "invitee_name": "Ajeet Singh",
    "invitee_email": "ajeetsing187@gmail.com",
    "date": "2025-10-15",
    "slot_start_time": "10:00"
}
```

#### List Appointments
```http
GET /appointments?calendar_owner_id=user123
```

##  Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_booking.py::test_set_availability_success -v
```

### Test Coverage
The test suite includes comprehensive edge cases:
- Input validation
- Business logic validation
- Error handling
- Time boundary conditions
- Concurrent operations
- Performance scenarios

##  Configuration

The application uses environment-based configuration. Create a `.env` file in the root directory:

```env
# Application settings
APP_NAME="Calendar Booking System"
APP_VERSION="1.0.0"
DEBUG=false

# Time settings
DEFAULT_SLOT_DURATION_MINUTES=60


# Booking settings
MAX_ADVANCE_BOOKING_DAYS=365
```

## Design Patterns Used

### 1. Dependency Injection
Services and repositories are injected rather than imported directly, making the code more testable and maintainable.

### 2. Repository Pattern
Abstract interface for data access with concrete implementations, allowing easy swapping of storage backends.

### 3. Factory Pattern
Factory functions for creating repository instances, providing flexibility in object creation.

### 4. Singleton Pattern
Configuration management ensures single instance of BaseBookingRepository, BookingService, settings across the application to persist the in memory data across the requests.

### 5. Strategy Pattern
Different repository implementations can be swapped without changing the business logic.

## 🔄 Future Enhancements

### Planned Features
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Email notifications
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Recurring appointments
- [ ] Timezone support
- [ ] Rate limiting
- [ ] Caching (Redis)
- [ ] Background job processing

### Scalability Considerations
- Horizontal scaling with load balancers
- Database sharding for large datasets
- Microservices architecture
- Event-driven architecture for notifications
- Caching strategies for performance

##  Error Handling

The application uses custom exceptions for better error handling:

- `BookingException` - Base exception for booking-related errors
- `ValidationException` - Input validation errors (400)
- `NotFoundException` - Resource not found errors (404)
- `ConflictException` - Conflict errors like double booking (409)


