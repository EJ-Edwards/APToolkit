#!/bin/bash

# APToolkit Auto-Installer and Updater
# This script installs APToolkit and provides update notifications

# Configuration
REPO_URL="https://github.com/EJ-Edwards/APToolkit/blob/main/APToolkit.git"
INSTALL_DIR="$HOME/.APToolkit"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
UPDATE_CHECK_INTERVAL=7  # days
LAST_UPDATE_FILE="$INSTALL_DIR/.last_update"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies
install_dependencies() {
    print_status "Checking and installing dependencies..."
    
    # Update package list
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y git python3 python3-pip
    elif command_exists dnf; then
        sudo dnf install -y git python3 python3-pip
    elif command_exists pacman; then
        sudo pacman -Sy --noconfirm git python python-pip
    elif command_exists zypper; then
        sudo zypper refresh
        sudo zypper install -y git python3 python3-pip
    else
        print_error "Unsupported package manager. Please install git, python3, and python3-pip manually."
        exit 1
    fi
    
    # Install Python dependencies
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        pip3 install --user -r "$INSTALL_DIR/requirements.txt"
    else
        print_warning "No requirements.txt found. Continuing anyway..."
    fi
}

# Function to create desktop entry
create_desktop_entry() {
    mkdir -p "$DESKTOP_DIR"
    cat > "$DESKTOP_DIR/APToolkit.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=APToolkit
Comment=Android Pentesting Toolkit
Exec=$BIN_DIR/APToolkit
Icon=$INSTALL_DIR/icon.png
Terminal=true
Categories=Security;Development;
EOF
    chmod +x "$DESKTOP_DIR/APToolkit.desktop"
    print_status "Desktop entry created"
}

# Function to install APToolkit
install_APToolkit() {
    print_header "Installing APToolkit"
    
    # Create installation directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"
    
    # Clone or update the repository
    if [ -d "$INSTALL_DIR/.git" ]; then
        print_status "Repository exists. Updating..."
        cd "$INSTALL_DIR"
        git pull origin main
    else
        print_status "Cloning repository..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    # Install dependencies
    install_dependencies
    
    # Create executable script
    mkdir -p "$BIN_DIR"
    cat > "$BIN_DIR/APToolkit" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 APToolkit.py "\$@"
EOF
    chmod +x "$BIN_DIR/APToolkit"
    
    # Add to PATH if not already there
    if ! echo "$PATH" | grep -q "$BIN_DIR"; then
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
        export PATH="$PATH:$BIN_DIR"
        print_status "Added $BIN_DIR to PATH in .bashrc"
    fi
    
    # Create desktop entry
    create_desktop_entry
    
    # Create last update file
    date +%s > "$LAST_UPDATE_FILE"
    
    print_status "Installation completed successfully!"
    print_status "You can now run 'APToolkit' from the terminal or use the desktop entry."
}

# Function to check for updates
check_for_updates() {
    # Check if it's time to check for updates
    if [ -f "$LAST_UPDATE_FILE" ]; then
        last_update=$(cat "$LAST_UPDATE_FILE")
        current_date=$(date +%s)
        update_interval_seconds=$((UPDATE_CHECK_INTERVAL * 24 * 60 * 60))
        
        if [ $((current_date - last_update)) -lt $update_interval_seconds ]; then
            return 0  # Not time to check yet
        fi
    fi
    
    print_status "Checking for updates..."
    
    # Fetch the latest changes without applying them
    cd "$INSTALL_DIR"
    git fetch origin main
    
    # Check if there are updates
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        print_warning "A new version of APToolkit is available!"
        echo "Current version: $(git log -1 --pretty=format:'%h - %s' $LOCAL)"
        echo "Latest version: $(git log -1 --pretty=format:'%h - %s' $REMOTE)"
        echo ""
        read -p "Would you like to update now? (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Updating APToolkit..."
            git pull origin main
            install_dependencies
            print_status "Update completed successfully!"
        fi
    else
        print_status "APToolkit is up to date."
    fi
    
    # Update the last update time
    date +%s > "$LAST_UPDATE_FILE"
}

# Function to uninstall APToolkit
uninstall_APToolkit() {
    print_header "Uninstalling APToolkit"
    
    read -p "Are you sure you want to uninstall APToolkit? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove installation directory
        rm -rf "$INSTALL_DIR"
        
        # Remove executable
        rm -f "$BIN_DIR/APToolkit"
        
        # Remove desktop entry
        rm -f "$DESKTOP_DIR/APToolkit.desktop"
        
        print_status "APToolkit has been uninstalled successfully."
    else
        print_status "Uninstallation cancelled."
    fi
}

# Main script logic
case "$1" in
    install)
        install_APToolkit
        ;;
    update)
        check_for_updates
        ;;
    uninstall)
        uninstall_APToolkit
        ;;
    *)
        print_header "APToolkit Installer"
        echo "Usage: $0 {install|update|uninstall}"
        echo ""
        echo "Commands:"
        echo "  install   - Install APToolkit"
        echo "  update    - Check for and apply updates"
        echo "  uninstall - Remove APToolkit from your system"
        echo ""
        exit 1
        ;;
esac

exit 0
