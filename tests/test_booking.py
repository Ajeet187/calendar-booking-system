import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app
from app.core.dependencies import get_booking_repository, get_booking_service, get_time_utils
from app.repositories.booking_repo import InMemoryBookingRepository
from app.services.booking_service import BookingService
from app.utils.time_utils import TimeUtils
from concurrent.futures import ThreadPoolExecutor, as_completed


"""
Ensure complete test isolation. Each test gets fresh instances of:
- Repository (with empty data)
- Service (with fresh repository)
- TimeUtils (fresh instance)

1. No test contamination - each test starts with clean state
2. Order independence - tests can run in any order
3. Easy to mock - dependencies can be overridden with test doubles
4. Perfect isolation - tests are completely independent
"""

# Test fixture for isolated client with fresh dependencies
@pytest.fixture
def client():
    """Test client with fresh dependencies for each test"""
    # Create fresh instances for each test
    repository = InMemoryBookingRepository()
    service = BookingService(repository)
    time_utils = TimeUtils()
    
    # Override FastAPI dependencies with fresh instances
    app.dependency_overrides[get_booking_repository] = lambda: repository
    app.dependency_overrides[get_booking_service] = lambda: service
    app.dependency_overrides[get_time_utils] = lambda: time_utils
    
    yield TestClient(app)
    
    # Cleanup after each test - critical for isolation
    app.dependency_overrides.clear()

# ===== SET AVAILABILITY TEST CASES =====

def test_set_availability_success(client):
    """Test successful availability setting"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "10:00",
        "end_time": "17:00"
    })
    assert res.status_code == 200
    assert res.json()["message"] == "Availability set successfully"

def test_set_availability_invalid_time_format(client):
    """Test invalid time format"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "25:00",  # Invalid hour
        "end_time": "17:00"
    })
    assert res.status_code == 422

def test_set_availability_start_after_end(client):
    """Test start time after end time"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "18:00",
        "end_time": "17:00"
    })
    assert res.status_code == 400
    assert "Start time must be before end time" in res.json()["detail"]

def test_set_availability_same_start_end(client):
    """Test start time equals end time"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "17:00",
        "end_time": "17:00"
    })
    assert res.status_code == 400
    assert "Start time must be before end time" in res.json()["detail"]


def test_set_availability_missing_fields(client):
    """Test missing required fields"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "10:00"
        # Missing end_time
    })
    assert res.status_code == 422  # Validation error

def test_set_availability_empty_strings(client):
    """Test empty string values"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "",
        "start_time": "",
        "end_time": ""
    })
    assert res.status_code == 422

def test_set_availability_malformed_time(client):
    """Test malformed time strings"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "10:30:45",  # Should be HH:00 format
        "end_time": "17:00"
    })
    assert res.status_code == 422

# ===== GET SLOTS EDGE CASES =====

def test_get_slots_success(client):
    """Test successful slot retrieval"""
    # First set availability
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user2",
        "start_time": "09:00",
        "end_time": "17:00"
    })

    today_str = date.today().isoformat()  # e.g. "2025-08-09"

    res = client.get(f"/api/v1/slots?calendar_owner_id=user2&for_date={today_str}")
    assert res.status_code == 200
    assert "available_slots" in res.json()
    slots = res.json()["available_slots"]
    assert len(slots) > 0
    assert all(":" in slot for slot in slots)

def test_get_slots_user_not_found(client):
    """Test getting slots for non-existent user"""
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    res = client.get(f"/api/v1/slots?calendar_owner_id=nonexistent&for_date={today_str}")
    assert res.status_code == 404
    assert "User Not Found" in res.json()["detail"]

def test_get_slots_missing_parameters(client):
    """Test missing query parameters"""
    res = client.get("/api/v1/slots")
    assert res.status_code == 422

def test_get_slots_invalid_date_format(client):
    """Test invalid date format"""
    res = client.get("/api/v1/slots?calendar_owner_id=user1&for_date=invalid-date")
    assert res.status_code == 422

def test_get_slots_past_date(client):

    """Test getting slots for past date"""

    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "09:00",
        "end_time": "17:00"
    })

    past_date = (date.today() - timedelta(days=1)).isoformat()
    res = client.get(f"/api/v1/slots?calendar_owner_id=user1&for_date={past_date}")
    assert res.status_code == 400
    assert "Cannot retrieve slots for a past date" in res.json()["detail"]

def test_get_slots_far_future_date(client):
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user1",
        "start_time": "09:00",
        "end_time": "17:00"
    })

    """Test getting slots for far future date"""
    future_date = (date.today() + timedelta(days=300)).isoformat()
    res = client.get(f"/api/v1/slots?calendar_owner_id=user1&for_date={future_date}")
    assert res.status_code == 200

def test_get_slots_empty_availability(client):
    """Test getting slots when user has no availability set"""
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    res = client.get(f"/api/v1/slots?calendar_owner_id=newuser&for_date={today_str}")
    assert res.status_code == 404

# ===== BOOK APPOINTMENT EDGE CASES =====

def test_book_appointment_success(client):
    """Test successful appointment booking"""
    # Set availability first
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user3",
        "start_time": "10:00",
        "end_time": "17:00"
    })
    today_str = date.today().isoformat()  # e.g. "2025-08-09"

    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user3",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": today_str,
        "slot_start_time": "10:00"
    })
    assert res.status_code == 200
    assert res.json()["message"] == "Appointment booked"

def test_book_appointment_slot_already_booked(client):
    """Test booking an already booked slot"""
    # Set availability
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user4",
        "start_time": "10:00",
        "end_time": "17:00"
    })
    
    # Book first appointment
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user4",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": today_str,
        "slot_start_time": "10:00"
    })
    
    # Try to book same slot again
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user4",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": today_str,
        "slot_start_time": "10:00"
    })
    assert res.status_code == 409
    assert "Slot already booked" in res.json()["detail"]

def test_book_appointment_outside_availability(client):
    """Test booking outside available hours"""
    # Set availability for 10:00-17:00
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user5",
        "start_time": "10:00",
        "end_time": "17:00"
    })
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    # Try to book at 18:00 (outside availability)
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user5",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": today_str,
        "slot_start_time": "18:00"
    })
    assert res.status_code == 400
    assert "Invalid time" in res.json()["detail"]

def test_book_appointment_user_not_found(client):
    """Test booking for user without availability"""
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "nonexistent",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": today_str,
        "slot_start_time": "10:00"
    })
    assert res.status_code == 404
    assert "User Not Found" in res.json()["detail"]

def test_book_appointment_invalid_time_format(client):
    """Test booking with invalid time format"""
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user1",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": today_str,
        "slot_start_time": "25:00"  # Invalid hour
    })
    assert res.status_code == 422

def test_book_appointment_missing_fields(client):
    """Test booking with missing required fields"""
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user1",
        "invitee_name": "Ajeet Singh",
        # Missing invitee_email, date, slot_start_time
    })
    assert res.status_code == 422

def test_book_appointment_invalid_email(client):
    """Test booking with invalid email format"""
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user1",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "invalid email",
        "date": "2025-08-07",
        "slot_start_time": "10:00"
    })
    assert res.status_code == 422

def test_book_appointment_past_date(client):
    """Test booking for past date"""
    past_date = (date.today() - timedelta(days=1)).isoformat()
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user1",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": past_date,
        "slot_start_time": "10:00"
    })
    assert res.status_code == 422


def test_book_appointment_more_than_max_advance_booking_days_date(client):
    """Test successful appointment booking"""
    # Set availability first
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user3",
        "start_time": "10:00",
        "end_time": "17:00"
    })
    far_future_str = (date.today() + timedelta(days=371)).isoformat()

    print("far_future_str", far_future_str)

    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user3",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmail.com",
        "date": far_future_str,
        "slot_start_time": "10:00"
    })
    assert res.status_code == 422

# ===== APPOINTMENTS EDGE CASES =====

def test_list_appointments_success(client):
    """Test successful appointment listing"""
    # Set availability and book appointment
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user6",
        "start_time": "10:00",
        "end_time": "17:00"
    })
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    
    # Book appointment
    booking_res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user6",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmaiil.com",
        "date": today_str,
        "slot_start_time": "10:00"
    })
    assert booking_res.status_code == 200
    
    # Get appointments
    res = client.get("/api/v1/appointments?calendar_owner_id=user6")
    assert res.status_code == 200
    appointments = res.json()
    assert len(appointments) > 0
    assert appointments[0]["invitee_name"] == "Ajeet Singh"

def test_list_appointments_no_appointments(client):
    """Test listing appointments for user with no appointments"""
    res = client.get("/api/v1/appointments?calendar_owner_id=user7")
    assert res.status_code == 200
    assert res.json() == []

def test_list_appointments_missing_parameter(client):
    """Test listing appointments without calendar_owner_id"""
    res = client.get("/api/v1/appointments")
    assert res.status_code == 422

def test_list_appointments_user_not_found(client):
    """Test listing appointments for non-existent user"""
    res = client.get("/api/v1/appointments?calendar_owner_id=nonexistent")
    assert res.status_code == 200
    assert res.json() == []


def test_concurrent_bookings(client):
    """Test multiple users booking different slots"""
    # Set availability for user
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user8",
        "start_time": "10:00",
        "end_time": "17:00"
    })
    
    # Book multiple slots
    today_str = date.today().isoformat()  # e.g. "2025-08-09"

    for i, hour in enumerate(["10:00", "11:00", "12:00"]):
        res = client.post("/api/v1/appointments", json={
            "calendar_owner_id": "user8",
            "invitee_name": f"Ajeet Singh {i}",
            "invitee_email": f"ajeetsing{i}@gmail.com",
            "date": today_str,
            "slot_start_time": hour
        })
        assert res.status_code == 200
    
    # Verify slots are booked
    slots = client.get(f"/api/v1/slots?calendar_owner_id=user8&for_date={today_str}").json()["available_slots"]
    assert "10:00" not in slots
    assert "11:00" not in slots
    assert "12:00" not in slots

def test_boundary_time_slots(client):
    """Test booking at boundary times"""
    # Set availability with specific boundaries
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user9",
        "start_time": "09:00",
        "end_time": "17:00"
    })
    
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    # Try to book at exact start time
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user9",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmaiil.com",
        "date": today_str,
        "slot_start_time": "09:00"
    })
    assert res.status_code == 200
    today_str = date.today().isoformat()  # e.g. "2025-08-09"

    # Try to book at end time (should fail)
    res = client.post("/api/v1/appointments", json={
        "calendar_owner_id": "user9",
        "invitee_name": "Ajeet Singh",
        "invitee_email": "ajeetsing187@gmaiil.com",
        "date": today_str,
        "slot_start_time": "17:00"
    })
    assert res.status_code == 400

# ===== PERFORMANCE EDGE CASES =====

def test_large_time_range(client):
    """Test availability with very large time range"""
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": "user10",
        "start_time": "00:00",
        "end_time": "23:00"
    })
    assert res.status_code == 200
    today_str = date.today().isoformat()  # e.g. "2025-08-09"
    
    slots = client.get(f"/api/v1/slots?calendar_owner_id=user10&for_date={today_str}").json()["available_slots"]
    assert len(slots) == 23  # 23 hourly slots

def test_many_appointments(client):
    """Test system with many appointments"""
    # Set availability
    client.post("/api/v1/availability", json={
        "calendar_owner_id": "user11",
        "start_time": "09:00",
        "end_time": "18:00"
    })
    
    today_str = date.today().isoformat()  # e.g. "2025-08-09"

    # Book many appointments
    for i in range(9):  # 9 hours available
        res = client.post("/api/v1/appointments", json={
            "calendar_owner_id": "user11",
            "invitee_name": f"User {i}",
            "invitee_email": f"user{i}@example.com",
            "date": today_str,
            "slot_start_time": f"{9+i:02d}:00"
        })
        assert res.status_code == 200
    
    # Verify no slots are available
    slots = client.get(f"/api/v1/slots?calendar_owner_id=user11&for_date={today_str}").json()["available_slots"]
    assert len(slots) == 0



#===== TEST Concurrent request ======

def test_concurrent_booking(client):
    # Setup - set availability first
    calendar_owner_id = "concurrent_user"
    date_str = "2025-08-10"
    slot_start_time = "10:00"

    # Set availability
    res = client.post("/api/v1/availability", json={
        "calendar_owner_id": calendar_owner_id,
        "start_time": "09:00",
        "end_time": "17:00"
    })
    assert res.status_code == 200

    # Define booking payload
    booking_payload = {
        "calendar_owner_id": calendar_owner_id,
        "invitee_name": "Test User",
        "invitee_email": "testuser@example.com",
        "date": date_str,
        "slot_start_time": slot_start_time
    }

    # Define a function to attempt booking
    def try_booking():
        return client.post("/api/v1/appointments", json=booking_payload)

    # Use ThreadPoolExecutor to simulate 5 concurrent booking attempts
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(try_booking) for _ in range(5)]
        results = [f.result() for f in as_completed(futures)]

    # Count successes and conflicts
    success_count = sum(1 for r in results if r.status_code == 200)
    conflict_count = sum(1 for r in results if r.status_code == 409)

    # Exactly one should succeed, rest should get conflict (409)
    assert success_count == 1, f"Expected 1 success, got {success_count}"
    assert conflict_count == 4, f"Expected 4 conflicts, got {conflict_count}"
