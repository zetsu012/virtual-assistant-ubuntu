"""
Configuration Manager for Virtual Assistant
Handles loading, saving, and managing application settings.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path.home() / ".config" / "virtual-assistant"
        self.config_file = self.config_dir / "settings.json"
        self._config: Dict[str, Any] = {}
        self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> None:
        """Load default configuration settings."""
        self._config = {
            "voice": {
                "timeout": 5,
                "language": "en-US",
                "speech_rate": 150,
                "enabled": True
            },
            "hotkeys": {
                "voice_command": "<Ctrl>+<Alt>+V",
                "text_command": "<Ctrl>+<Alt>+T"
            },
            "notifications": {
                "enabled": True,
                "duration": 3,
                "sound_enabled": True
            },
            "general": {
                "autostart": False,
                "log_level": "INFO",
                "theme": "light"
            },
            "commands": {
                "confirm_dangerous": True,
                "show_feedback": True,
                "execution_timeout": 30
            }
        }
    
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # Merge with defaults (deep merge for nested dicts)
                self._merge_config(self._config, file_config)
                self.logger.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                self.logger.info("No configuration file found, using defaults")
                self.save_config()  # Create config file with defaults
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.logger.info("Using default configuration")
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def _merge_config(self, default: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge override config into default config."""
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config key (e.g., 'voice.timeout')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key_path.split('.')
            value = self._config
            
            for key in keys:
                value = value[key]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config key (e.g., 'voice.timeout')
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = key_path.split('.')
            config = self._config
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set the value
            config[keys[-1]] = value
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set config value '{key_path}': {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name (e.g., 'voice', 'notifications')
            
        Returns:
            Configuration section dictionary
        """
        return self._config.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any]) -> bool:
        """
        Update an entire configuration section.
        
        Args:
            section: Section name to update
            values: Dictionary of values to set in the section
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if section not in self._config:
                self._config[section] = {}
            
            self._config[section].update(values)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update section '{section}': {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        try:
            self._load_default_config()
            self.logger.info("Configuration reset to defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get a copy of the entire configuration dictionary."""
        return self._config.copy()
    
    def is_voice_enabled(self) -> bool:
        """Check if voice commands are enabled."""
        return self.get('voice.enabled', True)
    
    def are_notifications_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self.get('notifications.enabled', True)
    
    def get_voice_timeout(self) -> int:
        """Get voice recording timeout in seconds."""
        return self.get('voice.timeout', 5)
    
    def get_notification_duration(self) -> int:
        """Get notification display duration in seconds."""
        return self.get('notifications.duration', 3)
