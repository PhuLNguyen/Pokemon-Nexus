# Use the official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies, including Gunicorn and Gevent/WebSocket libs
COPY ./web/requirements.txt  .
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy the application code to the container
COPY ./web .

# Expose the ports used by the internal services (5000 for core, 5001 for real-time)
EXPOSE 5000 5001

# The CMD is no longer needed as the entry point is defined by the 'command' 
# in docker-compose.yaml for each service (Gunicorn/Python).
# CMD ["flask", "run", "--host=0.0.0.0"]