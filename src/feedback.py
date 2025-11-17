"""
Feedback System for Virtual Assistant
Handles text-to-speech and desktop notifications.
"""

import logging
import subprocess
import os
from typing import Optional
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    from gi.repository import Notify
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False


class FeedbackManager:
    """Manages feedback through TTS and notifications."""
    
    def __init__(self, config_manager):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # Initialize TTS engine
        self.tts_engine = None
        self._init_tts()
        
        # Initialize notification system
        self._init_notifications()
        
        self.logger.info("Feedback manager initialized")
    
    def _init_tts(self) -> None:
        """Initialize text-to-speech engine."""
        try:
            if TTS_AVAILABLE and self.config_manager.get('voice.enabled', True):
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS settings
                rate = self.config_manager.get('voice.speech_rate', 150)
                self.tts_engine.setProperty('rate', rate)
                
                # Set voice (prefer female if available)
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if 'female' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                
                self.logger.info("TTS engine initialized")
            else:
                self.logger.warning("TTS not available or disabled")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    def _init_notifications(self) -> None:
        """Initialize desktop notification system."""
        try:
            if NOTIFICATIONS_AVAILABLE and self.config_manager.are_notifications_enabled():
                Notify.init("VirtualAssistant")
                self.logger.info("Desktop notifications initialized")
            else:
                self.logger.warning("Desktop notifications not available or disabled")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize notifications: {e}")
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.tts_engine:
                self.logger.warning("TTS not available")
                return False
            
            if not text.strip():
                return False
            
            self.logger.info(f"Speaking: {text[:50]}...")
            
            # Speak in a separate thread to avoid blocking
            def speak_async():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    self.logger.error(f"Error in TTS playback: {e}")
            
            import threading
            thread = threading.Thread(target=speak_async, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
            return False
    
    def show_notification(self, title: str, message: str, urgency: str = "normal") -> bool:
        """
        Show desktop notification.
        
        Args:
            title: Notification title
            message: Notification message
            urgency: Notification urgency ("low", "normal", "critical")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not NOTIFICATIONS_AVAILABLE or not self.config_manager.are_notifications_enabled():
                self.logger.warning("Desktop notifications not available or disabled")
                return False
            
            self.logger.info(f"Showing notification: {title} - {message[:50]}...")
            
            # Create notification
            notification = Notify.Notification.new(title, message)
            
            # Set urgency
            if urgency == "critical":
                notification.set_urgency(Notify.Urgency.CRITICAL)
            elif urgency == "low":
                notification.set_urgency(Notify.Urgency.LOW)
            else:
                notification.set_urgency(Notify.Urgency.NORMAL)
            
            # Set timeout (duration in milliseconds)
            timeout = self.config_manager.get_notification_duration() * 1000
            notification.set_timeout(timeout)
            
            # Show notification
            notification.show()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")
            return False
    
    def provide_feedback(self, message: str, use_speech: bool = None, use_notification: bool = None) -> None:
        """
        Provide feedback using both speech and notifications.
        
        Args:
            message: Message to deliver
            use_speech: Whether to use TTS (None = use config)
            use_notification: Whether to use notifications (None = use config)
        """
        try:
            # Determine whether to use each feedback method
            if use_speech is None:
                use_speech = (self.tts_engine is not None and 
                            self.config_manager.get('voice.enabled', True))
            
            if use_notification is None:
                use_notification = (NOTIFICATIONS_AVAILABLE and 
                                  self.config_manager.are_notifications_enabled())
            
            # Provide speech feedback
            if use_speech:
                self.speak(message)
            
            # Provide notification feedback
            if use_notification:
                self.show_notification("Virtual Assistant", message)
            
        except Exception as e:
            self.logger.error(f"Error providing feedback: {e}")
    
    def notify_success(self, message: str) -> None:
        """Notify about successful operation."""
        self.show_notification("Success", message, "normal")
        if self.config_manager.get('voice.enabled', True):
            self.speak(message)
    
    def notify_error(self, message: str) -> None:
        """Notify about error."""
        self.show_notification("Error", message, "critical")
        if self.config_manager.get('voice.enabled', True):
            self.speak(f"Error: {message}")
    
    def notify_info(self, message: str) -> None:
        """Notify about informational message."""
        self.show_notification("Virtual Assistant", message, "normal")
        # Don't speak info messages by default to avoid being too chatty
    
    def notify_command_result(self, command: str, result: str, success: bool = True) -> None:
        """
        Notify about command execution result.
        
        Args:
            command: The command that was executed
            result: The result message
            success: Whether the command was successful
        """
        try:
            if success:
                self.notify_success(result)
            else:
                self.notify_error(result)
                
        except Exception as e:
            self.logger.error(f"Error notifying command result: {e}")
    
    def test_tts(self) -> bool:
        """Test TTS functionality."""
        try:
            test_message = "Virtual Assistant is working correctly"
            return self.speak(test_message)
        except Exception as e:
            self.logger.error(f"TTS test failed: {e}")
            return False
    
    def test_notifications(self) -> bool:
        """Test notification functionality."""
        try:
            return self.show_notification(
                "Test Notification", 
                "Virtual Assistant notifications are working!",
                "normal"
            )
        except Exception as e:
            self.logger.error(f"Notification test failed: {e}")
            return False
    
    def update_tts_settings(self) -> None:
        """Update TTS settings from configuration."""
        try:
            if self.tts_engine:
                rate = self.config_manager.get('voice.speech_rate', 150)
                self.tts_engine.setProperty('rate', rate)
                
                self.logger.info(f"TTS settings updated: rate={rate}")
            
        except Exception as e:
            self.logger.error(f"Error updating TTS settings: {e}")
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices."""
        try:
            if not self.tts_engine:
                return []
            
            voices = []
            for voice in self.tts_engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                })
            
            return voices
            
        except Exception as e:
            self.logger.error(f"Error getting available voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set TTS voice by ID.
        
        Args:
            voice_id: ID of the voice to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.tts_engine:
                return False
            
            self.tts_engine.setProperty('voice', voice_id)
            self.logger.info(f"TTS voice set to: {voice_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up feedback system resources."""
        try:
            self.logger.info("Cleaning up feedback manager...")
            
            # Clean up TTS
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                except:
                    pass
                self.tts_engine = None
            
            # Clean up notifications
            if NOTIFICATIONS_AVAILABLE:
                try:
                    Notify.uninit()
                except:
                    pass
            
            self.logger.info("Feedback manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class SystemFeedback:
    """Fallback feedback system using system commands."""
    
    @staticmethod
    def speak_system(text: str) -> bool:
        """
        Speak using system TTS (espeak) as fallback.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use espeak as fallback
            subprocess.run(['espeak', text], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            return True
        except:
            return False
    
    @staticmethod
    def notify_system(title: str, message: str) -> bool:
        """
        Show notification using system notify-send as fallback.
        
        Args:
            title: Notification title
            message: Notification message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(['notify-send', title, message], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            return True
        except:
            return False
