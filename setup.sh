#!/bin/bash

# Immich Home Server Setup Script
# This script sets up all prerequisites and configurations for running Immich on Ubuntu

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Function to check Ubuntu version
check_ubuntu() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot determine OS version"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$NAME" != "Ubuntu" ]]; then
        print_warning "This script is designed for Ubuntu. Proceeding anyway..."
    else
        print_success "Ubuntu detected: $VERSION"
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System packages updated"
}

# Function to install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is already installed"
        return
    fi
    
    print_status "Installing Docker..."
    
    # Install prerequisites
    sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed successfully"
    print_warning "You may need to log out and back in for Docker group permissions to take effect"
}

# Function to install Docker Compose (standalone)
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is already installed"
        return
    fi
    
    print_status "Installing Docker Compose..."
    
    # Get latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    # Download and install
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed successfully"
}

# Function to install additional utilities
install_utilities() {
    print_status "Installing additional utilities..."
    
    sudo apt install -y \
        curl \
        wget \
        git \
        nano \
        htop \
        ufw \
        fail2ban \
        unzip \
        tree
    
    print_success "Additional utilities installed"
}

# Function to configure firewall
configure_firewall() {
    print_status "Configuring UFW firewall..."
    
    # Enable UFW
    sudo ufw --force enable
    
    # Allow SSH (important!)
    sudo ufw allow ssh
    
    # Allow Immich port
    sudo ufw allow 2283/tcp
    
    # Allow HTTP and HTTPS (if you plan to use reverse proxy)
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    print_success "Firewall configured"
    sudo ufw status
}

# Function to configure fail2ban
configure_fail2ban() {
    print_status "Configuring fail2ban..."
    
    sudo systemctl enable fail2ban
    sudo systemctl start fail2ban
    
    print_success "fail2ban configured and started"
}

# Function to create immich directories
setup_immich_directories() {
    print_status "Setting up Immich directories..."
    
    # Create main directory
    mkdir -p ~/immich-server
    cd ~/immich-server
    
    # Create upload directory
    mkdir -p ./library
    
    # Set proper permissions
    chmod 755 ./library
    
    print_success "Immich directories created"
}

# Function to download Immich files
download_immich_files() {
    print_status "Downloading Immich configuration files..."
    
    cd ~/immich-server
    
    # Download docker-compose.yml
    curl -L https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml -o docker-compose.yml
    
    # Download example.env
    curl -L https://github.com/immich-app/immich/releases/latest/download/example.env -o .env
    
    print_success "Immich configuration files downloaded"
}

# Function to configure Immich environment
configure_immich() {
    print_status "Configuring Immich environment..."
    
    cd ~/immich-server
    
    # Generate random password for database
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    
    # Update .env file with generated password
    sed -i "s/DB_PASSWORD=postgres/DB_PASSWORD=${DB_PASSWORD}/" .env
    
    # Set upload location
    sed -i "s|UPLOAD_LOCATION=./library|UPLOAD_LOCATION=$(pwd)/library|" .env
    
    print_success "Immich environment configured"
    print_status "Database password generated and configured"
}

# Function to create systemd service (optional)
create_systemd_service() {
    print_status "Creating systemd service for Immich..."
    
    sudo tee /etc/systemd/system/immich.service > /dev/null <<EOF
[Unit]
Description=Immich Media Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$HOME/immich-server
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable immich
    
    print_success "Systemd service created and enabled"
}

# Function to start Immich
start_immich() {
    print_status "Starting Immich..."
    
    cd ~/immich-server
    docker-compose up -d
    
    print_success "Immich started successfully"
}

# Function to display final information
display_final_info() {
    echo
    echo "=========================================="
    echo "  🎉 Immich Home Server Setup Complete!"
    echo "=========================================="
    echo
    print_success "Immich is running on: http://$(hostname -I | awk '{print $1}'):2283"
    echo
    echo "📁 Immich directory: ~/immich-server"
    echo "📸 Upload directory: ~/immich-server/library"
    echo
    echo "🔧 Management commands:"
    echo "  • Start: docker-compose up -d"
    echo "  • Stop: docker-compose down"
    echo "  • Logs: docker-compose logs -f"
    echo "  • Update: docker-compose pull && docker-compose up -d"
    echo
    echo "🔥 Firewall ports opened:"
    echo "  • SSH (22)"
    echo "  • Immich (2283)"
    echo "  • HTTP (80) and HTTPS (443) for reverse proxy"
    echo
    echo "📖 Next steps:"
    echo "  1. Open http://$(hostname -I | awk '{print $1}'):2283 in your browser"
    echo "  2. Create your admin account"
    echo "  3. Configure mobile apps with server URL"
    echo "  4. Consider setting up a reverse proxy with SSL (Nginx/Caddy)"
    echo
    print_warning "Remember to backup your ~/immich-server directory regularly!"
}

# Main execution
main() {
    echo "=========================================="
    echo "  🏠 Immich Home Server Setup Script"
    echo "=========================================="
    echo
    
    check_root
    check_ubuntu
    
    print_status "Starting Immich home server setup..."
    
    update_system
    install_utilities
    install_docker
    install_docker_compose
    configure_firewall
    configure_fail2ban
    setup_immich_directories
    download_immich_files
    configure_immich
    create_systemd_service
    start_immich
    
    display_final_info
}

# Run main function
main "$@"