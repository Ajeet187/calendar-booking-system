import uuid
from typing import Dict, List, Optional
from datetime import time, date
from app.repositories.base_repository import BaseBookingRepository

class InMemoryBookingRepository(BaseBookingRepository):
    """In-memory implementation of booking repository"""
    
    def __init__(self):
        self.availability_store: Dict[str, Dict[str, time]] = {}
        self.appointments_store: Dict[str, List[Dict]] = {}
    
    def set_availability(self, calendar_owner_id: str, start: time, end: time) -> None:
        """Set user availability"""
        self.availability_store[calendar_owner_id] = {"start": start, "end": end}
    
    def get_availability(self, calendar_owner_id: str) -> Optional[Dict[str, time]]:
        """Get user availability"""
        return self.availability_store.get(calendar_owner_id)
    
    def add_appointment(self, calendar_owner_id: str, appointment: Dict) -> None:
        """Add a new appointment with unique ID"""
        appointment_id = str(uuid.uuid4())
        appointment["id"] = appointment_id
        self.appointments_store.setdefault(calendar_owner_id, []).append(appointment)
    
    def get_appointments(self, calendar_owner_id: str) -> List[Dict]:
        """Get all appointments for a user"""
        return self.appointments_store.get(calendar_owner_id, [])
    
    def is_slot_booked(self, calendar_owner_id: str, booking_date: date, slot: time) -> bool:
        """Check if a slot is already booked"""
        appointments = self.appointments_store.get(calendar_owner_id, [])
        return any(
            a["date"] == booking_date and a["start_time"] == slot 
            for a in appointments
        )
    

# Factory function for creating repository instances
def create_booking_repository() -> BaseBookingRepository:
    return InMemoryBookingRepository()
