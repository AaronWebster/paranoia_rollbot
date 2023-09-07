# Use Python 3.10.9 as a base image
FROM python:3.10.9-slim-buster

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir numpy discord.py

# Run the script when the container launches
CMD ["python", "./rollbot.py"]

