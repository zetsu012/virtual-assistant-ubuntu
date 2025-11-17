#!/usr/bin/env python3
"""
Virtual Assistant for Ubuntu - Main Entry Point
This is the main application entry point that initializes the system tray icon
and manages the application lifecycle.
"""

import sys
import logging
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from typing import Optional

from tray_icon import VirtualAssistantTrayIcon
from config_manager import ConfigManager


def setup_logging() -> None:
    """Set up logging configuration for the application."""
    log_dir = os.path.expanduser("~/.local/share/virtual-assistant")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "assistant.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Virtual Assistant logging initialized")
    logger.info(f"Log file location: {log_file}")


class VirtualAssistantApp:
    """Main application class for the Virtual Assistant."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app: Optional[QApplication] = None
        self.tray_icon: Optional[VirtualAssistantTrayIcon] = None
        self.config_manager: Optional[ConfigManager] = None
        
    def initialize(self) -> bool:
        """Initialize the application components."""
        try:
            self.logger.info("Initializing Virtual Assistant...")
            
            # Create Qt application
            self.app = QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)  # Keep running with tray icon
            
            # Initialize configuration manager
            self.config_manager = ConfigManager()
            
            # Initialize system tray icon
            self.tray_icon = VirtualAssistantTrayIcon(self.config_manager)
            
            if not self.tray_icon.is_available():
                self.logger.error("System tray is not available on this system")
                return False
            
            self.tray_icon.show()
            
            self.logger.info("Virtual Assistant initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Virtual Assistant: {e}")
            return False
    
    def run(self) -> int:
        """Run the application main loop."""
        if not self.initialize():
            return 1
        
        try:
            self.logger.info("Starting Virtual Assistant main loop...")
            return self.app.exec_()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down...")
            return 0
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            return 1
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up application resources."""
        try:
            self.logger.info("Cleaning up Virtual Assistant...")
            
            # Clean up tray icon first (this will clean up its components)
            if self.tray_icon:
                self.tray_icon.cleanup()
                self.tray_icon = None
            
            # Add a small delay to allow threads to finish
            QTimer.singleShot(500, self._final_cleanup)
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _final_cleanup(self) -> None:
        """Final cleanup after threads have had time to finish."""
        try:
            if self.app:
                self.app.quit()
                self.app = None
            
            self.logger.info("Virtual Assistant cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during final cleanup: {e}")


def main() -> int:
    """Main entry point for the application."""
    # Set up logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Virtual Assistant for Ubuntu...")
    
    # Check if we're running on a supported system
    if sys.platform != "linux":
        logger.warning("This application is designed for Ubuntu/Linux")
    
    # Create and run the application
    app = VirtualAssistantApp()
    exit_code = app.run()
    
    logger.info(f"Virtual Assistant exited with code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
