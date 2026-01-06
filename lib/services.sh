# Format: "external_hostname|internal_hostname|internal_port"
declare -a SERVICES=(
  "photos.wildharvesthomestead.com|immich.lan|2283"
  "stream.wildharvesthomestead.com|jellyfin.lan|8096"
)

check_root() {
	if [[ $EUID -eq 0 ]]; then
		print_error "This script should not be run as root"
		exit 1
	fi
}

check_os() {
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

update_system() {
	# Skip if apt cache was updated in the last 6 hours
	local apt_cache_file="/var/lib/apt/periodic/update-success-stamp"
	if [[ -f "$apt_cache_file" ]]; then
		local last_update=$(stat -c %Y "$apt_cache_file" 2>/dev/null || echo 0)
		local current_time=$(date +%s)
		local hours_since=$((($current_time - $last_update) / 3600))
		if [[ $hours_since -lt 6 ]]; then
			print_status "System packages updated ${hours_since}h ago, skipping update"
			return
		fi
	fi
	
	print_status "Updating system packages..."
	sudo apt-get update
	sudo apt-get upgrade -y
	sudo apt-get autoremove -y
	print_success "System updated"
}


install_utilities() {
	print_status "Checking for required utilities..."
	
	# List of utilities to install
	local utilities=(
		"curl"
		"wget"
		"git"
		"nano"
		"htop"
		"ufw"
		"fail2ban"
		"unzip"
		"tree"
	)
	
	# Check which utilities are already installed
	local missing=()
	for util in "${utilities[@]}"; do
		# Try command first (for tools with CLI), then fall back to dpkg (for services)
		if ! command -v "$util" &> /dev/null && ! dpkg -l | grep -q "^ii  $util"; then
			missing+=("$util")
		fi
	done
	
	# If all are installed, skip
	if [[ ${#missing[@]} -eq 0 ]]; then
		print_success "All required utilities are already installed"
		return
	fi
	
	print_status "Installing missing utilities: ${missing[*]}"
	sudo apt-get install -y "${missing[@]}"
	print_success "Utilities installed"
}

configure_firewall() {
	if grep -qi microsoft /proc/version; then
		print_warning "Running in WSL - skipping UFW firewall (use Windows Firewall instead)"
		return
	fi
	
	# Check if UFW is already enabled
	if sudo ufw status | grep -q "Status: active"; then
		print_status "Firewall is already configured and active"
		return
	fi
	
	print_status "Configuring UFW firewall..."
	
	# Enable UFW
	sudo ufw --force enable
	
	# Allow SSH (important!)
	sudo ufw allow ssh
	
	# Allow HTTP and HTTPS (for reverse proxy)
	sudo ufw allow 80/tcp
	sudo ufw allow 443/tcp
	
	print_success "Firewall configured"
	sudo ufw status
}

configure_fail2ban() {
	if grep -qi microsoft /proc/version; then
		print_warning "Running in WSL - skipping fail2ban (systemd may not be available)"
		return
	fi
	
	# Check if fail2ban is already running
	if sudo systemctl is-active --quiet fail2ban; then
		print_status "fail2ban is already configured and running"
		return
	fi
	
	print_status "Configuring fail2ban..."
	
	sudo systemctl enable fail2ban
	sudo systemctl start fail2ban
	
	print_success "fail2ban configured and started"
}

install_docker() {
	if command -v docker &> /dev/null; then
		print_success "Docker is already installed"
		return
	fi
	
	print_status "Installing Docker..."
	
	# Install prerequisites
	sudo apt-get update
	sudo apt-get install -y \
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
	
	# Install Docker Engine and Compose
	sudo apt-get update
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	
	# Add current user to docker group
	sudo usermod -aG docker $USER
	
	print_success "Docker installed successfully"
	print_warning "You may need to log out and back in for Docker group permissions to take effect"
}

require_command() {
	local cmd=$1
	local package=$2
	
	# If package not specified, assume it's the same as command
	if [[ -z "$package" ]]; then
		package=$cmd
	fi
	
	if command -v "$cmd" &> /dev/null; then
		return 0
	fi
	
	update_system
	print_status "Installing $package package (required for $cmd command)..."
	sudo apt-get install -y "$package"
	
	if ! command -v "$cmd" &> /dev/null; then
		print_error "Failed to install $package or command $cmd is not available"
		exit 1
	fi
	
	print_success "$package installed"
}