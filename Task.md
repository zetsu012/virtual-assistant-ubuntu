# Virtual Assistant Specification for Ubuntu

## Project Overview
A voice and text-based virtual assistant for Ubuntu with a system tray icon for quick access. This is a prototype/base setup to establish core functionality.

---

## Technical Architecture

### Core Components
1. **System Tray Application** - Persistent hover icon in Ubuntu's top panel
2. **Voice Input Module** - Speech-to-text conversion for voice commands
3. **Text Input Module** - GUI/CLI for text-based commands
4. **Command Processor** - Parse and route commands to appropriate handlers
5. **Task Execution Engine** - Execute system tasks based on commands
6. **Feedback System** - Text-to-speech and notification responses

---

## Technology Stack

### Primary Technologies
- **Language**: Python 3.10+
- **System Tray**: `pystray` or `PyQt5/PyQt6` (for Ubuntu compatibility)
- **Speech Recognition**: `SpeechRecognition` library with `PyAudio`
- **Text-to-Speech**: `pyttsx3` or `gTTS`
- **GUI Framework**: `PyQt5` or `Tkinter` (for input dialog)
- **System Operations**: `subprocess`, `os`, `psutil`

### Dependencies
```
PyQt5>=5.15.0
SpeechRecognition>=3.10.0
PyAudio>=0.2.13
pyttsx3>=2.90
pystray>=0.19.4
Pillow>=10.0.0
psutil>=5.9.0
```

---

## Functional Requirements

### 1. System Tray Icon
**Requirements:**
- Icon must appear in Ubuntu's top panel (navbar)
- Right-click menu with options:
  - "Voice Command" - Activate voice input
  - "Text Command" - Open text input dialog
  - "Settings" - Configure assistant
  - "Quit" - Exit application

**Technical Details:**
- Use `pystray` for cross-platform tray icon OR `PyQt5.QtWidgets.QSystemTrayIcon` for native Ubuntu integration
- Icon should be visible at all times when app is running
- Must support Ubuntu 20.04+ GNOME environment

---

### 2. Voice Command Module
**Requirements:**
- Activate via system tray menu or keyboard shortcut
- Listen for voice input for 5 seconds (configurable)
- Convert speech to text
- Process command
- Provide audio/visual feedback

**Technical Implementation:**
```python
import speech_recognition as sr

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=5)
    
    try:
        command = recognizer.recognize_google(audio)
        return command.lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return "error"
```

---

### 3. Text Command Module
**Requirements:**
- Open dialog box via system tray
- Accept text input
- Parse and execute command
- Display result in notification

**Technical Implementation:**
- PyQt5 dialog with single-line input field
- Submit on Enter key or button click
- Non-blocking execution (run in separate thread)

---

### 4. Command Processing System

**Command Categories:**

#### A. System Operations
- `open <application>` - Launch applications (Firefox, VS Code, Terminal)
- `close <application>` - Close running applications
- `shutdown` - Shutdown system
- `restart` - Restart system
- `lock` - Lock screen
- `volume up/down/mute` - Audio control

#### B. File Operations
- `open file <path>` - Open file with default application
- `create file <name>` - Create empty file in current directory
- `delete file <path>` - Delete file (with confirmation)
- `search <filename>` - Find files by name

#### C. Web Operations
- `search <query>` - Open browser with Google search
- `open website <url>` - Open specific URL

#### D. Information Queries
- `time` - Current time
- `date` - Current date
- `weather` - Current weather (requires API integration)
- `cpu usage` - System resource usage
- `memory usage` - RAM usage statistics

**Command Parser Structure:**
```python
def parse_command(command_text):
    command_text = command_text.lower().strip()
    
    # Define command patterns
    patterns = {
        'open_app': r'^open (.+)$',
        'close_app': r'^close (.+)$',
        'system_control': r'^(shutdown|restart|lock)$',
        'volume': r'^volume (up|down|mute)$',
        # Add more patterns
    }
    
    # Match and route to handler
    for cmd_type, pattern in patterns.items():
        match = re.match(pattern, command_text)
        if match:
            return cmd_type, match.groups()
    
    return 'unknown', None
```

---

### 5. Task Execution Handlers

**Example Handlers:**

```python
def handle_open_app(app_name):
    app_commands = {
        'firefox': 'firefox',
        'chrome': 'google-chrome',
        'vscode': 'code',
        'terminal': 'gnome-terminal',
        'files': 'nautilus',
    }
    
    if app_name in app_commands:
        subprocess.Popen([app_commands[app_name]])
        return f"Opening {app_name}"
    return f"Application {app_name} not recognized"

def handle_system_control(action):
    commands = {
        'shutdown': 'shutdown now',
        'restart': 'reboot',
        'lock': 'gnome-screensaver-command -l'
    }
    
    if action in commands:
        subprocess.run(['sudo', commands[action]])
        return f"Executing {action}"
    return "Invalid system command"
```

---

### 6. Feedback System
**Requirements:**
- Text-to-speech for voice responses
- Desktop notifications for text commands
- Error handling with user-friendly messages

**Implementation:**
```python
import pyttsx3
from gi.repository import Notify

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def show_notification(title, message):
    Notify.init("VirtualAssistant")
    notification = Notify.Notification.new(title, message)
    notification.show()
```

---

## Project Structure

```
virtual-assistant/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── tray_icon.py            # System tray implementation
│   ├── voice_module.py         # Voice command handling
│   ├── text_module.py          # Text command handling
│   ├── command_processor.py    # Command parsing & routing
│   ├── task_handlers.py        # Task execution logic
│   └── feedback.py             # TTS & notifications
├── resources/
│   └── icon.png                # Tray icon image
├── config/
│   └── settings.json           # Configuration file
├── requirements.txt
├── setup.sh                    # Installation script
└── README.md
```

---

## Installation & Setup Instructions

### Prerequisites
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-dev portaudio19-dev
sudo apt install -y libnotify-bin espeak
```

### Installation Script (`setup.sh`)
```bash
#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make main script executable
chmod +x src/main.py

echo "Setup complete! Run: python src/main.py"
```

---

## Execution Flow

1. **Startup**: Launch `main.py` → Initialize system tray icon
2. **User Interaction**: Click tray icon → Select "Voice Command" or "Text Command"
3. **Input Processing**: 
   - Voice: Record audio → Convert to text
   - Text: Open input dialog → Get text
4. **Command Parsing**: Analyze command → Match pattern → Extract parameters
5. **Task Execution**: Route to appropriate handler → Execute system operation
6. **Feedback**: Provide response via speech/notification
7. **Loop**: Return to listening state

---

## Autostart Configuration

**Ubuntu Autostart:**
Create file at `~/.config/autostart/virtual-assistant.desktop`
```ini
[Desktop Entry]
Type=Application
Name=Virtual Assistant
Exec=/path/to/virtual-assistant/venv/bin/python /path/to/virtual-assistant/src/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

---

## Configuration File (`settings.json`)

```json
{
  "voice": {
    "timeout": 5,
    "language": "en-US",
    "speech_rate": 150
  },
  "hotkeys": {
    "voice_command": "<Ctrl>+<Alt>+V",
    "text_command": "<Ctrl>+<Alt>+T"
  },
  "notifications": {
    "enabled": true,
    "duration": 3
  }
}
```

---

## Security Considerations

1. **Sudo Commands**: Require password confirmation for critical operations (shutdown/restart)
2. **File Deletion**: Implement confirmation dialog before deleting files
3. **Command Validation**: Sanitize inputs to prevent command injection
4. **Restricted Commands**: Whitelist allowed system commands

---

## Testing Checklist

- [ ] System tray icon appears on Ubuntu navbar
- [ ] Voice command activation works
- [ ] Text command dialog opens and closes properly
- [ ] Commands parse correctly
- [ ] Applications launch successfully
- [ ] System operations execute (with proper permissions)
- [ ] TTS feedback works
- [ ] Desktop notifications display
- [ ] Error handling functions correctly
- [ ] Application exits cleanly

---

## Known Limitations

1. **Voice Recognition**: Requires internet for Google Speech Recognition
2. **Permissions**: Some system commands require sudo access
3. **Ubuntu Version**: Tested on Ubuntu 20.04+ with GNOME
4. **Microphone**: Must have working audio input device

---

## Future Enhancements (Post-Prototype)

- Natural language processing for complex commands
- Custom command macros
- Plugin system for extensibility
- Context awareness (based on active window)
- Integration with calendar/email
- Wake word detection for hands-free activation

---

## Command Reference for Coding Agent

**Implement this spec with the following priorities:**

1. **Phase 1**: System tray icon + basic text command input
2. **Phase 2**: Command processor + 5-10 basic task handlers
3. **Phase 3**: Voice input module + speech recognition
4. **Phase 4**: TTS feedback + notification system
5. **Phase 5**: Configuration system + autostart setup

**Code Quality Requirements:**
- Use type hints for all functions
- Add docstrings to all modules/classes
- Implement proper error handling with try-except blocks
- Log all operations to `assistant.log`
- Follow PEP 8 style guidelines

**Testing Requirements:**
- Test on Ubuntu 22.04 LTS
- Verify all 10 base commands work
- Ensure clean startup/shutdown
- Test with both voice and text input