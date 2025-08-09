from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import time, date

class BaseBookingRepository(ABC):
    """Abstract base class for booking repository operations"""
    
    @abstractmethod
    def set_availability(self, calendar_owner_id: str, start: time, end: time) -> None:
        # set user availability
        pass
    
    @abstractmethod
    def get_availability(self, calendar_owner_id: str) -> Optional[Dict[str, time]]:
        # Get user availability
        pass
    
    @abstractmethod
    def add_appointment(self, calendar_owner_id: str, appointment: Dict) -> None:
        # Add a new appointment
        pass
    
    @abstractmethod
    def get_appointments(self, calendar_owner_id: str) -> List[Dict]:
        # Get all appointments for a user
        pass
    
    @abstractmethod
    def is_slot_booked(self, calendar_owner_id: str, booking_date: date, slot: time) -> bool:
        # Check if a slot is already booked
        pass
