# Use a minimal Python image
FROM python:3.10-slim

# Set environment variables to avoid .pyc files and enable stdout logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Default command to run the Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
