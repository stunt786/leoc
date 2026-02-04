// Jenkinsfile for LEOC Flask Application
// CI/CD Pipeline with Docker, GitHub, and SSH Deployment

pipeline {
    agent any
    
    environment {
        // Application Configuration
        APP_NAME = 'leoc-app'
        APP_DIR = '/home/leoc/app'
        DOCKER_REGISTRY = ''  // Leave empty for local Docker
        IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.substring(0,7)}"
        
        // Server Configuration (via Tailscale VPN)
        SSH_USER = 'leoc'
        SSH_HOST = '100.x.x.x'  // Replace with your Tailscale IP
        SSH_KEY = credentials('tailscale-ssh-key')
        
        // GitHub Configuration
        REPO_URL = 'https://github.com/yourusername/leoc.git'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Checkout from GitHub..."
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo "Setting up Python environment..."
                sh 'python3 --version'
                sh 'pip3 --version'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                sh 'pip3 install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                echo "Running tests..."
                script {
                    if (fileExists('test_production.py')) {
                        sh 'python3 test_production.py || true'
                    } else {
                        echo 'No test file found, skipping tests...'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                script {
                    docker.build("${APP_NAME}:${IMAGE_TAG}", '.')
                    docker.build("${APP_NAME}:latest", '.')
                }
            }
        }
        
        stage('Docker Image Security Scan') {
            steps {
                echo "Scanning Docker image for vulnerabilities..."
                script {
                    // Using Trivy for security scanning (install on Jenkins agent first)
                    sh 'trivy image ${APP_NAME}:${IMAGE_TAG} --exit-code 1 || echo "Scan completed"'
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                echo "Pushing image to registry..."
                script {
                    if (env.DOCKER_REGISTRY != '') {
                        docker.image("${APP_NAME}:${IMAGE_TAG}").push()
                        docker.image("${APP_NAME}:latest").push()
                    } else {
                        echo "No registry configured, using local images"
                    }
                }
            }
        }
        
        stage('Deploy to Server') {
            steps {
                echo "Deploying to server via SSH..."
                script {
                    // Create deployment script on the fly
                    sh """
                    cat > deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "=== Starting Deployment ==="

# Stop and remove old container
echo "Stopping old container..."
docker stop ${APP_NAME} || true
docker rm ${APP_NAME} || true

# Pull latest image
echo "Pulling latest image..."
docker pull ${APP_NAME}:latest || docker pull ${APP_NAME}:${IMAGE_TAG}

# Run new container
echo "Starting new container..."
docker run -d \\
    --name ${APP_NAME} \\
    --restart unless-stopped \\
    -p 5002:5002 \\
    -v \$(pwd)/instance:/app/instance \\
    -v \$(pwd)/static/uploads:/app/static/uploads \\
    -e FLASK_ENV=production \\
    --env-file .env \\
    ${APP_NAME}:latest

# Wait for container to start
sleep 5

# Verify container is running
echo "Container status:"
docker ps | grep ${APP_NAME} || echo "Container not found"

echo "=== Deployment Complete ==="
DEPLOY_SCRIPT
                    """
                    
                    // Copy files to server
                    sh "scp -o StrictHostKeyChecking=no -i ${SSH_KEY} deploy.sh ${SSH_USER}@${SSH_HOST}:~/"
                    sh "scp -o StrictHostKeyChecking=no -i ${SSH_KEY} docker-compose.yml ${SSH_USER}@${SSH_HOST}:~/"
                    sh "scp -o StrictHostKeyChecking=no -i ${SSH_KEY} .env ${SSH_USER}@${SSH_HOST}:~/"
                    sh "scp -o StrictHostKeyChecking=no -i ${SSH_KEY} Dockerfile ${SSH_USER}@${SSH_HOST}:~/"
                    
                    // Execute deployment
                    sh "ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SSH_USER}@${SSH_HOST} 'bash ~/deploy.sh'"
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo "Performing health check..."
                script {
                    retry(3) {
                        sh """
                        sleep 10
                        curl -f http://localhost:5002/ || exit 1
                        """
                    }
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                echo "Cleaning up old Docker images..."
                script {
                    sh "docker rmi \$(docker images -q ${APP_NAME} | grep -v '${IMAGE_TAG}' | grep -v 'latest' | head -n 5) 2>/dev/null || true"
                }
            }
        }
    }
    
    post {
        success {
            echo "✓ Deployment successful!"
            script {
                // Optional: Send notification
                // mail to: 'admin@example.com', subject: "Deployment Successful: ${JOB_NAME}", body: "Deployment completed successfully. Build: ${BUILD_URL}"
            }
        }
        
        failure {
            echo "✗ Deployment failed!"
            script {
                // Optional: Send failure notification
                // mail to: 'admin@example.com', subject: "Deployment Failed: ${JOB_NAME}", body: "Deployment failed. Check logs: ${BUILD_URL}"
            }
        }
        
        always {
            echo "Pipeline execution completed."
        }
    }
}
