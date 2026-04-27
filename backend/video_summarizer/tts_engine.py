"""
COMPLETELY FIXED TTS Engine with VERIFIED Hindi/Kannada Support
Tests gTTS codes and provides detailed error messages
"""

import os
from typing import Dict, Any
from pydub import AudioSegment
from gtts import gTTS
from backend.video_summarizer import config


class MultilingualTTS:
    """
    Fixed TTS with VERIFIED language codes
    """
    
    def __init__(self):
        print("🎤 Initializing FIXED Multilingual TTS...")
        
        # VERIFIED gTTS language codes (tested and working)
        self.lang_codes = {
            "english": "en",
            "hindi": "hi",      # ✅ Verified working
            "kannada": "kn"     # ✅ Verified working
        }
        
        # Test if gTTS supports these languages
        print("   Testing gTTS language support...")
        self._test_language_support()
        
        print("✅ TTS engine initialized")
    
    def _test_language_support(self):
        """Test if gTTS supports our languages"""
        try:
            from gtts.lang import tts_langs
            supported = tts_langs()
            
            print("   gTTS supported languages:")
            for lang_name, lang_code in self.lang_codes.items():
                if lang_code in supported:
                    print(f"   ✅ {lang_name} ({lang_code}): {supported[lang_code]}")
                else:
                    print(f"   ❌ {lang_name} ({lang_code}): NOT SUPPORTED")
            
        except Exception as e:
            print(f"   ⚠️ Could not verify language support: {e}")
    
    async def generate_speech(
        self,
        text: str,
        language: str,
        output_path: str,
        speaker_voice: str = "female"
    ) -> Dict[str, Any]:
        """Generate speech using gTTS with DETAILED error handling"""
        try:
            print(f"\n   🎯 Generating {language} speech...")
            print(f"   Text length: {len(text)} characters")
            print(f"   Text preview: {text[:150]}...")
            
            # Get language code
            lang_code = self.lang_codes.get(language)
            if not lang_code:
                raise ValueError(f"Unsupported language: {language}")
            
            print(f"   Using gTTS language code: '{lang_code}'")
            
            # Validate text
            if not text or len(text.strip()) < 5:
                raise ValueError(f"Text too short for TTS: '{text}'")
            
            # Test if text contains proper characters for the language
            if language == "hindi":
                has_hindi = any('\u0900' <= char <= '\u097F' for char in text)
                if not has_hindi:
                    print(f"   ⚠️ WARNING: Text doesn't contain Hindi (Devanagari) characters!")
                    print(f"   Text: {text[:100]}")
            elif language == "kannada":
                has_kannada = any('\u0C80' <= char <= '\u0CFF' for char in text)
                if not has_kannada:
                    print(f"   ⚠️ WARNING: Text doesn't contain Kannada characters!")
                    print(f"   Text: {text[:100]}")
            
            # Generate speech with detailed error catching
            print(f"   Calling gTTS...")
            try:
                tts = gTTS(text=text, lang=lang_code, slow=False)
            except Exception as e:
                print(f"   ❌ gTTS creation failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                raise
            
            # Save to temp MP3
            temp_mp3 = output_path.replace('.wav', '_temp.mp3')
            print(f"   Saving MP3 to: {os.path.basename(temp_mp3)}")
            
            try:
                tts.save(temp_mp3)
            except Exception as e:
                print(f"   ❌ MP3 save failed: {e}")
                raise
            
            if not os.path.exists(temp_mp3):
                raise FileNotFoundError(f"TTS did not create MP3 file: {temp_mp3}")
            
            mp3_size = os.path.getsize(temp_mp3)
            print(f"   ✅ MP3 created: {mp3_size / 1024:.2f} KB")
            
            # Convert to WAV with better quality
            print("   Converting MP3 to WAV...")
            try:
                audio = AudioSegment.from_mp3(temp_mp3)
                print(f"   Audio loaded: {len(audio)}ms, {audio.frame_rate}Hz")
            except Exception as e:
                print(f"   ❌ MP3 to WAV conversion failed: {e}")
                raise
            
            # Enhance audio quality
            audio = audio.set_channels(2)  # Stereo
            audio = audio.set_frame_rate(44100)  # CD quality
            audio = audio.normalize()  # Normalize volume
            audio = audio + 2  # Slight boost
            
            # Export as WAV
            print(f"   Exporting WAV to: {os.path.basename(output_path)}")
            audio.export(output_path, format='wav')
            
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Failed to create WAV file: {output_path}")
            
            wav_size = os.path.getsize(output_path)
            print(f"   ✅ WAV exported: {wav_size / 1024:.2f} KB")
            
            # Get duration
            duration = len(audio) / 1000.0
            
            # Cleanup temp file
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
                print(f"   Cleaned up temp MP3")
            
            print(f"   ✅ {language} speech generated successfully: {duration:.1f}s")
            
            return {
                "success": True,
                "audio_path": output_path,
                "duration": duration,
                "language": language,
                "backend": "gTTS",
                "quality": "good",
                "sample_rate": 44100,
                "channels": 2
            }
            
        except Exception as e:
            print(f"\n   ❌ TTS COMPLETE FAILURE FOR {language}")
            print(f"   Error: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            import traceback
            print("\n   Full traceback:")
            traceback.print_exc()
            
            # Provide helpful debug info
            print(f"\n   Debug Info:")
            print(f"   - Language: {language}")
            print(f"   - Lang code: {self.lang_codes.get(language, 'NOT FOUND')}")
            print(f"   - Text length: {len(text)}")
            print(f"   - Output path: {output_path}")
            
            return {
                "success": False,
                "error": str(e),
                "audio_path": None,
                "language": language
            }
    
    async def adjust_audio_speed(
        self,
        audio_path: str,
        target_duration: float,
        output_path: str
    ) -> str:
        """Adjust audio speed to fit target duration"""
        try:
            audio = AudioSegment.from_file(audio_path)
            current_duration = len(audio) / 1000.0
            
            speed_factor = current_duration / target_duration
            
            # Only adjust if reasonable (0.8x to 1.3x)
            if 0.8 <= speed_factor <= 1.3:
                print(f"   ⚙️ Adjusting speed: {speed_factor:.2f}x")
                
                # Use FFmpeg for better quality speed adjustment
                adjusted = audio._spawn(
                    audio.raw_data,
                    overrides={
                        "frame_rate": int(audio.frame_rate * speed_factor)
                    }
                ).set_frame_rate(audio.frame_rate)
                
                adjusted.export(output_path, format="wav")
                print(f"   ✅ Audio speed adjusted")
                return output_path
            else:
                print(f"   ⚠️ Speed factor {speed_factor:.2f}x too extreme, keeping original")
                return audio_path
                
        except Exception as e:
            print(f"   ⚠️ Speed adjustment failed: {e}")
            return audio_path


# """
# OFFLINE TTS Engine - Works Without Internet Connection
# Uses pyttsx3 for offline speech synthesis
# Falls back to gTTS only if online and pyttsx3 fails

# Install required package:
#     pip install pyttsx3
# """

# import os
# from typing import Dict, Any
# from pydub import AudioSegment
# import tempfile
# from backend.video_summarizer import config

# # Try to import offline TTS first (priority)
# try:
#     import pyttsx3
#     PYTTSX3_AVAILABLE = True
#     print("✅ Offline TTS (pyttsx3) available")
# except ImportError:
#     PYTTSX3_AVAILABLE = False
#     print("⚠️ pyttsx3 not found. Install: pip install pyttsx3")

# # Try to import online TTS as backup
# try:
#     from gtts import gTTS
#     GTTS_AVAILABLE = True
#     print("✅ Online TTS (gTTS) available as backup")
# except ImportError:
#     GTTS_AVAILABLE = False
#     print("⚠️ gTTS not available")


# class MultilingualTTS:
#     """
#     Offline-First TTS Engine
#     - Primary: pyttsx3 (works offline, fast)
#     - Backup: gTTS (requires internet, better quality for Hindi/Kannada)
#     """
    
#     def __init__(self):
#         print("🎤 Initializing Offline-First TTS Engine...")
        
#         # Language codes for gTTS
#         self.lang_codes = {
#             "english": "en",
#             "hindi": "hi",
#             "kannada": "kn"
#         }
        
#         # Initialize pyttsx3 engine
#         self.offline_engine = None
#         self.offline_available = False
        
#         if PYTTSX3_AVAILABLE:
#             try:
#                 self.offline_engine = pyttsx3.init()
                
#                 # Configure voice settings
#                 self.offline_engine.setProperty('rate', 150)  # Speed
#                 self.offline_engine.setProperty('volume', 0.9)  # Volume
                
#                 # Try to find a good voice
#                 voices = self.offline_engine.getProperty('voices')
#                 if voices:
#                     # Prefer female voice if available
#                     for voice in voices:
#                         if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
#                             self.offline_engine.setProperty('voice', voice.id)
#                             print(f"   Selected voice: {voice.name}")
#                             break
#                     else:
#                         self.offline_engine.setProperty('voice', voices[0].id)
#                         print(f"   Selected voice: {voices[0].name}")
                
#                 self.offline_available = True
#                 print("   ✅ Offline TTS engine initialized")
                
#             except Exception as e:
#                 print(f"   ⚠️ Offline TTS init failed: {e}")
#                 self.offline_available = False
        
#         print("✅ TTS Engine ready")
    
#     async def generate_speech(
#         self,
#         text: str,
#         language: str,
#         output_path: str,
#         speaker_voice: str = "female"
#     ) -> Dict[str, Any]:
#         """
#         Generate speech - tries offline first, then online
#         """
#         print(f"\n🎯 Generating {language} speech...")
#         print(f"   Text length: {len(text)} characters")
#         print(f"   Text preview: {text[:100]}...")
        
#         # Validate text
#         if not text or len(text.strip()) < 5:
#             return {
#                 "success": False,
#                 "error": "Text too short for TTS",
#                 "audio_path": None,
#                 "language": language
#             }
        
#         # Try offline TTS first (pyttsx3)
#         if self.offline_available:
#             print("   📢 Trying offline TTS (pyttsx3)...")
#             result = await self._generate_offline(text, language, output_path)
            
#             if result["success"]:
#                 return result
#             else:
#                 print(f"   ⚠️ Offline TTS failed: {result.get('error')}")
        
#         # Try online TTS as backup (gTTS)
#         if GTTS_AVAILABLE:
#             print("   🌐 Trying online TTS (gTTS)...")
#             result = await self._generate_online(text, language, output_path)
            
#             if result["success"]:
#                 return result
#             else:
#                 print(f"   ⚠️ Online TTS failed: {result.get('error')}")
        
#         # Both failed
#         return {
#             "success": False,
#             "error": "All TTS methods failed. Check internet connection or install pyttsx3.",
#             "audio_path": None,
#             "language": language
#         }
    
#     async def _generate_offline(
#         self,
#         text: str,
#         language: str,
#         output_path: str
#     ) -> Dict[str, Any]:
#         """Generate speech using pyttsx3 (offline)"""
        
#         try:
#             # Create temp file for pyttsx3 output
#             temp_wav = output_path.replace('.wav', '_pyttsx3_temp.wav')
            
#             # Note: pyttsx3 doesn't support Hindi/Kannada text-to-speech natively
#             # It will read the text but pronunciation may not be accurate
#             if language != "english":
#                 print(f"   ⚠️ Note: Offline TTS may not pronounce {language} accurately")
            
#             # Generate speech
#             self.offline_engine.save_to_file(text, temp_wav)
#             self.offline_engine.runAndWait()
            
#             # Check if file was created
#             if not os.path.exists(temp_wav):
#                 raise FileNotFoundError("pyttsx3 did not create audio file")
            
#             file_size = os.path.getsize(temp_wav)
#             if file_size < 1000:  # Less than 1KB is suspicious
#                 raise ValueError(f"Audio file too small: {file_size} bytes")
            
#             print(f"   ✅ Offline audio created: {file_size / 1024:.2f} KB")
            
#             # Enhance audio quality
#             audio = AudioSegment.from_wav(temp_wav)
            
#             # Normalize and enhance
#             audio = audio.set_channels(2)  # Stereo
#             audio = audio.set_frame_rate(44100)  # CD quality
#             audio = audio.normalize()  # Normalize volume
#             audio = audio + 3  # Slight volume boost
            
#             # Export final audio
#             audio.export(output_path, format='wav')
            
#             # Get duration
#             duration = len(audio) / 1000.0
            
#             # Cleanup temp file
#             if os.path.exists(temp_wav):
#                 os.remove(temp_wav)
            
#             print(f"   ✅ Offline speech generated: {duration:.1f}s")
            
#             return {
#                 "success": True,
#                 "audio_path": output_path,
#                 "duration": duration,
#                 "language": language,
#                 "backend": "pyttsx3 (offline)",
#                 "quality": "good",
#                 "sample_rate": 44100,
#                 "channels": 2
#             }
            
#         except Exception as e:
#             print(f"   ❌ Offline TTS error: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "audio_path": None,
#                 "language": language
#             }
    
#     async def _generate_online(
#         self,
#         text: str,
#         language: str,
#         output_path: str
#     ) -> Dict[str, Any]:
#         """Generate speech using gTTS (online)"""
        
#         try:
#             lang_code = self.lang_codes.get(language, "en")
#             print(f"   Using gTTS with language code: {lang_code}")
            
#             # Create gTTS object
#             tts = gTTS(text=text, lang=lang_code, slow=False)
            
#             # Save to temp MP3
#             temp_mp3 = output_path.replace('.wav', '_gtts_temp.mp3')
#             tts.save(temp_mp3)
            
#             if not os.path.exists(temp_mp3):
#                 raise FileNotFoundError("gTTS did not create MP3 file")
            
#             mp3_size = os.path.getsize(temp_mp3)
#             print(f"   ✅ Online audio created: {mp3_size / 1024:.2f} KB")
            
#             # Convert to WAV
#             audio = AudioSegment.from_mp3(temp_mp3)
            
#             # Enhance audio
#             audio = audio.set_channels(2)
#             audio = audio.set_frame_rate(44100)
#             audio = audio.normalize()
#             audio = audio + 2
            
#             # Export
#             audio.export(output_path, format='wav')
            
#             # Get duration
#             duration = len(audio) / 1000.0
            
#             # Cleanup
#             if os.path.exists(temp_mp3):
#                 os.remove(temp_mp3)
            
#             print(f"   ✅ Online speech generated: {duration:.1f}s")
            
#             return {
#                 "success": True,
#                 "audio_path": output_path,
#                 "duration": duration,
#                 "language": language,
#                 "backend": "gTTS (online)",
#                 "quality": "high",
#                 "sample_rate": 44100,
#                 "channels": 2
#             }
            
#         except Exception as e:
#             error_msg = str(e).lower()
            
#             if "failed to connect" in error_msg or "connection" in error_msg:
#                 print("   ❌ No internet connection available")
            
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "audio_path": None,
#                 "language": language
#             }
    
#     async def adjust_audio_speed(
#         self,
#         audio_path: str,
#         target_duration: float,
#         output_path: str
#     ) -> str:
#         """Adjust audio speed to fit target duration"""
#         try:
#             audio = AudioSegment.from_file(audio_path)
#             current_duration = len(audio) / 1000.0
            
#             speed_factor = current_duration / target_duration
            
#             # Only adjust if reasonable (0.8x to 1.3x)
#             if 0.8 <= speed_factor <= 1.3:
#                 print(f"   ⚙️ Adjusting speed: {speed_factor:.2f}x")
                
#                 adjusted = audio._spawn(
#                     audio.raw_data,
#                     overrides={
#                         "frame_rate": int(audio.frame_rate * speed_factor)
#                     }
#                 ).set_frame_rate(audio.frame_rate)
                
#                 adjusted.export(output_path, format="wav")
#                 print(f"   ✅ Audio speed adjusted")
#                 return output_path
#             else:
#                 print(f"   ⚠️ Speed factor {speed_factor:.2f}x too extreme, keeping original")
#                 return audio_path
                
#         except Exception as e:
#             print(f"   ⚠️ Speed adjustment failed: {e}")
#             return audio_path


# # Test function
# async def test_tts():
#     """Test TTS functionality"""
#     tts = MultilingualTTS()
    
#     # Test English
#     result = await tts.generate_speech(
#         text="Hello, this is a test of the text to speech system.",
#         language="english",
#         output_path="test_english.wav"
#     )
#     print(f"English TTS: {result}")
    
#     # Test Hindi
#     result = await tts.generate_speech(
#         text="नमस्ते, यह एक परीक्षण है।",
#         language="hindi",
#         output_path="test_hindi.wav"
#     )
#     print(f"Hindi TTS: {result}")


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test_tts())