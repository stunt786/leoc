#!/bin/bash
# Quick Setup Script for Jenkins CI/CD
# Run this on your target server

set -e

echo "=========================================="
echo "  LEOC Jenkins CI/CD Quick Setup"
echo "=========================================="
echo ""

# Configuration
TAILSCALE_IP=""
GITHUB_REPO=""
JENKINS_URL="http://localhost:8090"
APP_DIR="/home/leoc/app"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "Docker is installed"
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    print_status "Git is installed"
}

# Setup deployment directory
setup_directory() {
    echo ""
    echo "Setting up deployment directory..."
    
    mkdir -p $APP_DIR/instance
    mkdir -p $APP_DIR/static/uploads
    mkdir -p /home/leoc/backups
    
    print_status "Directories created"
}

# Generate SSH key
generate_ssh_key() {
    echo ""
    echo "Generating SSH key for Jenkins..."
    
    if [ -f ~/.ssh/tailscale-ssh-key ]; then
        print_warning "SSH key already exists. Skipping generation."
        cat ~/.ssh/tailscale-ssh-key.pub
        return
    fi
    
    ssh-keygen -t ed25519 -f ~/.ssh/tailscale-ssh-key -N ""
    
    # Add to authorized_keys
    cat ~/.ssh/tailscale-ssh-key.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    
    print_status "SSH key generated"
    echo ""
    echo "=== COPY THIS PRIVATE KEY TO JENKINS ==="
    cat ~/.ssh/tailscale-ssh-key
    echo ""
    echo "=== END PRIVATE KEY ==="
}

# Copy deployment files
copy_files() {
    echo ""
    echo "Copying deployment files..."
    
    # Copy scripts
    cp deploy-jenkins.sh $APP_DIR/
    chmod +x $APP_DIR/deploy-jenkins.sh
    
    # Copy docker-compose
    cp docker-compose.yml $APP_DIR/
    
    # Copy .env.production as .env
    if [ -f .env.production.example ]; then
        cp .env.production.example $APP_DIR/.env
        print_warning "Please update $APP_DIR/.env with your actual values"
    fi
    
    print_status "Files copied to $APP_DIR"
}

# Setup Docker network
setup_docker() {
    echo ""
    echo "Setting up Docker..."
    
    # Create Docker network if not exists
    docker network create leoc-network 2>/dev/null || true
    
    print_status "Docker network ready"
}

# Print next steps
print_next_steps() {
    echo ""
    echo "=========================================="
    echo "  Setup Complete! Next Steps:"
    echo "=========================================="
    echo ""
    echo "1. Update Jenkinsfile with your Tailscale IP:"
    echo "   SSH_HOST = '<your-tailscale-ip>'"
    echo ""
    echo "2. In Jenkins Dashboard:"
    echo "   - Install required plugins"
    echo "   - Add SSH credentials (use the private key above)"
    echo "   - Create a new Pipeline job"
    echo "   - Point to your GitHub repository"
    echo ""
    echo "3. Setup GitHub Webhook:"
    echo "   - Payload URL: $JENKINS_URL/github-webhook/"
    echo "   - Content type: application/json"
    echo ""
    echo "4. Update .env file at $APP_DIR/.env with your values"
    echo ""
    echo "5. Initial deployment:"
    echo "   cd $APP_DIR && ./deploy-jenkins.sh"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    setup_directory
    generate_ssh_key
    copy_files
    setup_docker
    print_next_steps
}

main "$@"
