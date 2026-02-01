#!/bin/bash

# LEOC Docker Management Script

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "LEOC Docker Management Script"
echo "==============================="

case "$1" in
    start)
        echo "Starting LEOC application..."
        cd "$SCRIPT_DIR" && docker-compose up -d
        echo "Application started. Access at http://localhost:5002"
        ;;
    stop)
        echo "Stopping LEOC application..."
        cd "$SCRIPT_DIR" && docker-compose down
        echo "Application stopped."
        ;;
    restart)
        echo "Restarting LEOC application..."
        cd "$SCRIPT_DIR" && docker-compose down && docker-compose up -d
        echo "Application restarted. Access at http://localhost:5002"
        ;;
    logs)
        echo "Showing application logs..."
        cd "$SCRIPT_DIR" && docker-compose logs -f
        ;;
    build)
        echo "Building Docker image..."
        cd "$SCRIPT_DIR" && docker-compose build --no-cache
        echo "Build completed."
        ;;
    status)
        echo "Checking container status..."
        cd "$SCRIPT_DIR" && docker-compose ps
        ;;
    shell)
        echo "Opening shell in the application container..."
        cd "$SCRIPT_DIR" && docker exec -it leoc-app bash
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|build|status|shell}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the application containers"
        echo "  stop    - Stop the application containers"
        echo "  restart - Restart the application containers"
        echo "  logs    - View application logs"
        echo "  build   - Rebuild the Docker image"
        echo "  status  - Show container status"
        echo "  shell   - Open shell in the application container"
        echo ""
        echo "The LEOC application will be available at http://localhost:5002"
        exit 1
        ;;
esac