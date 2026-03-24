# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8082

# Set Environment Variables for Production
ENV HOST=0.0.0.0
ENV PORT=8082
ENV LOG_LEVEL=INFO

# Command to run the application
# We use uvicorn directly for better production handling
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8082"]
