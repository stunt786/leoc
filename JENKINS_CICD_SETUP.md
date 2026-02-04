# Jenkins CI/CD Pipeline Setup Guide for LEOC Application

## Overview
This guide explains how to set up a complete CI/CD pipeline using Jenkins for your LEOC Flask application with Docker deployment.

## Prerequisites
- Jenkins running on Docker (port 8090)
- Target server accessible via SSH through Tailscale VPN
- GitHub repository for the project
- Docker installed on both Jenkins and target server

## Architecture
```
GitHub → Jenkins (Docker:8090) → Tailscale VPN → Target Server (Docker)
```

## Step 1: Prepare the Target Server

### 1.1 Install Docker on Target Server
```bash
# SSH into your server via Tailscale
ssh leoc@<tailscale-ip>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 1.2 Create Deployment Directory
```bash
# Create app directory
sudo mkdir -p /home/leoc/app
sudo chown -R leoc:leoc /home/leoc

# Create directories for persistent data
mkdir -p /home/leoc/app/instance
mkdir -p /home/leoc/app/static/uploads
mkdir -p /home/leoc/backups
```

### 1.3 Generate SSH Key for Jenkins
```bash
# Generate SSH key on target server
ssh-keygen -t ed25519 -f ~/.ssh/tailscale-ssh-key -N ""

# Add public key to authorized_keys
cat ~/.ssh/tailscale-ssh-key.pub >> ~/.ssh/authorized_keys

# Copy the private key to Jenkins (you'll need this for credential setup)
cat ~/.ssh/tailscale-ssh-key
```

## Step 2: Configure Jenkins

### 2.1 Access Jenkins Dashboard
Open browser and navigate to: `http://localhost:8090`

### 2.2 Install Required Plugins
Go to **Manage Jenkins** → **Manage Plugins** and install:
- Docker Pipeline
- SSH Agent Plugin
- GitHub Integration Plugin
- Pipeline: Stage View

### 2.3 Configure Docker
Go to **Manage Jenkins** → **Global Tool Configuration**:
- Add Docker installation (auto-install)

### 2.4 Add SSH Credentials
Go to **Manage Jenkins** → **Manage Credentials**:
1. Click "Jenkins" under "Stores scoped to Jenkins"
2. Click "Global credentials"
3. Add Credentials:
   - Kind: SSH Username with private key
   - ID: `tailscale-ssh-key`
   - Username: `leoc`
   - Private Key: Paste contents of `~/.ssh/tailscale-ssh-key`
   - Passphrase: (empty if no passphrase)

### 2.5 Add GitHub Credentials (if private repository)
Go to **Manage Jenkins** → **Manage Credentials**:
- Add Credentials:
  - Kind: Username and password
  - ID: `github-credentials`
  - Username: GitHub username
  - Password: GitHub Personal Access Token

## Step 3: Create Jenkins Pipeline Job

### 3.1 Create New Job
1. Click "New Item"
2. Enter name: `leoc-deploy`
3. Select "Pipeline"
4. Click OK

### 3.2 Configure Pipeline
In the Pipeline section:

```groovy
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/yourusername/leoc.git
Credentials: (select github-credentials if private)
Branch: */main (or */master)
Script Path: Jenkinsfile
```

### 3.3 Update Jenkinsfile Configuration
Edit the `Jenkinsfile` in your repository and update:

```groovy
environment {
    SSH_HOST = '100.x.x.x'  // Your Tailscale IP
    REPO_URL = 'https://github.com/yourusername/leoc.git'
}
```

## Step 4: Configure GitHub Webhook

### 4.1 Generate Jenkins API Token
1. Go to Jenkins → Click username → Configure
2. Under "API Token", click "Add new Token"
3. Copy the generated token

### 4.2 Add Webhook to GitHub
1. Go to your GitHub repository → Settings → Webhooks
2. Add webhook:
   - Payload URL: `http://localhost:8090/github-webhook/`
   - Content type: `application/json`
   - Secret: (optional)
   - Events: Push, Pull Request

## Step 5: Set Up GitHub Personal Access Token (if needed)

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic) with:
   - `repo` scope (full control)
   - `admin:repo_hook` scope
3. Copy the token and use it in Jenkins credentials

## Step 6: First Deployment

### 6.1 Manually Trigger Build
1. Go to Jenkins job: `leoc-deploy`
2. Click "Build Now"
3. Watch the build progress in Blue Ocean or Stage View

### 6.2 Monitor Build
- Click on build number → Console Output
- Check for any errors

## Pipeline Stages Explained

| Stage | Description |
|-------|-------------|
| Checkout | Clone code from GitHub |
| Setup Python | Verify Python environment |
| Install Dependencies | Install Python packages from requirements.txt |
| Run Tests | Execute test suite |
| Build Docker | Build Docker image |
| Security Scan | Scan Docker image for vulnerabilities |
| Push to Registry | Push image to Docker registry (optional) |
| Deploy to Server | Deploy container via SSH |
| Health Check | Verify application is running |
| Cleanup | Remove old Docker images |

## Troubleshooting

### Build Fails - SSH Connection
```bash
# Test SSH connection from Jenkins agent
ssh -o StrictHostKeyChecking=no -i /path/to/key leoc@<tailscale-ip>
```

### Docker Build Fails
```bash
# Check Docker is running on Jenkins agent
docker ps

# Check Docker socket mount
docker run -v /var/run/docker.sock:/var/run/docker.sock ...
```

### Deployment Fails - Container Won't Start
```bash
# Check container logs
docker logs leoc-app

# Check port is not in use
netstat -tlnp | grep 5002

# Check environment variables
docker exec leoc-app env
```

### Health Check Fails
```bash
# Check if application is running
curl http://localhost:5002/

# Check Gunicorn process
docker exec leoc-app ps aux | grep gunicorn
```

## Environment Variables

Make sure `.env` file on target server contains:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=sqlite:////app/instance/leoc.db
UPLOAD_FOLDER=/app/static/uploads
CACHE_TIMEOUT=300
```

## Useful Commands

### View Logs
```bash
# Jenkins container logs
docker logs jenkins

# Application logs (on target server)
docker logs leoc-app -f
```

### Restart Jenkins
```bash
docker restart jenkins
```

### Manual Deployment
```bash
# On target server
cd /home/leoc/app
./deploy-jenkins.sh
```

## Security Best Practices

1. **Use Docker Content Trust** for image verification
2. **Regularly update base images** in Dockerfile
3. **Scan images** for vulnerabilities before deployment
4. **Use secrets management** for sensitive data
5. **Limit SSH access** to necessary IPs

## Next Steps

1. Set up automated database migrations
2. Configure monitoring and alerting
3. Set up log aggregation
4. Implement blue-green deployment
5. Add integration tests
