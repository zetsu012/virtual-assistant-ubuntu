"""
Voice Input Module for Virtual Assistant
Handles speech recognition and voice command processing.
"""

import logging
import threading
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

from command_processor import CommandProcessor


class VoiceCommandHandler(QObject):
    """Handles voice command input and processing."""
    
    # Signals
    command_recognized = pyqtSignal(str)  # Recognized command text
    recognition_failed = pyqtSignal(str)  # Error message
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    
    def __init__(self, config_manager, feedback_manager):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.feedback_manager = feedback_manager
        
        # Initialize speech recognition
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.listening_thread = None
        
        self._init_speech_recognition()
        
        self.logger.info("Voice command handler initialized")
    
    def _init_speech_recognition(self) -> None:
        """Initialize speech recognition components."""
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                self.logger.error("Speech recognition library not available")
                return
            
            if not PYAUDIO_AVAILABLE:
                self.logger.error("PyAudio not available for microphone access")
                return
            
            # Initialize recognizer
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer settings
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Test microphone availability
            try:
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("Speech recognition initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize microphone: {e}")
                self.microphone = None
                
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
    
    def start_listening(self) -> bool:
        """
        Start listening for voice commands.
        
        Returns:
            True if listening started successfully, False otherwise
        """
        try:
            if self.is_listening:
                self.logger.warning("Already listening for voice commands")
                return False
            
            if not self._is_available():
                self.logger.error("Voice recognition not available")
                self.recognition_failed.emit("Voice recognition not available")
                return False
            
            self.is_listening = True
            self.listening_started.emit()
            
            # Start listening in a separate thread
            self.listening_thread = threading.Thread(target=self._listen_for_command, daemon=True)
            self.listening_thread.start()
            
            # Provide feedback to user
            self.feedback_manager.show_notification("Voice Command", "Listening...")
            
            self.logger.info("Started listening for voice commands")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting voice listening: {e}")
            self.is_listening = False
            self.recognition_failed.emit(f"Failed to start listening: {e}")
            return False
    
    def stop_listening(self) -> None:
        """Stop listening for voice commands."""
        try:
            if not self.is_listening:
                return
            
            self.is_listening = False
            
            if self.recognizer:
                self.recognizer.operation_cancel()
            
            self.listening_stopped.emit()
            self.logger.info("Stopped listening for voice commands")
            
        except Exception as e:
            self.logger.error(f"Error stopping voice listening: {e}")
    
    def _listen_for_command(self) -> None:
        """Listen for voice command in a separate thread."""
        try:
            timeout = self.config_manager.get_voice_timeout()
            
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                try:
                    audio = self.recognizer.listen(source, timeout=timeout)
                    
                    if not self.is_listening:
                        return
                    
                    # Recognize speech
                    command = self._recognize_speech(audio)
                    
                    if command and self.is_listening:
                        self.command_recognized.emit(command)
                        
                except sr.WaitTimeoutError:
                    if self.is_listening:
                        self.recognition_failed.emit("Listening timeout - no speech detected")
                except sr.RequestError as e:
                    if self.is_listening:
                        self.recognition_failed.emit(f"Speech recognition service error: {e}")
                except Exception as e:
                    if self.is_listening:
                        self.recognition_failed.emit(f"Error listening for speech: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error in voice listening thread: {e}")
            if self.is_listening:
                self.recognition_failed.emit(f"Voice recognition error: {e}")
        finally:
            self.is_listening = False
            self.listening_stopped.emit()
    
    def _recognize_speech(self, audio) -> Optional[str]:
        """
        Recognize speech from audio data.
        
        Args:
            audio: Audio data from speech recognition
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Speech recognized (Google): {text}")
                return text.lower().strip()
                
            except sr.RequestError as e:
                self.logger.warning(f"Google Speech Recognition failed: {e}")
                
                # Try Sphinx as fallback
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    self.logger.info(f"Speech recognized (Sphinx): {text}")
                    return text.lower().strip()
                except sr.RequestError as e:
                    self.logger.error(f"Sphinx recognition failed: {e}")
                    return None
                    
        except sr.UnknownValueError:
            self.logger.warning("Speech recognition could not understand audio")
            return None
        except Exception as e:
            self.logger.error(f"Error recognizing speech: {e}")
            return None
    
    def _is_available(self) -> bool:
        """Check if voice recognition is available."""
        return (SPEECH_RECOGNITION_AVAILABLE and 
                PYAUDIO_AVAILABLE and 
                self.recognizer is not None and 
                self.microphone is not None)
    
    def test_microphone(self) -> bool:
        """Test microphone functionality."""
        try:
            if not self._is_available():
                return False
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=2)
                
                # Try to recognize something
                text = self._recognize_speech(audio)
                return text is not None
                
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
    
    def get_available_microphones(self) -> list:
        """Get list of available microphones."""
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return []
            
            mic_list = []
            for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
                mic_list.append({
                    'index': i,
                    'name': mic_name
                })
            
            return mic_list
            
        except Exception as e:
            self.logger.error(f"Error getting microphone list: {e}")
            return []
    
    def set_microphone(self, device_index: int) -> bool:
        """
        Set specific microphone device.
        
        Args:
            device_index: Index of microphone device
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return False
            
            self.microphone = sr.Microphone(device_index=device_index)
            
            # Test the new microphone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info(f"Microphone set to device index: {device_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting microphone: {e}")
            return False
    
    def adjust_sensitivity(self, energy_threshold: int) -> bool:
        """
        Adjust microphone sensitivity.
        
        Args:
            energy_threshold: Energy threshold for speech detection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.recognizer:
                self.recognizer.energy_threshold = energy_threshold
                self.logger.info(f"Energy threshold set to: {energy_threshold}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error adjusting sensitivity: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up voice recognition resources."""
        try:
            self.logger.info("Cleaning up voice command handler...")
            
            # Stop listening
            self.stop_listening()
            
            # Wait for thread to finish with longer timeout
            if self.listening_thread and self.listening_thread.is_alive():
                self.logger.info("Waiting for voice thread to finish...")
                self.listening_thread.join(timeout=5)
                
                if self.listening_thread.is_alive():
                    self.logger.warning("Voice thread did not finish gracefully")
            
            # Clean up resources
            self.recognizer = None
            self.microphone = None
            self.listening_thread = None
            
            self.logger.info("Voice command handler cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class VoiceCommandProcessor:
    """Processes recognized voice commands."""
    
    def __init__(self, config_manager, feedback_manager):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.feedback_manager = feedback_manager
        
        # Initialize command processor
        self.command_processor = CommandProcessor(config_manager, feedback_manager)
        
        # Voice-specific command patterns
        self.voice_patterns = {
            'stop_listening': r'(stop|cancel|never mind)',
            'assistant_name': r'(assistant|hey assistant|hello assistant)',
        }
        
        self.logger.info("Voice command processor initialized")
    
    def process_voice_command(self, command_text: str) -> str:
        """
        Process a voice command.
        
        Args:
            command_text: Recognized voice command
            
        Returns:
            Processing result message
        """
        try:
            command_text = command_text.lower().strip()
            
            if not command_text:
                return "Empty command"
            
            self.logger.info(f"Processing voice command: {command_text}")
            
            # Check for voice-specific commands
            for pattern_type, pattern in self.voice_patterns.items():
                import re
                if re.search(pattern, command_text):
                    return self._handle_voice_specific_command(pattern_type)
            
            # Process as regular command
            self.command_processor.process_command(command_text)
            return f"Processing command: {command_text}"
            
        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            return f"Error processing command: {e}"
    
    def _handle_voice_specific_command(self, pattern_type: str) -> str:
        """Handle voice-specific commands."""
        if pattern_type == 'stop_listening':
            return "Voice listening stopped"
        elif pattern_type == 'assistant_name':
            return "I'm listening for your command"
        else:
            return "Unknown voice command"
