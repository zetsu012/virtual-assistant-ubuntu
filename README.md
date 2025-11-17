# Virtual Assistant for Ubuntu

A voice and text-based virtual assistant with system tray integration for Ubuntu Linux. This application provides hands-free control over your system through natural language commands.

![Virtual Assistant](resources/icon.png)

## Features

### 🎤 Voice Commands
- Speech-to-text recognition using Google Speech API
- Configurable timeout and sensitivity
- Fallback to offline CMU Sphinx recognition
- Real-time audio feedback

### 💬 Text Commands
- Clean dialog interface for text input
- Command history and suggestions
- Keyboard shortcuts for quick access
- Auto-completion support

### 🖥️ System Integration
- Persistent system tray icon in Ubuntu's top panel
- Right-click context menu with quick actions
- Desktop notifications for feedback
- Text-to-speech responses

### ⚡ System Operations
- **Application Control**: Launch and close applications
- **System Control**: Shutdown, restart, lock screen
- **Volume Control**: Adjust system audio levels
- **File Operations**: Open, create, delete, and search files
- **Web Operations**: Search the web and open websites
- **Information Queries**: Time, date, system stats, and more

## Installation

### Prerequisites
- Ubuntu 20.04+ or Debian-based Linux distribution
- Python 3.10+ (recommended)
- Working microphone (for voice commands)
- Internet connection (for Google Speech Recognition)

### Quick Install

1. **Clone or download the repository:**
   ```bash
   git clone <repository-url>
   cd virtual-assistant
   ```

2. **Run the installation script:**
   ```bash
   ./setup.sh
   ```

3. **Launch the application:**
   ```bash
   # Option 1: Using the launcher
   virtual-assistant
   
   # Option 2: Direct execution
   ./venv/bin/python src/main.py
   
   # Option 3: From application menu
   # Look for "Virtual Assistant" in your applications
   ```

### Manual Installation

If you prefer manual installation:

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-dev portaudio19-dev \
       libnotify-bin espeak python3-pyqt5
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python src/main.py
   ```

## Usage

### Starting the Application

The application runs as a system tray icon in Ubuntu's top panel:

- **Left-click** on the tray icon to open text command dialog
- **Right-click** to access the context menu

### Voice Commands

1. Right-click the tray icon and select "Voice Command"
2. Wait for the "Listening..." notification
3. Speak your command clearly
4. The assistant will process and execute your command

### Text Commands

1. Left-click the tray icon or right-click → "Text Command"
2. Type your command in the dialog
3. Press Enter or click "Execute"
4. View the result in the dialog

### Available Commands

#### System Operations
```bash
open firefox          # Launch Firefox browser
open terminal         # Open terminal
close firefox         # Close Firefox
shutdown              # Shutdown system (requires confirmation)
restart               # Restart system (requires confirmation)
lock                  # Lock screen
volume up             # Increase volume
volume down           # Decrease volume
volume mute           # Mute audio
```

#### File Operations
```bash
open file ~/Documents/report.pdf    # Open file with default app
create file notes.txt               # Create new file
delete file ~/tmp/old_file.txt      # Delete file (requires confirmation)
search *.py                         # Search for Python files
```

#### Web Operations
```bash
search python tutorials             # Google search
open website github.com             # Open specific website
https://www.google.com              # Open URL directly
```

#### Information Queries
```bash
time                  # Show current time
date                  # Show current date
cpu usage             # Show CPU statistics
memory usage          # Show memory usage
disk usage            # Show disk usage
system info           # Show system information
help                  # Show available commands
version               # Show application version
```

## Configuration

### Settings File

Configuration is stored in `~/.config/virtual-assistant/settings.json`:

```json
{
  "voice": {
    "timeout": 5,
    "language": "en-US",
    "speech_rate": 150,
    "enabled": true
  },
  "notifications": {
    "enabled": true,
    "duration": 3,
    "sound_enabled": true
  },
  "commands": {
    "confirm_dangerous": true,
    "show_feedback": true,
    "execution_timeout": 30
  }
}
```

### Configuration Options

- **voice.timeout**: Seconds to wait for voice input (default: 5)
- **voice.speech_rate**: TTS speech speed (default: 150)
- **notifications.duration**: Notification display time in seconds (default: 3)
- **commands.confirm_dangerous**: Require confirmation for dangerous commands (default: true)

## Autostart Configuration

To automatically start Virtual Assistant on login:

### Method 1: Using Ubuntu's Startup Applications
1. Open "Startup Applications" from Ubuntu's application menu
2. Click "Add"
3. Enter:
   - **Name**: Virtual Assistant
   - **Command**: `/path/to/virtual-assistant/venv/bin/python /path/to/virtual-assistant/src/main.py`
   - **Comment**: Voice and text-based virtual assistant

### Method 2: Enable Autostart Entry
```bash
# Edit the autostart desktop file
nano ~/.config/autostart/virtual-assistant.desktop

# Change this line:
X-GNOME-Autostart-enabled=false

# To:
X-GNOME-Autostart-enabled=true
```

## Troubleshooting

### Voice Commands Not Working

1. **Check microphone permissions:**
   ```bash
   # Test microphone
   arecord -d 5 test.wav
   aplay test.wav
   ```

2. **Check audio system:**
   ```bash
   pulseaudio --kill
   pulseaudio --start
   ```

3. **Verify PyAudio installation:**
   ```bash
   python3 -c "import pyaudio; print('PyAudio OK')"
   ```

### System Tray Icon Not Appearing

1. **Check if system tray is available:**
   ```bash
   # GNOME users may need to install extensions
   sudo apt install gnome-shell-extension-appindicator
   ```

2. **Restart the application:**
   ```bash
   pkill -f virtual-assistant
   virtual-assistant
   ```

### Notifications Not Working

1. **Check notification service:**
   ```bash
   notify-send "Test" "This is a test notification"
   ```

2. **Check notification settings in Ubuntu Settings**

### Application Won't Start

1. **Check logs:**
   ```bash
   tail -f ~/.local/share/virtual-assistant/assistant.log
   ```

2. **Verify Python dependencies:**
   ```bash
   source venv/bin/activate
   pip list | grep -E "(PyQt5|speech|pyttsx3)"
   ```

3. **Check for missing system packages:**
   ```bash
   sudo apt install --reinstall python3-pyqt5 libnotify-bin
   ```

## Development

### Project Structure

```
virtual-assistant/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── tray_icon.py       # System tray implementation
│   ├── voice_module.py    # Voice command handling
│   ├── text_module.py     # Text command dialog
│   ├── command_processor.py # Command parsing & routing
│   ├── task_handlers.py   # Task execution logic
│   ├── feedback.py        # TTS & notifications
│   └── config_manager.py  # Configuration management
├── config/                # Configuration files
│   └── settings.json      # Default settings
├── resources/             # Resources
│   └── icon.png          # Tray icon
├── requirements.txt       # Python dependencies
├── setup.sh              # Installation script
└── README.md             # This file
```

### Adding New Commands

1. **Add command pattern** in `src/command_processor.py`:
   ```python
   'new_command': r'^new\s+command\s+(.+)$',
   ```

2. **Add handler method** in `src/task_handlers.py`:
   ```python
   def _handle_new_command(self, param: str) -> str:
       # Your implementation here
       return f"Executed new command with: {param}"
   ```

3. **Route to handler** in `execute_command()` method:
   ```python
   elif cmd_type == 'new_command':
       return self._handle_new_command(params[0] if params else "")
   ```

### Testing

Run the application in test mode:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python src/main.py
```

Test individual components:
```bash
# Test voice recognition
python3 -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Say something!')
    audio = r.listen(source)
    print('You said:', r.recognize_google(audio))
"

# Test notifications
notify-send "Virtual Assistant Test" "Notifications are working!"

# Test TTS
python3 -c "
import pyttsx3
engine = pyttsx3.init()
engine.say('Virtual Assistant is working')
engine.runAndWait()
"
```

## Security Considerations

### Command Execution Safety
- Dangerous commands (shutdown, restart, file deletion) require confirmation
- Command inputs are sanitized to prevent injection attacks
- Only whitelisted system commands are executed

### Privacy
- Voice data is processed locally (except for Google Speech API)
- No personal data is stored or transmitted
- Configuration files are stored in user's home directory

### Permissions
- Application runs with user privileges only
- No sudo access required for basic functionality
- System commands may require password confirmation

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for all functions
- Add docstrings to all modules and classes
- Include proper error handling with try-except blocks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

### Known Issues
- Voice recognition requires internet connection for Google Speech API
- Some Ubuntu versions may need additional extensions for system tray
- Microphone access may require permission configuration

### Getting Help
- Check the logs: `~/.local/share/virtual-assistant/assistant.log`
- Review troubleshooting section above
- Open an issue on the project repository

### Feature Requests
- Natural language processing for complex commands
- Custom command macros
- Plugin system for extensibility
- Context awareness based on active window
- Integration with calendar/email services

## Changelog

### Version 1.0.0
- Initial release
- System tray integration
- Voice and text command support
- Basic system operations
- Configuration management
- Installation script

---

**Virtual Assistant for Ubuntu** - Making your system more accessible through voice and text commands.
