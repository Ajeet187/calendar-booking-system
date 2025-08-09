from typing import Annotated, Optional
from fastapi import Depends
from app.repositories.base_repository import BaseBookingRepository
from app.repositories.booking_repo import create_booking_repository 
from app.services.booking_service import BookingService
from app.utils.time_utils import TimeUtils

# Singleton instances
_repository_instance: Optional[BaseBookingRepository] = None
_service_instance: Optional[BookingService] = None
_time_utils_instance: Optional[TimeUtils] = None

# Repository dependency
def get_booking_repository() -> BaseBookingRepository:
    """Get singleton booking repository instance"""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = create_booking_repository()
    return _repository_instance

# Service dependency
def get_booking_service() -> BookingService:
    """Get singleton booking service instance"""
    global _service_instance
    if _service_instance is None:
        repository = get_booking_repository()
        _service_instance = BookingService(repository)
    return _service_instance

# Time utils dependency
def get_time_utils() -> TimeUtils:
    """Get singleton time utils instance"""
    global _time_utils_instance
    if _time_utils_instance is None:
        _time_utils_instance = TimeUtils()
    return _time_utils_instance
