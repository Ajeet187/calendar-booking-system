try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from typing import Optional

class Settings(BaseSettings):    
    # Application settings
    app_name: str = "Calendar Booking System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings (for future use)
    database_url: Optional[str] = None
    
    # Time settings
    default_slot_duration_minutes: int = 60
    
    # Booking settings
    max_advance_booking_days: int = 365
    
    # Rate limiting (for future use)
    rate_limit_per_minute: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
