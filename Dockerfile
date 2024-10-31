# Stage 1: Build stage

# Build stage
FROM python:3.10-slim AS builder

# Set the working directory
WORKDIR /app

# Copy only the requirements file
COPY requirements-cpu.txt .

# Install build dependencies and create virtual environment
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && python -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --no-cache-dir -r requirements-cpu.txt \
    && pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && pip uninstall opencv-python -y \
    && pip install opencv-python-headless==4.10.0.84

# Final stage
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/venv /app/venv

# Copy the application code
COPY . .

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the PATH to use the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Expose the desired port
EXPOSE 8149

# Run the FastAPI app with Uvicorn
CMD ["sh", "-c", ". /app/venv/bin/activate && uvicorn src.api:app --host 0.0.0.0 --port 8149"]