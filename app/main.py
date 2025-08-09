from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import booking_routes
from app.core.config import get_settings
from app.core.exceptions import BookingException
import time

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(booking_routes.router, prefix="/api/v1", tags=["booking"])

# Global exception handler
@app.exception_handler(BookingException)
async def booking_exception_handler(request: Request, exc: BookingException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
    }

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
    }