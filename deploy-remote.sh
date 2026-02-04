#!/bin/bash
# Remote deployment script (run on target server)
# Usage: ./deploy-remote.sh <image-tag>

set -e

IMAGE_TAG="${1:-latest}"
APP_NAME="leoc-app"
APP_DIR="/home/leoc/app"

echo "=== Starting Deployment ==="
echo "Image tag: $IMAGE_TAG"
echo ""

# Stop and remove old container
echo "Stopping old container..."
docker stop $APP_NAME 2>/dev/null || true
docker rm $APP_NAME 2>/dev/null || true

# Build new image on server
echo "Building Docker image..."
cd $APP_DIR
docker build -t ${APP_NAME}:${IMAGE_TAG} .

# Run new container
echo "Starting new container..."
docker run -d \
    --name $APP_NAME \
    --restart unless-stopped \
    -p 5002:5002 \
    -v ${APP_DIR}/instance:/app/instance \
    -v ${APP_DIR}/static/uploads:/app/static/uploads \
    -e FLASK_ENV=production \
    --env-file ${APP_DIR}/.env \
    ${APP_NAME}:${IMAGE_TAG}

# Wait for container to start
sleep 5

# Verify container is running
echo ""
echo "Container status:"
docker ps | grep $APP_NAME || echo "Container not running!"

echo ""
echo "=== Deployment Complete ==="
echo "Container logs: docker logs $APP_NAME"
