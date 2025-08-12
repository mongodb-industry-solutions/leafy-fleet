# Use a lightweight Python base image  
FROM python:3.10-slim  
  
# Set the working directory in the container  
WORKDIR /app  
  
# Copy everything from `./app` into `/app` (including requirements.txt)  
COPY ./app /app  
  
# Install dependencies globally in the container  
RUN pip install --no-cache-dir -r requirements.txt  
  
# Copy the application code into the container  
COPY ./app /app  
  
# The default command to run the FastAPI application  
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  
