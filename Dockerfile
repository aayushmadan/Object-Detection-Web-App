# Stage 1: Builder
FROM python:3.9-slim AS builder

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3.9-slim AS runner

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/venv venv

# Copy the application files
COPY functions/ functions/
COPY yolov8n.pt yolov8n.pt

# Set up environment variables
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=functions/app.py

# Expose the application port
EXPOSE 8080

# Start the Flask application using Gunicorn
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "functions.app:app"]
