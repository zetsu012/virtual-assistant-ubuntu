"""
Task Handlers for Virtual Assistant
Implements the actual execution of various system tasks.
"""

import os
import subprocess
import datetime
import psutil
import logging
import shutil
import glob
from typing import Optional, Tuple, Dict, Any
import urllib.parse


class TaskHandler:
    """Handles execution of various system tasks."""
    
    def __init__(self, config_manager, feedback_manager):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.feedback_manager = feedback_manager
        
        # Application command mappings
        self.app_commands = {
            'firefox': 'firefox',
            'chrome': 'google-chrome',
            'google chrome': 'google-chrome',
            'chromium': 'chromium-browser',
            'vscode': 'code',
            'visual studio code': 'code',
            'terminal': 'gnome-terminal',
            'console': 'gnome-terminal',
            'files': 'nautilus',
            'file manager': 'nautilus',
            'calculator': 'gnome-calculator',
            'text editor': 'gedit',
            'gedit': 'gedit',
            'music': 'rhythmbox',
            'rhythmbox': 'rhythmbox',
            'settings': 'gnome-control-center',
            'system settings': 'gnome-control-center',
        }
        
        self.logger.info("Task handler initialized")
    
    def execute_command(self, cmd_type: str, params: Optional[Tuple]) -> str:
        """
        Execute a command based on its type and parameters.
        
        Args:
            cmd_type: The type of command to execute
            params: Command parameters
            
        Returns:
            Result message string
        """
        try:
            self.logger.info(f"Executing command type: {cmd_type}, params: {params}")
            
            # Route to appropriate handler
            if cmd_type == 'open_app':
                return self._handle_open_app(params[0] if params else "")
            elif cmd_type == 'close_app':
                return self._handle_close_app(params[0] if params else "")
            elif cmd_type == 'system_control':
                return self._handle_system_control(params[0] if params else "")
            elif cmd_type in ['volume', 'volume_up', 'volume_down', 'volume_mute', 'volume_unmute']:
                return self._handle_volume_control(cmd_type)
            elif cmd_type == 'open_file':
                return self._handle_open_file(params[0] if params else "")
            elif cmd_type == 'create_file':
                return self._handle_create_file(params[0] if params else "")
            elif cmd_type == 'delete_file':
                return self._handle_delete_file(params[0] if params else "")
            elif cmd_type == 'search_files':
                return self._handle_search_files(params[0] if params else "")
            elif cmd_type == 'web_search':
                return self._handle_web_search(params[0] if params else "")
            elif cmd_type == 'open_website':
                return self._handle_open_website(params[0] if params else "")
            elif cmd_type == 'open_url':
                return self._handle_open_url(params[0] if params else "")
            elif cmd_type == 'time':
                return self._handle_time()
            elif cmd_type == 'date':
                return self._handle_date()
            elif cmd_type == 'cpu_usage':
                return self._handle_cpu_usage()
            elif cmd_type == 'memory_usage':
                return self._handle_memory_usage()
            elif cmd_type == 'disk_usage':
                return self._handle_disk_usage()
            elif cmd_type == 'system_info':
                return self._handle_system_info()
            elif cmd_type == 'weather':
                return self._handle_weather()
            elif cmd_type == 'help':
                return self._handle_help()
            elif cmd_type == 'version':
                return self._handle_version()
            else:
                return f"Unknown command type: {cmd_type}"
                
        except Exception as e:
            self.logger.error(f"Error executing command {cmd_type}: {e}")
            return f"Error executing command: {e}"
    
    def _handle_open_app(self, app_name: str) -> str:
        """Handle opening applications."""
        try:
            app_name = app_name.lower().strip()
            
            if not app_name:
                return "Please specify an application name"
            
            # Check if application is in our mapping
            if app_name in self.app_commands:
                command = self.app_commands[app_name]
                subprocess.Popen([command], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                return f"Opening {app_name}..."
            
            # Try to find the application using which command
            try:
                result = subprocess.run(['which', app_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.Popen([app_name], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    return f"Opening {app_name}..."
            except:
                pass
            
            return f"Application '{app_name}' not found. Available apps: {', '.join(list(self.app_commands.keys())[:10])}"
            
        except Exception as e:
            self.logger.error(f"Error opening app {app_name}: {e}")
            return f"Failed to open {app_name}: {e}"
    
    def _handle_close_app(self, app_name: str) -> str:
        """Handle closing applications."""
        try:
            app_name = app_name.lower().strip()
            
            if not app_name:
                return "Please specify an application name"
            
            # Map common names to process names
            process_names = {
                'firefox': 'firefox',
                'chrome': 'google-chrome',
                'google chrome': 'google-chrome',
                'chromium': 'chromium-browser',
                'vscode': 'code',
                'visual studio code': 'code',
                'terminal': 'gnome-terminal',
                'files': 'nautilus',
                'calculator': 'gnome-calculator',
                'text editor': 'gedit',
                'gedit': 'gedit',
            }
            
            target_process = process_names.get(app_name, app_name)
            
            # Find and kill the process
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if target_process.lower() in proc.info['name'].lower():
                        proc.terminate()
                        return f"Closed {app_name}"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return f"Application '{app_name}' is not running"
            
        except Exception as e:
            self.logger.error(f"Error closing app {app_name}: {e}")
            return f"Failed to close {app_name}: {e}"
    
    def _handle_system_control(self, action: str) -> str:
        """Handle system control commands."""
        try:
            action = action.lower().strip()
            
            if action == 'shutdown':
                if self.config_manager.get('commands.confirm_dangerous', True):
                    return "Shutdown command requires confirmation in settings"
                subprocess.run(['shutdown', 'now'])
                return "Shutting down system..."
            
            elif action in ['restart', 'reboot']:
                if self.config_manager.get('commands.confirm_dangerous', True):
                    return "Restart command requires confirmation in settings"
                subprocess.run(['reboot'])
                return "Restarting system..."
            
            elif action == 'lock':
                subprocess.run(['gnome-screensaver-command', '-l'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Screen locked"
            
            elif action == 'logout':
                subprocess.run(['gnome-session-quit', '--logout'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Logging out..."
            
            else:
                return f"Unknown system control action: {action}"
                
        except Exception as e:
            self.logger.error(f"Error in system control {action}: {e}")
            return f"Failed to execute {action}: {e}"
    
    def _handle_volume_control(self, cmd_type: str) -> str:
        """Handle volume control commands."""
        try:
            if cmd_type in ['volume_up', 'volume']:
                subprocess.run(['amixer', 'sset', 'Master', '5%+'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Volume increased"
            
            elif cmd_type == 'volume_down':
                subprocess.run(['amixer', 'sset', 'Master', '5%-'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Volume decreased"
            
            elif cmd_type in ['volume_mute', 'volume']:
                subprocess.run(['amixer', 'sset', 'Master', 'mute'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Volume muted"
            
            elif cmd_type == 'volume_unmute':
                subprocess.run(['amixer', 'sset', 'Master', 'unmute'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Volume unmuted"
            
            else:
                return f"Unknown volume command: {cmd_type}"
                
        except Exception as e:
            self.logger.error(f"Error in volume control: {e}")
            return f"Failed to control volume: {e}"
    
    def _handle_open_file(self, file_path: str) -> str:
        """Handle opening files."""
        try:
            file_path = file_path.strip().strip('"\'')
            
            if not file_path:
                return "Please specify a file path"
            
            # Expand home directory if needed
            file_path = os.path.expanduser(file_path)
            
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            # Open with default application
            subprocess.run(['xdg-open', file_path], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening {file_path}"
            
        except Exception as e:
            self.logger.error(f"Error opening file {file_path}: {e}")
            return f"Failed to open file: {e}"
    
    def _handle_create_file(self, filename: str) -> str:
        """Handle creating files."""
        try:
            filename = filename.strip().strip('"\'')
            
            if not filename:
                return "Please specify a filename"
            
            # Create in current directory or home if no path specified
            if os.path.dirname(filename):
                file_path = os.path.expanduser(filename)
            else:
                file_path = os.path.join(os.path.expanduser("~"), filename)
            
            if os.path.exists(file_path):
                return f"File already exists: {file_path}"
            
            with open(file_path, 'w') as f:
                f.write("")
            
            return f"Created file: {file_path}"
            
        except Exception as e:
            self.logger.error(f"Error creating file {filename}: {e}")
            return f"Failed to create file: {e}"
    
    def _handle_delete_file(self, file_path: str) -> str:
        """Handle deleting files."""
        try:
            file_path = file_path.strip().strip('"\'')
            
            if not file_path:
                return "Please specify a file path"
            
            file_path = os.path.expanduser(file_path)
            
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            if self.config_manager.get('commands.confirm_dangerous', True):
                return f"File deletion requires confirmation in settings"
            
            os.remove(file_path)
            return f"Deleted file: {file_path}"
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return f"Failed to delete file: {e}"
    
    def _handle_search_files(self, pattern: str) -> str:
        """Handle searching for files."""
        try:
            pattern = pattern.strip().strip('"\'')
            
            if not pattern:
                return "Please specify a search pattern"
            
            # Search in home directory
            home_dir = os.path.expanduser("~")
            search_pattern = os.path.join(home_dir, "**", f"*{pattern}*")
            
            found_files = glob.glob(search_pattern, recursive=True)[:10]  # Limit to 10 results
            
            if found_files:
                result = f"Found {len(found_files)} files:\n"
                for file_path in found_files:
                    result += f"  {file_path}\n"
                return result
            else:
                return f"No files found matching: {pattern}"
                
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return f"Failed to search files: {e}"
    
    def _handle_web_search(self, query: str) -> str:
        """Handle web search."""
        try:
            query = query.strip()
            
            if not query:
                return "Please specify a search query"
            
            # Encode query for URL
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Open in default browser
            subprocess.run(['xdg-open', search_url], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Searching for: {query}"
            
        except Exception as e:
            self.logger.error(f"Error in web search: {e}")
            return f"Failed to perform web search: {e}"
    
    def _handle_open_website(self, url: str) -> str:
        """Handle opening websites."""
        try:
            url = url.strip()
            
            if not url:
                return "Please specify a website URL"
            
            # Add http:// if no protocol specified
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            subprocess.run(['xdg-open', url], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening website: {url}"
            
        except Exception as e:
            self.logger.error(f"Error opening website {url}: {e}")
            return f"Failed to open website: {e}"
    
    def _handle_open_url(self, url: str) -> str:
        """Handle opening URLs directly."""
        return self._handle_open_website(url)
    
    def _handle_time(self) -> str:
        """Handle time query."""
        try:
            current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
            return f"Current time: {current_time}"
        except Exception as e:
            return f"Error getting time: {e}"
    
    def _handle_date(self) -> str:
        """Handle date query."""
        try:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today's date: {current_date}"
        except Exception as e:
            return f"Error getting date: {e}"
    
    def _handle_cpu_usage(self) -> str:
        """Handle CPU usage query."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            return f"CPU Usage: {cpu_percent}% ({cpu_count} cores)"
        except Exception as e:
            return f"Error getting CPU usage: {e}"
    
    def _handle_memory_usage(self) -> str:
        """Handle memory usage query."""
        try:
            memory = psutil.virtual_memory()
            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)
            percent = memory.percent
            return f"Memory Usage: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%)"
        except Exception as e:
            return f"Error getting memory usage: {e}"
    
    def _handle_disk_usage(self) -> str:
        """Handle disk usage query."""
        try:
            disk = psutil.disk_usage('/')
            used_gb = disk.used / (1024**3)
            total_gb = disk.total / (1024**3)
            percent = (disk.used / disk.total) * 100
            return f"Disk Usage: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.1f}%)"
        except Exception as e:
            return f"Error getting disk usage: {e}"
    
    def _handle_system_info(self) -> str:
        """Handle system info query."""
        try:
            import platform
            
            info = f"System Information:\n"
            info += f"  OS: {platform.system()} {platform.release()}\n"
            info += f"  Architecture: {platform.machine()}\n"
            info += f"  Processor: {platform.processor()}\n"
            info += f"  CPU Cores: {psutil.cpu_count()}\n"
            info += f"  Memory: {psutil.virtual_memory().total / (1024**3):.1f}GB"
            
            return info
        except Exception as e:
            return f"Error getting system info: {e}"
    
    def _handle_weather(self) -> str:
        """Handle weather query."""
        return "Weather feature not yet implemented. Requires API integration."
    
    def _handle_help(self) -> str:
        """Handle help command."""
        help_text = """
Available Commands:
  open <app>           - Launch application (firefox, terminal, etc.)
  close <app>          - Close running application
  shutdown             - Shutdown system
  restart              - Restart system
  lock                 - Lock screen
  volume up/down/mute  - Control volume
  open file <path>     - Open file with default app
  create file <name>   - Create new file
  delete file <path>   - Delete file
  search <pattern>     - Search files or web
  open website <url>   - Open website
  time                 - Show current time
  date                 - Show current date
  cpu usage            - Show CPU usage
  memory usage         - Show memory usage
  system info          - Show system information
  help                 - Show this help
  version              - Show version
        """.strip()
        return help_text
    
    def _handle_version(self) -> str:
        """Handle version command."""
        return "Virtual Assistant v1.0.0 for Ubuntu"
