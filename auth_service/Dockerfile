FROM python:3-slim

WORKDIR /app

# Copy only the service folder
COPY . /app/auth_service

# Install dependencies
RUN pip install --no-cache-dir -r /app/auth_service/requirements.txt

# Ensure module is in Python path
ENV PYTHONPATH=/app

# Expose port dynamically
EXPOSE ${AUTH_SERVICE_PORT}

# Start the application
CMD ["python", "-m", "auth_service.app"]