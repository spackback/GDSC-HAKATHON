"""
Voice Processor for Cherry AI Assistant
Handles speech recognition, text-to-speech, and wake word detection
"""

import asyncio
import logging
import threading
import queue
import time
import os
from typing import Callable, Optional, Any, Dict
from io import BytesIO

try:
    import speech_recognition as sr
    import pyaudio
    from gtts import gTTS
    from pygame import mixer
except ImportError:
    print("Voice processing dependencies not installed. Install with:")
    print("pip install SpeechRecognition pyaudio gTTS pygame")
    import sys
    sys.exit(1)

class VoiceProcessor:
    """Handles all voice-related functionality for Cherry"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.event_loop = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.voice_callback = None
        self.stop_background_listening = None
        self.is_active = False

    async def initialize(self):
        """Initialize voice processing components"""
        try:
            self.logger.info("Initializing voice processor...")
            self.event_loop = asyncio.get_running_loop()
            self.microphone = sr.Microphone()
            self.logger.info("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            mixer.init()
            await self.speak("Cherry voice system initialized")
            self.logger.info("Voice processor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize voice processor: {e}")

    async def start_listening(self, voice_callback: Callable[[str], None]):
        """Start continuous voice listening in the background."""
        if self.is_listening or not self.microphone:
            return
        self.voice_callback = voice_callback
        self.is_listening = True
        
        self.stop_background_listening = self.recognizer.listen_in_background(
            self.microphone, 
            self._background_listener_callback,
            phrase_time_limit=10
        )
        self.logger.info("Started continuous voice listening in background.")

    async def stop_listening(self):
        """Stop voice listening."""
        if not self.is_listening:
            return
        self.is_listening = False
        self.is_active = False

        if self.stop_background_listening:
            self.stop_background_listening(wait_for_stop=False)
            self.stop_background_listening = None

        self.logger.info("Stopped voice listening.")

    def _background_listener_callback(self, recognizer, audio):
        """Callback for the background listener. This is called from a separate thread."""
        if not self.is_listening:
            return

        wake_word = self.config.get('WAKE_WORD', 'cherry').lower()
        wake_word_enabled = self.config.get('WAKE_WORD_ENABLED', True)
        use_google_cloud = self._can_use_google_cloud()
        
        try:
            text = self._recognize_audio(audio, use_google_cloud)
            if not text:
                return

            self.logger.info(f"Heard: '{text}'")
            
            if not wake_word_enabled:
                if self.voice_callback:
                    asyncio.run_coroutine_threadsafe(self.voice_callback(text), self.event_loop)
                return

            if self.is_active:
                self.is_active = False
                if self.voice_callback:
                    self.logger.info(f"Processing command: '{text}'")
                    asyncio.run_coroutine_threadsafe(self.voice_callback(text), self.event_loop)
                return

            if wake_word in text:
                command_text = text.split(wake_word, 1)[-1].strip()
                
                if command_text:
                    self.logger.info(f"Processing command: '{command_text}'")
                    if self.voice_callback:
                        asyncio.run_coroutine_threadsafe(self.voice_callback(command_text), self.event_loop)
                else:
                    self.logger.info("Wake word detected. Activating for next command.")
                    self.is_active = True
                    # Use asyncio.run_coroutine_threadsafe because this is called from a non-async thread
                    asyncio.run_coroutine_threadsafe(self.speak("Yes?"), self.event_loop)

        except Exception as e:
            self.logger.error(f"Error in background listener callback: {e}")
            self.is_active = False

    def _recognize_audio(self, audio_data: sr.AudioData, use_google_cloud: bool) -> Optional[str]:
        """Recognizes audio using the configured speech recognition engine."""
        try:
            if use_google_cloud:
                return self.recognizer.recognize_google_cloud(audio_data).lower()
            else:
                return self.recognizer.recognize_google(audio_data).lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition request error: {e}")
            # Use asyncio.run_coroutine_threadsafe as this can be called from a thread
            asyncio.run_coroutine_threadsafe(self.speak("Sorry, I'm having trouble connecting to the speech service."), self.event_loop)
            return None

    def _can_use_google_cloud(self) -> bool:
        """Check if Google Cloud credentials are available"""
        gcp_creds_path = self.config.get('GCP_CREDENTIALS_PATH')
        return gcp_creds_path and os.path.exists(gcp_creds_path)

    async def speak(self, text: str):
        """Asynchronously queue text to be spoken by the TTS worker thread."""
        if not text:
            return
        self.logger.info(f"Speaking: '{text[:50]}...'")
        try:
            tts = gTTS(text=text, lang='en')
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            mixer.music.load(fp)
            mixer.music.play()
            while mixer.music.get_busy():
                await asyncio.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Failed to speak: {e}")


    async def cleanup(self):
        """Cleanup voice processor resources"""
        self.logger.info("Cleaning up voice processor...")
        await self.stop_listening()
        mixer.quit()
        self.logger.info("Voice processor cleanup completed")

    def get_status(self) -> Dict[str, Any]:
        """Get voice processor status"""
        return {
            'is_listening': self.is_listening,
            'is_active': self.is_active,
            'microphone_available': self.microphone is not None,
        }
