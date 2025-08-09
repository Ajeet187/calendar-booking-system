from typing import Optional

# Base exception for booking-related errors
class BookingException(Exception):
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Exception for validation errors
class ValidationException(BookingException):
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
        
# Exception for conflict errors (e.g., slot already booked)
class ConflictException(BookingException):
    
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


# Exception for user Does not exist
class NotFoundException(BookingException):
    
    def __init__(self, message: str):
        super().__init__(message, status_code=404)