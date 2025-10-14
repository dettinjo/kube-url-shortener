FROM python:3-slim

WORKDIR /app

# Copy only the service folder
COPY . /app/url_shortener_service

# Install dependencies
RUN pip install --no-cache-dir -r /app/url_shortener_service/requirements.txt

# Ensure module is in Python path
ENV PYTHONPATH=/app

# Expose port dynamically
EXPOSE ${SHORTENER_SERVICE_PORT}

# Start the application
CMD ["python", "-m", "url_shortener_service.app"]