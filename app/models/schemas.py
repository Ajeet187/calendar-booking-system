from pydantic import BaseModel, validator
from datetime import date, timedelta
from typing import Optional
from app.core.config import get_settings
from app.utils.time_utils import TimeUtils
settings = get_settings()


class AvailabilityRequest(BaseModel):
    calendar_owner_id: str
    start_time: str
    end_time: str
    
    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        if not TimeUtils.is_valid_time_format(v):
            raise ValueError('Time must be in HH:00 format')
        return v
    
    @validator('calendar_owner_id')
    def validate_calendar_owner_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Calendar owner ID cannot be empty')
        return v.strip()

class AppointmentRequest(BaseModel):
    calendar_owner_id: str
    invitee_name: str
    invitee_email: str
    date: date
    slot_start_time: str
    
    @validator('slot_start_time')
    def validate_time_format(cls, v):
        if not TimeUtils.is_valid_time_format(v):
            raise ValueError('Time must be in HH:00 format')
        return v
    
    @validator('invitee_name')
    def validate_invitee_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Invitee name cannot be empty')
        return v.strip()
    

    @validator('date')
    def validate_date_within_range(cls, v):
        today = date.today()
        settings = get_settings()

        if v < today:
            raise ValueError('Cannot book appointments in the past')

        if v > today + timedelta(days=365):
            raise ValueError(
                f'Cannot book more than {settings.max_advance_booking_days} days in advance'
            )
        return v

class AppointmentResponse(BaseModel):
    id: Optional[str] = None
    invitee_name: str
    invitee_email: str
    date: date
    start_time: str
    end_time: str
    status: str = "confirmed"

class AvailabilityResponse(BaseModel):
    calendar_owner_id: str
    start_time: str
    end_time: str
    available_hours: int
