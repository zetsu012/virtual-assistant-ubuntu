#!/bin/bash

# Virtual Assistant for Ubuntu - Installation Script
# This script sets up the virtual assistant with all dependencies

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons."
   print_error "Please run as a regular user. The script will ask for sudo password when needed."
   exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_status "Starting Virtual Assistant installation..."
print_status "Installation directory: $SCRIPT_DIR"

# Check if we're on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    print_error "This script is designed for Ubuntu/Debian systems."
    print_error "apt package manager not found."
    exit 1
fi

# Update package list
print_status "Updating package list..."
sudo apt update

# Install system dependencies
print_status "Installing system dependencies..."

# Basic Python and development tools
sudo apt install -y python3 python3-pip python3-dev python3-venv

# Audio dependencies for speech recognition
sudo apt install -y portaudio19-dev python3-pyaudio

# System notification dependencies
sudo apt install -y libnotify-bin gir1.2-notify-0.7

# Text-to-speech dependencies
sudo apt install -y espeak espeak-data

# GUI dependencies (PyQt5)
sudo apt install -y python3-pyqt5
# Note: python3-pyqt5-dev is optional and may not be available in all repositories
# It's only needed for development, not for running the application

# System utilities
sudo apt install -y pulseaudio pulseaudio-utils alsa-utils

# Check if Python 3.10+ is available
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Found Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 0 ]]; then
    print_warning "Python 3.10+ is recommended. Found: $PYTHON_VERSION"
    print_warning "Some features may not work correctly with older Python versions."
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Removing it..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p ~/.local/share/virtual-assistant
mkdir -p ~/.config/virtual-assistant
mkdir -p ~/.local/bin

# Copy configuration files
print_status "Setting up configuration..."
if [ -f "config/settings.json" ]; then
    cp config/settings.json ~/.config/virtual-assistant/
    print_success "Configuration file installed"
else
    print_warning "Default configuration file not found, will be created on first run"
fi

# Create launcher script
print_status "Creating application launcher..."
cat > ~/.local/bin/virtual-assistant << 'EOF'
#!/bin/bash
# Virtual Assistant launcher script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    python "$SCRIPT_DIR/src/main.py" "$@"
else
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please run the installation script again."
    exit 1
fi
EOF

chmod +x ~/.local/bin/virtual-assistant

# Create desktop entry for application menu
print_status "Creating desktop entry..."
cat > ~/.local/share/applications/virtual-assistant.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Virtual Assistant
Comment=A voice and text-based virtual assistant for Ubuntu
Exec=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/src/main.py
Icon=$SCRIPT_DIR/resources/icon.png
Terminal=false
Categories=Utility;Office;
StartupNotify=true
EOF

# Create autostart entry (disabled by default)
print_status "Creating autostart entry..."
cat > ~/.config/autostart/virtual-assistant.desktop << EOF
[Desktop Entry]
Type=Application
Name=Virtual Assistant
Comment=A voice and text-based virtual assistant for Ubuntu
Exec=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/src/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=false
EOF

# Test microphone access
print_status "Testing microphone access..."
if python3 -c "
import speech_recognition as sr
try:
    r = sr.Recognizer()
    mic = sr.Microphone()
    print('Microphone access: OK')
except Exception as e:
    print(f'Microphone access failed: {e}')
    exit(1)
" 2>/dev/null; then
    print_success "Microphone access test passed"
else
    print_warning "Microphone access test failed. Voice commands may not work."
    print_warning "Please check your microphone permissions and audio setup."
fi

# Test notification system
print_status "Testing notification system..."
if notify-send "Virtual Assistant" "Installation test notification" 2>/dev/null; then
    print_success "Notification system test passed"
else
    print_warning "Notification system test failed. Desktop notifications may not work."
fi

# Create a simple tray icon placeholder if it doesn't exist
if [ ! -f "resources/icon.png" ]; then
    print_status "Creating placeholder tray icon..."
    mkdir -p resources
    # Create a simple SVG icon and convert to PNG if possible
    cat > resources/icon.svg << 'EOF'
<svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="30" fill="#4285f4"/>
  <circle cx="32" cy="24" r="8" fill="white"/>
  <path d="M20 40 Q32 48 44 40" stroke="white" stroke-width="3" fill="none"/>
  <circle cx="20" cy="32" r="3" fill="white"/>
  <circle cx="44" cy="32" r="3" fill="white"/>
</svg>
EOF
    
    # Try to convert SVG to PNG if convert is available
    if command -v convert &> /dev/null; then
        convert resources/icon.svg resources/icon.png 2>/dev/null || true
    fi
    
    # If PNG conversion failed, copy SVG as PNG (some systems can handle SVG icons)
    if [ ! -f "resources/icon.png" ]; then
        cp resources/icon.svg resources/icon.png
    fi
fi

# Set up permissions
print_status "Setting up permissions..."
chmod +x src/main.py
chmod -R 755 .

# Print installation summary
echo ""
print_success "Virtual Assistant installation completed!"
echo ""
echo -e "${BLUE}Installation Summary:${NC}"
echo "  • Application directory: $SCRIPT_DIR"
echo "  • Virtual environment: $SCRIPT_DIR/venv"
echo "  • Configuration: ~/.config/virtual-assistant/"
echo "  • Logs: ~/.local/share/virtual-assistant/"
echo "  • Launcher: ~/.local/bin/virtual-assistant"
echo ""
echo -e "${BLUE}To run the application:${NC}"
echo "  1. From terminal: $SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/src/main.py"
echo "  2. Using launcher: virtual-assistant"
echo "  3. From application menu (look for 'Virtual Assistant')"
echo ""
echo -e "${BLUE}To enable autostart:${NC}"
echo "  1. Open 'Startup Applications' in Ubuntu"
echo "  2. Enable 'Virtual Assistant'"
echo "  3. Or edit ~/.config/autostart/virtual-assistant.desktop"
echo ""
echo -e "${BLUE}Troubleshooting:${NC}"
echo "  • If voice commands don't work, check microphone permissions"
echo "  • If notifications don't work, check system notification settings"
echo "  • Logs are available at: ~/.local/share/virtual-assistant/assistant.log"
echo ""
print_warning "Note: Voice recognition requires internet connection for Google Speech API."
print_warning "For offline recognition, install CMU Sphinx: pip install PocketSphinx"
echo ""

# Ask if user wants to run the application now
read -p "Would you like to start Virtual Assistant now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting Virtual Assistant..."
    source venv/bin/activate
    python src/main.py
fi

print_success "Installation and setup complete!"
