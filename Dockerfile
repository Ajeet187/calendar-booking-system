# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app source code
COPY . .

# Expose port (default for uvicorn)
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
