FROM python:3.11-slim

# Set the working directory to /app (creates the directory if it doesn't exist)
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Update the apt package list and upgrade packages,
# then clean up to reduce image size.
RUN apt-get update -y && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for the application
EXPOSE 8080

# Start the uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


