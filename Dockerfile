# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the start script executable
# RUN chmod +x bin/start.sh

# # Set entrypoint
# ENTRYPOINT ["bin/start.sh"]
