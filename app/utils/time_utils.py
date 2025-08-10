from datetime import datetime, timedelta, time, date
from typing import List

class TimeUtils:
    
    @staticmethod
    def parse_time(t: str) -> time:
        """Parse time string to time object"""
        return datetime.strptime(t, "%H:%M").time()
    
    @staticmethod
    def format_time(t: time) -> str:
        """Format time object to string"""
        return t.strftime("%H:%M")
    
    @staticmethod
    def generate_hourly_slots(start: time, end: time) -> List[time]:
        """Generate hourly time slots between start and end times"""
        slots = []
        current = datetime.combine(date.today(), start)
        end_dt = datetime.combine(date.today(), end)
        
        while current + timedelta(hours=1) <= end_dt:
            slots.append(current.time())
            current += timedelta(hours=1)
        
        return slots
    
    @staticmethod
    def is_valid_time_format(time_str: str) -> bool:
        """Validate time string format (HH:00 only)"""
        try:
            parsed = datetime.strptime(time_str, "%H:%M")
            # Ensure minutes are exactly 00
            return parsed.minute == 0
        except ValueError:
            return False
    
    @staticmethod
    def get_duration_between(start: time, end: time) -> timedelta:
        """Get duration between two times"""
        start_dt = datetime.combine(date.today(), start)
        end_dt = datetime.combine(date.today(), end)
        return end_dt - start_dt