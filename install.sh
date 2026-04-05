#!/bin/bash

# APToolkit Auto-Installer and Updater
# This script installs APToolkit and provides update notifications

# Configuration - FIXED: Correct Git URL
REPO_URL="https://github.com/EJ-Edwards/APToolkit.git"
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
print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

command_exists() { command -v "$1" >/dev/null 2>&1; }

# Function to install dependencies and setup Venv
install_dependencies() {
    print_status "Checking and installing system dependencies..."
    
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y git python3 python3-pip python3-venv
    elif command_exists dnf; then
        sudo dnf install -y git python3 python3-pip
    elif command_exists pacman; then
        sudo pacman -Sy --noconfirm git python python-pip
    else
        print_warning "Ensure git, python3, and venv are installed manually."
    fi
    
    # Setup Virtual Environment - Best Practice
    print_status "Setting up Python virtual environment..."
    python3 -m venv "$INSTALL_DIR/venv"
    
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        print_status "Installing Python requirements..."
        "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
        "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    else
        print_warning "No requirements.txt found."
    fi
}

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

install_APToolkit() {
    print_header "Installing APToolkit"
    
    mkdir -p "$INSTALL_DIR"
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        print_status "Repository exists. Updating..."
        cd "$INSTALL_DIR" && git pull origin main
    else
        print_status "Cloning repository..."
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
    
    install_dependencies
    
    # Create executable wrapper - FIXED: Uses Venv Python
    mkdir -p "$BIN_DIR"
    cat > "$BIN_DIR/APToolkit" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
"$INSTALL_DIR/venv/bin/python3" APToolkit.py "\$@"
EOF
    chmod +x "$BIN_DIR/APToolkit"
    
    # Add to PATH (only if not present)
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        if ! grep -q "$BIN_DIR" "$HOME/.bashrc"; then
            echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
            print_status "Added $BIN_DIR to PATH in .bashrc. Restart terminal or run 'source ~/.bashrc'"
        fi
    fi
    
    create_desktop_entry
    date +%s > "$LAST_UPDATE_FILE"
    print_status "Installation completed successfully!"
}

check_for_updates() {
    if [ ! -d "$INSTALL_DIR/.git" ]; then
        print_error "APToolkit is not installed."
        exit 1
    fi

    cd "$INSTALL_DIR" || exit
    print_status "Checking for updates..."
    git fetch origin main
    
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        print_warning "A new version is available!"
        read -p "Update now? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git pull origin main
            install_dependencies
            print_status "Updated successfully."
        fi
    else
        print_status "Already up to date."
    fi
    date +%s > "$LAST_UPDATE_FILE"
}

uninstall_APToolkit() {
    print_header "Uninstalling APToolkit"
    read -p "Are you sure? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        rm -f "$BIN_DIR/APToolkit"
        rm -f "$DESKTOP_DIR/APToolkit.desktop"
        print_status "Uninstalled."
    fi
}

case "$1" in
    install)   install_APToolkit ;;
    update)    check_for_updates ;;
    uninstall) uninstall_APToolkit ;;
    *)
        echo "Usage: $0 {install|update|uninstall}"
        exit 1
        ;;
esac
