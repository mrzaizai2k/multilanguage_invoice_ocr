FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory (app code) into the container
COPY . /app

# Update and install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    python3-venv

# Create and activate a virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python packages in the virtual environment
RUN . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements-cpu.txt && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip uninstall opencv-python -y && \
    pip install opencv-python-headless

# Expose the desired port for the app (8149 in this case)
EXPOSE 8149

# Run the FastAPI app with Uvicorn
CMD ["sh", "-c", ". /app/venv/bin/activate && uvicorn src.api:app --host 0.0.0.0 --port 8149"]