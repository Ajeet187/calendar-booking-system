from datetime import datetime, timedelta, date, time
from typing import List, Optional
from app.repositories.base_repository import BaseBookingRepository
from app.utils.time_utils import TimeUtils
from app.core.exceptions import  ConflictException, NotFoundException, ValidationException
import threading

class BookingService:
    """Service layer for booking operations"""
    
    def __init__(self, repository: BaseBookingRepository, time_utils: Optional[TimeUtils] = None):
        self.repository = repository
        self.time_utils = time_utils or TimeUtils()
        self.locks = {}  # dictionary to hold locks per (calendar_owner_id, date, slot)
        self.locks_lock = threading.Lock()  # lock to protect access to self.locks
        

    def _get_lock_for_key(self, key):
        with self.locks_lock:
            if key not in self.locks:
                self.locks[key] = threading.Lock()
            return self.locks[key]
    
    def set_user_availability(self, calendar_owner_id: str, start_str: str, end_str: str) -> None:
        """Set user availability with validation"""
        try:
            start = self.time_utils.parse_time(start_str)
            end = self.time_utils.parse_time(end_str)
            
            if start >= end:
                raise ValidationException("Start time must be before end time")
            
            self.repository.set_availability(calendar_owner_id, start, end)
        except ValueError as e:
            raise ValidationException(f"Invalid time format: {str(e)}")
    
    def get_available_slots(self, calendar_owner_id: str, for_date: date) -> List[str]:
        """Get available slots for a user on a specific date"""

    # Reject past dates
        if for_date < date.today():
            raise ValidationException("Cannot retrieve slots for a past date")
        
        avail = self.repository.get_availability(calendar_owner_id)
        if not avail:
            raise NotFoundException("User Not Found")
        
        slots = self.time_utils.generate_hourly_slots(avail["start"], avail["end"])
        available = [
            self.time_utils.format_time(slot)
            for slot in slots
            if not self.repository.is_slot_booked(calendar_owner_id, for_date, slot)
        ]
        return available
    
    def book_slot(self, req) -> str:
        """Book a slot with validation"""
        try:
            slot = self.time_utils.parse_time(req.slot_start_time)
            avail = self.repository.get_availability(req.calendar_owner_id)
            
            if not avail:
                raise NotFoundException("User Not Found")
            
            if not (avail["start"] <= slot < avail["end"]):
                raise ValidationException("Invalid time")

            key = (req.calendar_owner_id, req.date, slot)
            lock = self._get_lock_for_key(key)
            with lock:
                if self.repository.is_slot_booked(req.calendar_owner_id, req.date, slot):
                    raise ConflictException("Slot already booked")
                
                appointment = {
                    "invitee_name": req.invitee_name,
                    "invitee_email": req.invitee_email,
                    "date": req.date,
                    "start_time": slot,
                    "end_time": (datetime.combine(req.date, slot) + timedelta(hours=1)).time(),
                    "created_at": datetime.now(),
                    "status": "confirmed"
                }
                self.repository.add_appointment(req.calendar_owner_id, appointment)
                return appointment["id"]
        except ValueError as e:
            raise ValidationException(f"Invalid time format: {str(e)}")
    
    def list_upcoming_appointments(self, calendar_owner_id: str) -> List[dict]:
        """List upcoming appointments for a user"""
        today = date.today()
        appointments = self.repository.get_appointments(calendar_owner_id)
        
        return [
            {
                "id": a.get("id"),
                "invitee_name": a["invitee_name"],
                "invitee_email": a["invitee_email"],
                "date": a["date"],
                "start_time": self.time_utils.format_time(a["start_time"]),
                "end_time": self.time_utils.format_time(a["end_time"]),
                "status": a.get("status", "confirmed")
            }
            for a in appointments if a["date"] >= today
        ]