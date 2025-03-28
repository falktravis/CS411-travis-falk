#!/bin/bash

# Variables
IMAGE_NAME=Boxing
CONTAINER_TAG=box_container
HOST_PORT=5000
CONTAINER_PORT=5000
DB_VOLUME_PATH=./sql/init_db.sql
BUILD=true

# Check if we need to build the Docker image
if [ "$BUILD" = true ]; then
  echo "Building Docker image..."

else
  echo "Skipping Docker image build..."
fi

# Check if the database directory exists; if not, create it
if [ ! -d "${DB_VOLUME_PATH}" ]; then
  echo "Creating database directory at ${DB_VOLUME_PATH}..."

fi

# Stop and remove the running container if it exists
if [ "$(docker ps -q -a -f name=${IMAGE_NAME}_container)" ]; then
    echo "Stopping running container: ${IMAGE_NAME}_container"


    # Check if the stop was successful
    if [ $? -eq 0 ]; then
        echo "Removing container: ${IMAGE_NAME}_container"

    else
        echo "Failed to stop container: ${IMAGE_NAME}_container"
        exit 1
    fi
else
    echo "No running container named ${IMAGE_NAME}_container found."
fi

# Run the Docker container with the necessary ports and volume mappings
echo "Running Docker container..."

echo "Docker container is running on port ${HOST_PORT}."
