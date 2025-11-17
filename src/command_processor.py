"""
Command Processor for Virtual Assistant
Handles parsing and routing of commands to appropriate handlers.
"""

import re
import logging
from typing import Tuple, Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from task_handlers import TaskHandler


class CommandProcessor(QObject):
    """Processes and routes commands to appropriate handlers."""
    
    # Signals for command execution results
    command_completed = pyqtSignal(str)  # result message
    command_failed = pyqtSignal(str)     # error message
    
    def __init__(self, config_manager, feedback_manager):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.feedback_manager = feedback_manager
        
        # Initialize task handler
        self.task_handler = TaskHandler(config_manager, feedback_manager)
        
        # Track active workers for cleanup
        self.active_workers = []
        
        # Define command patterns
        self._setup_command_patterns()
        
        self.logger.info("Command processor initialized")
    
    def _setup_command_patterns(self) -> None:
        """Set up regex patterns for command matching."""
        self.patterns = {
            # System Operations
            'open_app': r'^open\s+(.+)$',
            'close_app': r'^close\s+(.+)$',
            'system_control': r'^(shutdown|restart|reboot|lock|logout)$',
            'volume': r'^volume\s+(up|down|mute|unmute)$',
            
            # File Operations
            'open_file': r'^open\s+file\s+(.+)$',
            'create_file': r'^create\s+file\s+(.+)$',
            'delete_file': r'^delete\s+file\s+(.+)$',
            'search_files': r'^search\s+(.+)$',
            
            # Web Operations
            'web_search': r'^search\s+(.+)$',
            'open_website': r'^open\s+website\s+(.+)$',
            'open_url': r'^https?://.+',
            
            # Information Queries
            'time': r'^time$',
            'date': r'^date$',
            'cpu_usage': r'^cpu\s+usage$',
            'memory_usage': r'^memory\s+usage$',
            'disk_usage': r'^disk\s+usage$',
            'system_info': r'^system\s+info$',
            
            # Application-specific
            'weather': r'^weather$',
            'help': r'^(help|\?)$',
            'version': r'^version$',
            
            # Volume control (alternative)
            'volume_up': r'^volume\s+up$',
            'volume_down': r'^volume\s+down$',
            'volume_mute': r'^volume\s+mute$',
            'volume_unmute': r'^volume\s+unmute$',
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {
            cmd_type: re.compile(pattern, re.IGNORECASE)
            for cmd_type, pattern in self.patterns.items()
        }
    
    def process_command(self, command_text: str) -> None:
        """
        Process a command and route it to the appropriate handler.
        
        Args:
            command_text: The command text to process
        """
        try:
            # Clean and normalize the command
            command_text = command_text.strip().lower()
            
            if not command_text:
                self.command_failed.emit("Empty command")
                return
            
            self.logger.info(f"Processing command: {command_text}")
            
            # Try to match command patterns
            cmd_type, params = self._parse_command(command_text)
            
            if cmd_type == 'unknown':
                self._handle_unknown_command(command_text)
                return
            
            # Execute the command in a separate thread to avoid blocking UI
            self._execute_command_async(cmd_type, params)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            self.command_failed.emit(f"Command processing error: {e}")
    
    def _parse_command(self, command_text: str) -> Tuple[str, Optional[Tuple]]:
        """
        Parse command text and extract command type and parameters.
        
        Args:
            command_text: The command text to parse
            
        Returns:
            Tuple of (command_type, parameters) or ('unknown', None)
        """
        try:
            # Check each pattern
            for cmd_type, pattern in self.compiled_patterns.items():
                match = pattern.match(command_text)
                if match:
                    params = match.groups() if match.groups() else None
                    return cmd_type, params
            
            return 'unknown', None
            
        except Exception as e:
            self.logger.error(f"Error parsing command: {e}")
            return 'unknown', None
    
    def _execute_command_async(self, cmd_type: str, params: Optional[Tuple]) -> None:
        """
        Execute command asynchronously to avoid blocking the UI.
        
        Args:
            cmd_type: The type of command to execute
            params: Command parameters
        """
        try:
            # Create a worker thread for command execution
            worker = CommandWorker(self.task_handler, cmd_type, params)
            worker.result_ready.connect(self._on_command_result)
            worker.error_occurred.connect(self._on_command_error)
            worker.finished.connect(lambda: self._on_worker_finished(worker))
            
            # Track the worker
            self.active_workers.append(worker)
            worker.start()
            
        except Exception as e:
            self.logger.error(f"Error executing command asynchronously: {e}")
            self.command_failed.emit(f"Execution error: {e}")
    
    def _on_command_result(self, result: str) -> None:
        """Handle successful command execution result."""
        try:
            self.logger.info(f"Command completed: {result}")
            self.command_completed.emit(result)
            
        except Exception as e:
            self.logger.error(f"Error handling command result: {e}")
    
    def _on_command_error(self, error_message: str) -> None:
        """Handle command execution error."""
        try:
            self.logger.error(f"Command failed: {error_message}")
            self.command_failed.emit(error_message)
            
        except Exception as e:
            self.logger.error(f"Error handling command error: {e}")
    
    def _on_worker_finished(self, worker: 'CommandWorker') -> None:
        """Handle worker thread completion."""
        try:
            if worker in self.active_workers:
                self.active_workers.remove(worker)
                worker.deleteLater()
            
        except Exception as e:
            self.logger.error(f"Error handling worker finished: {e}")
    
    def cleanup(self) -> None:
        """Clean up all active worker threads."""
        try:
            self.logger.info("Cleaning up command processor...")
            
            # Stop all active workers
            for worker in self.active_workers[:]:
                try:
                    if worker.isRunning():
                        worker.terminate()
                        worker.wait(1000)  # Wait up to 1 second
                    if worker in self.active_workers:
                        self.active_workers.remove(worker)
                    worker.deleteLater()
                except Exception as e:
                    self.logger.error(f"Error cleaning up worker: {e}")
            
            self.active_workers.clear()
            self.logger.info("Command processor cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during command processor cleanup: {e}")
    
    def _handle_unknown_command(self, command_text: str) -> None:
        """Handle unknown commands."""
        try:
            # Try to provide helpful suggestions
            suggestions = self._get_command_suggestions(command_text)
            
            if suggestions:
                message = f"Unknown command '{command_text}'. Did you mean:\n{chr(10).join(suggestions)}"
            else:
                message = f"Unknown command '{command_text}'. Type 'help' for available commands."
            
            self.command_failed.emit(message)
            
        except Exception as e:
            self.logger.error(f"Error handling unknown command: {e}")
            self.command_failed.emit(f"Unknown command: {command_text}")
    
    def _get_command_suggestions(self, command_text: str) -> list:
        """
        Get command suggestions based on partial matches.
        
        Args:
            command_text: The unknown command text
            
        Returns:
            List of suggested commands
        """
        try:
            suggestions = []
            command_words = command_text.split()
            
            # Simple suggestion logic based on first word
            if command_words:
                first_word = command_words[0]
                
                if first_word in ['opn', 'ope']:
                    suggestions.append("open <application>")
                elif first_word in ['cls', 'cloe']:
                    suggestions.append("close <application>")
                elif first_word in ['shut', 'shutdwn']:
                    suggestions.append("shutdown")
                elif first_word in ['rest', 'restrt']:
                    suggestions.append("restart")
                elif first_word in ['serch', 'serh']:
                    suggestions.append("search <query>")
                elif first_word in ['tim']:
                    suggestions.append("time")
                elif first_word in ['dat']:
                    suggestions.append("date")
            
            return suggestions[:3]  # Return max 3 suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return []
    
    def get_available_commands(self) -> Dict[str, str]:
        """
        Get a dictionary of available commands and their descriptions.
        
        Returns:
            Dictionary mapping command patterns to descriptions
        """
        return {
            "open <application>": "Launch an application (firefox, terminal, etc.)",
            "close <application>": "Close a running application",
            "shutdown": "Shutdown the system",
            "restart": "Restart the system",
            "lock": "Lock the screen",
            "volume up/down/mute": "Control system volume",
            "open file <path>": "Open a file with default application",
            "create file <name>": "Create a new empty file",
            "delete file <path>": "Delete a file",
            "search <filename>": "Search for files by name",
            "search <query>": "Search the web",
            "open website <url>": "Open a specific website",
            "time": "Show current time",
            "date": "Show current date",
            "cpu usage": "Show CPU usage statistics",
            "memory usage": "Show memory usage statistics",
            "system info": "Show system information",
            "help": "Show this help message",
            "version": "Show application version"
        }


class CommandWorker(QThread):
    """Worker thread for executing commands asynchronously."""
    
    # Signals
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, task_handler: TaskHandler, cmd_type: str, params: Optional[Tuple]):
        super().__init__()
        
        self.task_handler = task_handler
        self.cmd_type = cmd_type
        self.params = params
    
    def run(self) -> None:
        """Execute the command and emit results."""
        try:
            result = self.task_handler.execute_command(self.cmd_type, self.params)
            self.result_ready.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
