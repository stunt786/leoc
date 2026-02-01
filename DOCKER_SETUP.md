# Docker Setup for LEOC Application

This document explains how to run the Local Emergency Operating Centre (LEOC) application using Docker.

## Prerequisites

- Docker Engine (version 20.10 or later)
- Docker Compose (version 2.0 or later)

## Quick Start

### 1. Clone the repository (if needed)
```bash
git clone <repository-url>
cd leoc
```

### 2. Build and run the application
```bash
# Build the Docker image and start the containers
docker-compose up -d
```

### 3. Access the application
After the containers are running, you can access the application at:
- Main Dashboard: http://localhost:5002
- Disaster Report: http://localhost:5002/disaster-report

## Docker Configuration

### Services
- `leoc-app`: Main Flask application running on port 5002

### Volumes
- `./instance` → `/app/instance`: Persistent storage for SQLite database
- `./static/uploads` → `/app/static/uploads`: Storage for uploaded files
- `.:/app` → `/app`: Application code (for development)

### Environment Variables
The application uses the following environment variables (defined in `.env` file):

- `SECRET_KEY`: Secret key for Flask session management
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `UPLOAD_FOLDER`: Directory for file uploads
- `CACHE_TIMEOUT`: Cache timeout in seconds

## Managing the Containers

### View logs
```bash
docker-compose logs -f leoc-app
```

### Stop the application
```bash
docker-compose down
```

### Rebuild the image (after code changes)
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Access the container shell
```bash
docker exec -it leoc-app bash
```

## Production Notes

For production deployment, consider:
1. Setting strong values for environment variables in `.env`
2. Using a production-grade database instead of SQLite
3. Configuring a reverse proxy (nginx) for SSL termination
4. Setting up automated backups for the instance volume

## Troubleshooting

### Common Issues

1. **Port already in use**: Make sure port 5002 is available
2. **Permission errors**: Ensure the `instance` and `static/uploads` directories have proper permissions
3. **Database initialization**: The first run will initialize the database schema

### Useful Commands

```bash
# Check container status
docker-compose ps

# Check resource usage
docker stats leoc-app

# View application logs
docker-compose logs leoc-app

# Restart just the application container
docker-compose restart leoc-app
```

## Development with Docker

For development, the current setup mounts the source code as a volume, so changes to the code will be reflected immediately in the container. However, you may need to restart the container if you change dependencies in `requirements.txt`.

To add new dependencies:
1. Update `requirements.txt`
2. Rebuild the image: `docker-compose build`
3. Restart the container: `docker-compose up -d`