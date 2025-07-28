# Use a lightweight Python base image  
FROM python:3.10-slim
  
# Set the working directory in the container  
WORKDIR /app  
  
# Copy requirements file into the container  
COPY requirements.txt .  
  
# Install Python dependencies globally in the container  
RUN pip install --no-cache-dir -r requirements.txt
  
# The entrypoint can be overridden in docker-compose.yml  
CMD ["python"]  # Default command, runs `python` itself.  
