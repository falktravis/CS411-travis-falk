#!/bin/bash

# Variables
IMAGE_NAME=boxing
CONTAINER_TAG=boxing_container
HOST_PORT=5000
CONTAINER_PORT=5000
DB_VOLUME_PATH=./sql/init_db.sql
BUILD=true

# Check if we need to build the Docker image
if [ "$BUILD" = true ]; then
  echo "Building Docker image..."
  # Build the Docker image
  docker build -t ${IMAGE_NAME}:${CONTAINER_TAG} .
else
  echo "Skipping Docker image build..."
fi

# Check if the database directory exists; if not, create it
if [ ! -d "${DB_VOLUME_PATH}" ]; then
  echo "Creating database directory at ${DB_VOLUME_PATH}..."
  mkdir -p $(dirname "${DB_VOLUME_PATH}")
  touch "${DB_VOLUME_PATH}"
fi

# Stop and remove the running container if it exists
if [ "$(docker ps -q -a -f name=${CONTAINER_TAG})" ]; then
    echo "Stopping running container: ${CONTAINER_TAG}"
    docker stop ${CONTAINER_TAG}

    # Check if the stop was successful
    if [ $? -eq 0 ]; then
        echo "Removing container: ${CONTAINER_TAG}"
        docker rm ${CONTAINER_TAG}
    else
        echo "Failed to stop container: ${CONTAINER_TAG}"
        exit 1
    fi
else
    echo "No running container named ${CONTAINER_TAG} found."
fi

# Run the Docker container with the necessary ports and volume mappings
echo "Running Docker container..."
docker run -d \
  --name ${CONTAINER_TAG} \
  --env-file .env \
  -v $(pwd)/db:/app/db \
  -p ${HOST_PORT}:${CONTAINER_PORT} \
  ${IMAGE_NAME}:${CONTAINER_TAG}

echo "Docker container is running on port ${HOST_PORT}."


