# Use a lightweight Python image  
FROM python:3.10-slim  
  
# Set the working directory in the container  
WORKDIR /app  
  
# Copy requirements file into the container  
COPY requirements.txt . 
  
# Install Python dependencies  
RUN pip install --no-cache-dir -r requirements.txt  
  
# Copy the entire application folder into the container  
COPY ./app /app  
  
# Expose the application port for development  
EXPOSE 9004  
  
# Run the FastAPI application with live reload  
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "9004"]  
