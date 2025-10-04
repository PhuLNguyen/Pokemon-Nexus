# Use the official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY ./web/requirements.txt  .
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy the application code to the container
COPY ./web .

# Expose the port that Flask runs on
EXPOSE 5000

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]