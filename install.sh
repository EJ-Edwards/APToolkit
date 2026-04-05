#!/bin/bash

# Configuration
REPO_URL="https://github.com/EJ-Edwards/APToolkit.git"
INSTALL_DIR="$HOME/.APToolkit"
BIN_DIR="$HOME/.local/bin"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

install_toolkit() {
    print_status "Starting Hybrid Install (Go + Python)..."
    
    # 1. Setup Directory
    if [ ! -d "$INSTALL_DIR" ]; then
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
    cd "$INSTALL_DIR" || exit

    # 2. Install System Dependencies (Added 'golang')
    print_status "Installing system dependencies..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y git python3 python3-pip python3-venv golang-go
    else
        print_error "Please ensure 'go' and 'python3-venv' are installed manually."
    fi

    # 3. Build the Go C2 Server
    print_status "Compiling Go C2 Server..."
    if command -v go &>/dev/null; then
        go mod tidy 2>/dev/null
        go build -o c2server main.go
        print_status "C2 Binary created successfully."
    else
        print_error "Go compiler not found. C2 features will not work."
    fi

    # 4. Setup Python Virtual Env
    print_status "Setting up Python environment..."
    python3 -m venv venv
    # Installing common dependencies since requirements.txt is missing
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install requests pynput 2>/dev/null

    # 5. Create the Execution Wrapper (Pointing to root.py)
    mkdir -p "$BIN_DIR"
    cat > "$BIN_DIR/APToolkit" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
# Run the root.py using the virtual environment
"$INSTALL_DIR/venv/bin/python3" root.py "\$@"
EOF
    chmod +x "$BIN_DIR/APToolkit"

    # 6. Finalize PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        print_status "Added to PATH. Please run: source ~/.bashrc"
    fi

    print_status "Done! Type 'APToolkit' to launch."
}

install_toolkit
