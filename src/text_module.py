"""
Text Command Module for Virtual Assistant
Handles text-based command input through a dialog interface.
"""

import logging
from typing import Optional
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence

from command_processor import CommandProcessor


class TextCommandDialog(QDialog):
    """Dialog for text command input and execution."""
    
    # Signal emitted when a command is executed
    command_executed = pyqtSignal(str, str)  # command, result
    
    def __init__(self, config_manager, feedback_manager):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.feedback_manager = feedback_manager
        
        # Initialize command processor
        self.command_processor = CommandProcessor(config_manager, feedback_manager)
        
        # Set up the dialog
        self._setup_ui()
        self._connect_signals()
        
        self.logger.info("Text command dialog initialized")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        try:
            self.setWindowTitle("Virtual Assistant - Text Command")
            self.setFixedSize(500, 300)
            self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
            
            # Main layout
            layout = QVBoxLayout()
            
            # Title label
            title_label = QLabel("Enter your command:")
            title_font = QFont()
            title_font.setPointSize(12)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)
            
            # Command input field
            self.command_input = QLineEdit()
            self.command_input.setPlaceholderText("Type your command here...")
            self.command_input.setFont(QFont("Arial", 11))
            layout.addWidget(self.command_input)
            
            # Example commands label
            example_label = QLabel("Examples: 'open firefox', 'time', 'search python', 'shutdown'")
            example_font = QFont()
            example_font.setPointSize(9)
            example_font.setItalic(True)
            example_label.setFont(example_font)
            example_label.setStyleSheet("color: gray;")
            layout.addWidget(example_label)
            
            # Button layout
            button_layout = QHBoxLayout()
            
            self.execute_button = QPushButton("Execute")
            self.execute_button.setDefault(True)
            self.execute_button.setMinimumHeight(35)
            
            self.clear_button = QPushButton("Clear")
            self.clear_button.setMinimumHeight(35)
            
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.setMinimumHeight(35)
            
            button_layout.addWidget(self.execute_button)
            button_layout.addWidget(self.clear_button)
            button_layout.addWidget(self.cancel_button)
            
            layout.addLayout(button_layout)
            
            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            layout.addWidget(separator)
            
            # Result display
            result_label = QLabel("Result:")
            result_font = QFont()
            result_font.setPointSize(10)
            result_font.setBold(True)
            result_label.setFont(result_font)
            layout.addWidget(result_label)
            
            self.result_display = QTextEdit()
            self.result_display.setReadOnly(True)
            self.result_display.setMaximumHeight(100)
            self.result_display.setFont(QFont("Courier", 9))
            layout.addWidget(self.result_display)
            
            self.setLayout(layout)
            
            # Set focus to input field
            self.command_input.setFocus()
            
        except Exception as e:
            self.logger.error(f"Failed to set up UI: {e}")
    
    def _connect_signals(self) -> None:
        """Connect UI signals to handlers."""
        try:
            # Button signals
            self.execute_button.clicked.connect(self._execute_command)
            self.clear_button.clicked.connect(self._clear_input)
            self.cancel_button.clicked.connect(self.close)
            
            # Input field signals
            self.command_input.returnPressed.connect(self._execute_command)
            
            # Command processor signals
            self.command_processor.command_completed.connect(self._on_command_completed)
            self.command_processor.command_failed.connect(self._on_command_failed)
            
        except Exception as e:
            self.logger.error(f"Failed to connect signals: {e}")
    
    def _execute_command(self) -> None:
        """Execute the entered command."""
        try:
            command = self.command_input.text().strip()
            
            if not command:
                self.result_display.setText("Please enter a command.")
                return
            
            # Check if command processor is available
            if not self.command_processor:
                self.result_display.setText("Error: Command processor not available. Please reopen the dialog.")
                return
            
            self.logger.info(f"Executing text command: {command}")
            
            # Update UI to show processing
            self.execute_button.setEnabled(False)
            self.execute_button.setText("Processing...")
            self.result_display.setText("Executing command...")
            
            # Process the command
            self.command_processor.process_command(command)
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            self._on_command_failed(f"Error: {e}")
    
    def _clear_input(self) -> None:
        """Clear the input field and result display."""
        try:
            self.command_input.clear()
            self.result_display.clear()
            self.command_input.setFocus()
            
        except Exception as e:
            self.logger.error(f"Error clearing input: {e}")
    
    def _on_command_completed(self, result: str) -> None:
        """Handle successful command completion."""
        try:
            self.result_display.setText(result)
            self.execute_button.setEnabled(True)
            self.execute_button.setText("Execute")
            
            # Emit signal for other components
            command = self.command_input.text().strip()
            self.command_executed.emit(command, result)
            
            # Auto-close after successful execution if configured
            if self.config_manager.get('general.auto_close_dialog', False):
                QTimer.singleShot(2000, self.close)
            
        except Exception as e:
            self.logger.error(f"Error handling command completion: {e}")
    
    def _on_command_failed(self, error_message: str) -> None:
        """Handle command execution failure."""
        try:
            self.result_display.setText(f"Error: {error_message}")
            self.execute_button.setEnabled(True)
            self.execute_button.setText("Execute")
            
            # Show notification for errors
            if self.config_manager.are_notifications_enabled():
                self.feedback_manager.show_notification(
                    "Command Failed", 
                    error_message
                )
            
        except Exception as e:
            self.logger.error(f"Error handling command failure: {e}")
    
    def keyPressEvent(self, event) -> None:
        """Handle key press events."""
        try:
            # Escape key closes the dialog
            if event.key() == Qt.Key_Escape:
                self.close()
            # Ctrl+L clears input
            elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
                self._clear_input()
            else:
                super().keyPressEvent(event)
                
        except Exception as e:
            self.logger.error(f"Error handling key press: {e}")
    
    def showEvent(self, event) -> None:
        """Handle dialog show event."""
        try:
            super().showEvent(event)
            # Focus on input field when dialog is shown
            QTimer.singleShot(100, lambda: self.command_input.setFocus())
            
        except Exception as e:
            self.logger.error(f"Error handling show event: {e}")
    
    def closeEvent(self, event) -> None:
        """Handle dialog close event."""
        try:
            self.logger.info("Text command dialog closing")
            self.cleanup()
            super().closeEvent(event)
            
        except Exception as e:
            self.logger.error(f"Error handling close event: {e}")
    
    def cleanup(self) -> None:
        """Clean up dialog resources."""
        try:
            if self.command_processor:
                self.command_processor.cleanup()
                self.command_processor = None
            
        except Exception as e:
            self.logger.error(f"Error during dialog cleanup: {e}")
    
    def set_command(self, command: str) -> None:
        """Set the command text programmatically."""
        try:
            self.command_input.setText(command)
            self.command_input.selectAll()
            
        except Exception as e:
            self.logger.error(f"Error setting command: {e}")
    
    def get_last_command(self) -> str:
        """Get the last executed command."""
        return self.command_input.text().strip()
