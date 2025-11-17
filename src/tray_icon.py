"""
System Tray Icon for Virtual Assistant
Implements the system tray functionality with context menu for Ubuntu.
"""

import logging
import os
from typing import Optional
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

from text_module import TextCommandDialog
from voice_module import VoiceCommandHandler
from feedback import FeedbackManager


class VirtualAssistantTrayIcon(QSystemTrayIcon):
    """System tray icon for the Virtual Assistant application."""
    
    # Signals for communication with other components
    voice_command_requested = pyqtSignal()
    text_command_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, config_manager):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # Initialize components
        self.feedback_manager = FeedbackManager(config_manager)
        self.voice_handler = VoiceCommandHandler(config_manager, self.feedback_manager)
        self.text_dialog: Optional[TextCommandDialog] = None
        
        # Set up the tray icon
        self._setup_icon()
        self._setup_menu()
        self._connect_signals()
        
        self.logger.info("System tray icon initialized")
    
    def _setup_icon(self) -> None:
        """Set up the tray icon image."""
        try:
            # Try to load custom icon first
            icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.png")
            
            if os.path.exists(icon_path):
                self.setIcon(QIcon(icon_path))
                self.logger.info(f"Loaded custom icon from {icon_path}")
            else:
                # Use system default icon if custom icon not found
                self.setIcon(self.style().standardIcon(getattr(self.style(), 'SP_ComputerIcon')))
                self.logger.info("Using system default icon")
                
        except Exception as e:
            self.logger.error(f"Failed to set up tray icon: {e}")
            # Fallback to system icon
            self.setIcon(self.style().standardIcon(getattr(self.style(), 'SP_ComputerIcon')))
    
    def _setup_menu(self) -> None:
        """Set up the right-click context menu."""
        try:
            menu = QMenu()
            
            # Voice Command action
            voice_action = QAction("Voice Command", menu)
            voice_action.triggered.connect(self._on_voice_command)
            menu.addAction(voice_action)
            
            # Text Command action
            text_action = QAction("Text Command", menu)
            text_action.triggered.connect(self._on_text_command)
            menu.addAction(text_action)
            
            menu.addSeparator()
            
            # Settings action
            settings_action = QAction("Settings", menu)
            settings_action.triggered.connect(self._on_settings)
            menu.addAction(settings_action)
            
            menu.addSeparator()
            
            # About action
            about_action = QAction("About", menu)
            about_action.triggered.connect(self._on_about)
            menu.addAction(about_action)
            
            menu.addSeparator()
            
            # Quit action
            quit_action = QAction("Quit", menu)
            quit_action.triggered.connect(self._on_quit)
            menu.addAction(quit_action)
            
            self.setContextMenu(menu)
            self.setToolTip("Virtual Assistant - Click for commands")
            
            # Set up left-click behavior
            self.activated.connect(self._on_activated)
            
            self.logger.info("Context menu set up successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to set up context menu: {e}")
    
    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.voice_command_requested.connect(self._on_voice_command)
        self.text_command_requested.connect(self._on_text_command)
        self.settings_requested.connect(self._on_settings)
    
    def _on_activated(self, reason) -> None:
        """Handle tray icon activation (left-click)."""
        if reason == QSystemTrayIcon.Trigger:  # Left click
            # Show text command dialog on left click
            self._on_text_command()
    
    def _on_voice_command(self) -> None:
        """Handle voice command request."""
        try:
            self.logger.info("Voice command requested")
            
            if not self.config_manager.is_voice_enabled():
                self.feedback_manager.show_notification(
                    "Voice Disabled", 
                    "Voice commands are disabled in settings"
                )
                return
            
            # Start voice command handler
            self.voice_handler.start_listening()
            
        except Exception as e:
            self.logger.error(f"Error handling voice command: {e}")
            self.feedback_manager.show_notification(
                "Error", 
                f"Failed to start voice command: {e}"
            )
    
    def _on_text_command(self) -> None:
        """Handle text command request."""
        try:
            self.logger.info("Text command requested")
            
            # Create and show text command dialog
            if not self.text_dialog:
                self.text_dialog = TextCommandDialog(self.config_manager, self.feedback_manager)
            
            self.text_dialog.show()
            self.text_dialog.raise_()
            self.text_dialog.activateWindow()
            
        except Exception as e:
            self.logger.error(f"Error handling text command: {e}")
            self.feedback_manager.show_notification(
                "Error", 
                f"Failed to open text command dialog: {e}"
            )
    
    def _on_settings(self) -> None:
        """Handle settings request."""
        try:
            self.logger.info("Settings requested")
            self.feedback_manager.show_notification(
                "Settings", 
                "Settings dialog not yet implemented"
            )
            # TODO: Implement settings dialog
            
        except Exception as e:
            self.logger.error(f"Error handling settings: {e}")
    
    def _on_about(self) -> None:
        """Handle about dialog request."""
        try:
            self.logger.info("About dialog requested")
            
            about_text = """
            <h3>Virtual Assistant for Ubuntu</h3>
            <p>Version 1.0.0</p>
            <p>A voice and text-based virtual assistant with system tray integration.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Voice command recognition</li>
                <li>Text command input</li>
                <li>System operations</li>
                <li>Application launching</li>
                <li>File operations</li>
            </ul>
            """
            
            QMessageBox.about(None, "About Virtual Assistant", about_text)
            
        except Exception as e:
            self.logger.error(f"Error showing about dialog: {e}")
    
    def _on_quit(self) -> None:
        """Handle application quit request."""
        try:
            self.logger.info("Quit requested")
            
            # Confirm quit if configured
            if self.config_manager.get('commands.confirm_dangerous', True):
                reply = QMessageBox.question(
                    None, 
                    "Quit Virtual Assistant", 
                    "Are you sure you want to quit the Virtual Assistant?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            # Clean up and quit
            self.cleanup()
            
            # Emit quit signal to application
            from PyQt5.QtCore import QCoreApplication
            QCoreApplication.quit()
            
        except Exception as e:
            self.logger.error(f"Error during quit: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources before quitting."""
        try:
            self.logger.info("Cleaning up tray icon...")
            
            if self.voice_handler:
                self.voice_handler.cleanup()
            
            if self.text_dialog:
                self.text_dialog.close()
                self.text_dialog = None
            
            if self.feedback_manager:
                self.feedback_manager.cleanup()
            
            # Clean up command processor if it exists
            if hasattr(self.text_dialog, 'command_processor') and self.text_dialog.command_processor:
                self.text_dialog.command_processor.cleanup()
            
            self.logger.info("Tray icon cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def is_available(self) -> bool:
        """Check if system tray is available."""
        return QSystemTrayIcon.isSystemTrayAvailable()
    
    def show_message(self, title: str, message: str, icon_type=None) -> None:
        """Show a balloon message from the tray icon."""
        try:
            if icon_type is None:
                icon_type = QSystemTrayIcon.Information
            
            self.showMessage(title, message, icon_type, 
                           self.config_manager.get_notification_duration() * 1000)
            
        except Exception as e:
            self.logger.error(f"Failed to show tray message: {e}")
