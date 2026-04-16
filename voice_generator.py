import os
import requests
import asyncio
import edge_tts
from gtts import gTTS
from typing import Optional

class VoiceGenerator:
    def __init__(self, api_key: Optional[str] = None, service: str = "gtts"):
        self.api_key = api_key
        self.service = service
        # Map common languages to gTTS language codes
        self.lang_map = {
            "English": "en",
            "Hindi": "hi",
            "Telugu": "te",
            "Tamil": "ta",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese": "zh-cn"
        }
        
        # Map common languages to Edge-TTS voice codes
        self.edge_voice_map = {
            "English": "en-US-AriaNeural",
            "Hindi": "hi-IN-MadhurNeural",
            "Telugu": "te-IN-MohanNeural",
            "Tamil": "ta-IN-PallaviNeural",
            "Spanish": "es-ES-AlvaroNeural",
            "French": "fr-FR-DeniseNeural",
            "German": "de-DE-ConradNeural",
            "Italian": "it-IT-ElsaNeural",
            "Japanese": "ja-JP-NanamiNeural",
            "Korean": "ko-KR-SunHiNeural",
            "Chinese": "zh-CN-XiaoxiaoNeural"
        }

    def generate_voiceover(self, text: str, language: str, save_path: str) -> bool:
        """
        Generates voiceover for the given text in the specified language.
        """
        if self.service == "elevenlabs" and self.api_key:
            return self._generate_elevenlabs(text, language, save_path)
        elif self.service == "edge-tts":
            return asyncio.run(self._generate_edge_tts(text, language, save_path))
        else:
            return self._generate_gtts(text, language, save_path)

    async def _generate_edge_tts(self, text: str, language: str, save_path: str) -> bool:
        """
        Generates voiceover using Edge-TTS (Microsoft Edge's free natural voices).
        """
        voice = self.edge_voice_map.get(language, "en-US-AriaNeural")
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(save_path)
            return True
        except Exception as e:
            print(f"Error generating Edge-TTS voiceover: {e}")
            # Fallback to gTTS if Edge-TTS fails
            return self._generate_gtts(text, language, save_path)

    def _generate_gtts(self, text: str, language: str, save_path: str) -> bool:
        """
        Generates voiceover using gTTS.
        """
        lang_code = self.lang_map.get(language, "en")
        try:
            tts = gTTS(text=text, lang=lang_code)
            tts.save(save_path)
            return True
        except Exception as e:
            print(f"Error generating gTTS voiceover: {e}")
            return False

    def _generate_elevenlabs(self, text: str, language: str, save_path: str) -> bool:
        """
        Generates voiceover using ElevenLabs Multilingual v2 model.
        """
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Default Rachel voice
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"Error generating ElevenLabs voiceover: {e}")
            # Fallback to gTTS if ElevenLabs fails
            return self._generate_gtts(text, language, save_path)
