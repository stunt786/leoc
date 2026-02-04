#!/bin/bash
# Jenkins Deployment Script for LEOC Application
# This script should be copied to the server and run via SSH

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="leoc-app"
APP_DIR="/home/leoc/app"
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="/home/leoc/backups"

echo -e "${GREEN}=== LEOC Application Deployment Script ===${NC}"
echo "Time: $(date)"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    print_warning "Not running as root. Some operations may require sudo."
fi

# Step 1: Backup current deployment
echo ""
echo -e "${YELLOW}Step 1: Backing up current deployment...${NC}"
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
if [ -d "$APP_DIR" ]; then
    tar -czf $BACKUP_FILE -C $(dirname $APP_DIR) $(basename $APP_DIR) 2>/dev/null || true
    print_status "Backup created: $BACKUP_FILE"
else
    print_warning "No existing deployment found. Skipping backup."
fi

# Step 2: Pull latest code
echo ""
echo -e "${YELLOW}Step 2: Pulling latest code...${NC}"
cd $APP_DIR
if [ -d ".git" ]; then
    git fetch origin
    git pull origin main || git pull origin master
    print_status "Code updated successfully"
else
    print_warning "Not a git repository. Skipping git pull."
fi

# Step 3: Build Docker image
echo ""
echo -e "${YELLOW}Step 3: Building Docker image...${NC}"
docker build -t ${APP_NAME}:latest .
print_status "Docker image built successfully"

# Step 4: Stop existing container
echo ""
echo -e "${YELLOW}Step 4: Stopping existing container...${NC}"
docker stop ${APP_NAME} 2>/dev/null || true
docker rm ${APP_NAME} 2>/dev/null || true
print_status "Existing container stopped and removed"

# Step 5: Run new container
echo ""
echo -e "${YELLOW}Step 5: Starting new container...${NC}"
docker run -d \
    --name ${APP_NAME} \
    --restart unless-stopped \
    -p 5002:5002 \
    -v ${APP_DIR}/instance:/app/instance \
    -v ${APP_DIR}/static/uploads:/app/static/uploads \
    -e FLASK_ENV=production \
    --env-file ${APP_DIR}/.env \
    ${APP_NAME}:latest

# Wait for container to initialize
sleep 5

# Step 6: Verify container is running
echo ""
echo -e "${YELLOW}Step 6: Verifying deployment...${NC}"
if docker ps | grep -q ${APP_NAME}; then
    print_status "Container is running successfully"
else
    print_error "Container failed to start!"
    echo "Container logs:"
    docker logs ${APP_NAME} --tail 50
    exit 1
fi

# Step 7: Health check
echo ""
echo -e "${YELLOW}Step 7: Performing health check...${NC}"
MAX_RETRIES=5
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:5002/ > /dev/null 2>&1; then
        print_status "Health check passed!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    print_warning "Health check failed. Retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Health check failed after $MAX_RETRIES attempts"
    echo "Container logs:"
    docker logs ${APP_NAME} --tail 100
    exit 1
fi

# Step 8: Cleanup
echo ""
echo -e "${YELLOW}Step 8: Cleaning up old images...${NC}"
docker image prune -f
print_status "Cleanup completed"

# Final status
echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Container Status:"
docker ps --filter "name=${APP_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Application URL: http://localhost:5002"
echo "Container logs: docker logs ${APP_NAME}"
echo ""
