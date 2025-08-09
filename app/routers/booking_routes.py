from fastapi import APIRouter, HTTPException, Depends
from typing import List, Annotated
from app.models.schemas import *
from app.services.booking_service import BookingService
from app.core.dependencies import get_booking_service
from app.core.exceptions import BookingException

router = APIRouter()

@router.post("/availability")
def set_availability(
    req: AvailabilityRequest,
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
):
    try:
        booking_service.set_user_availability(req.calendar_owner_id, req.start_time, req.end_time)
        return {"message": "Availability set successfully"}
    except BookingException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/slots")
def get_slots(
    calendar_owner_id: str, 
    for_date: date,
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
):
    try:
        slots = booking_service.get_available_slots(calendar_owner_id, for_date)
        return {"available_slots": slots}
    except BookingException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post("/appointments")
def book_appointment(
    req: AppointmentRequest,
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
):
    try:
        appointment_id = booking_service.book_slot(req)
        return {"message": "Appointment booked", "appointment_id": appointment_id}
    except BookingException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/appointments", response_model=List[AppointmentResponse])
def list_appointments(
    calendar_owner_id: str,
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
):
    try:
        return booking_service.list_upcoming_appointments(calendar_owner_id)
    except BookingException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)