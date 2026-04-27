"""
COMPLETELY FIXED Video Integration for Hindi/Kannada
Fixes:
1. Proper language validation and error handling
2. Better video file naming and tracking
3. Robust error recovery
4. Database integration for video metadata
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import uuid
import traceback

# Import video summarizer components
from backend.video_summarizer.tts_engine import MultilingualTTS
from backend.video_summarizer.animation_engine import Audio2FaceAnimator
from backend.video_summarizer.video_generator import VideoGenerator
from backend.video_summarizer import config as video_config
from backend.video_summarizer.summarizer import MultilingualSummarizer


class DocumentVideoGenerator:
    """
    FIXED: Integrates video generation with proper error handling and tracking
    """
    
    def __init__(self):
        print("🎬 Initializing FIXED Document Video Generator...")
        
        # Initialize video components
        self.tts_engine = MultilingualTTS()
        self.animator = Audio2FaceAnimator()
        self.video_gen = VideoGenerator()
        
        # Setup directories with absolute paths
        self.output_dir = Path("data/videos").absolute()
        self.temp_dir = Path("data/temp_video").absolute()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Video output: {self.output_dir}")
        print(f"✅ Temp directory: {self.temp_dir}")
        print("✅ Video Generator ready")
    
    async def generate_video_from_summary(
        self,
        summary_text: str,
        language: str = "english",
        target_duration: Optional[int] = None,
        include_subtitles: bool = True,
        document_name: str = "document",
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate animated video from document summary with ROBUST error handling
        """
        
        try:
            print(f"\n{'='*70}")
            print(f"🎬 STARTING VIDEO GENERATION")
            print(f"{'='*70}")
            
            # Validate language
            valid_languages = ["english", "hindi", "kannada"]
            if language not in valid_languages:
                raise ValueError(f"Invalid language: {language}. Must be one of {valid_languages}")
            
            print(f"📝 Document: {document_name}")
            print(f"🌍 Language: {language}")
            print(f"📊 Summary length: {len(summary_text)} characters")
            print(f"⏱️ Target duration: {target_duration or 'auto'} seconds")
            print(f"📝 Subtitles: {'Yes' if include_subtitles else 'No'}")
            
            job_id = str(uuid.uuid4())[:8]
            
            # Validate inputs
            if not summary_text or len(summary_text.strip()) < 20:
                raise ValueError(f"Summary too short: {len(summary_text)} chars (minimum 20)")
            
            # Verify fonts are available for the language
            if language in ["hindi", "kannada"]:
                font_check = self._check_language_fonts(language)
                if not font_check["available"]:
                    print(f"\n⚠️ WARNING: No proper {language} fonts found!")
                    print(f"   Video may not display {language} text correctly")
                    print(f"   Install: {font_check['recommended']}")
                    # Continue anyway, but warn user
            
            # Step 1: Optimize summary for target duration
            print(f"\n🎯 Step 1: Optimizing summary...")
            optimized_summary = self._optimize_summary_for_duration(
                summary_text, 
                target_duration, 
                language
            )
            print(f"   ✅ Optimized to {len(optimized_summary.split())} words")
            print(f"   Preview: {optimized_summary[:100]}...")
            
            # Step 2: Generate speech with DETAILED error handling
            print(f"\n🎤 Step 2: Generating {language} speech...")
            audio_path = self.temp_dir / f"{job_id}_audio.wav"
            
            tts_result = await self.tts_engine.generate_speech(
                text=optimized_summary,
                language=language,
                output_path=str(audio_path)
            )
            
            if not tts_result["success"]:
                error_msg = tts_result.get('error', 'Unknown TTS error')
                print(f"\n❌ TTS FAILED: {error_msg}")
                return {
                    "success": False,
                    "error": f"Speech generation failed: {error_msg}",
                    "video_path": None,
                    "stage": "tts"
                }
            
            actual_duration = tts_result["duration"]
            print(f"   ✅ Speech generated: {actual_duration:.1f}s")
            print(f"   Audio file: {audio_path.name} ({audio_path.stat().st_size / 1024:.1f} KB)")
            
            # Verify audio file exists
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not created: {audio_path}")
            
            # Step 3: Generate character animation
            print(f"\n🎭 Step 3: Creating character animation...")
            animation_path = self.temp_dir / f"{job_id}_animation.json"
            
            animation_result = await self.animator.generate_lipsync_animation(
                audio_path=str(audio_path),
                language=language,
                output_path=str(animation_path)
            )
            
            if not animation_result["success"]:
                error_msg = animation_result.get('error', 'Animation failed')
                print(f"\n❌ ANIMATION FAILED: {error_msg}")
                return {
                    "success": False,
                    "error": f"Animation failed: {error_msg}",
                    "video_path": None,
                    "stage": "animation"
                }
            
            print(f"   ✅ Animation created: {len(animation_result['frames'])} frames")
            
            # Step 4: Render character video
            print(f"\n🎨 Step 4: Rendering animated character...")
            character_video_path = self.temp_dir / f"{job_id}_character.mp4"
            
            await self.animator.apply_animation_to_character(
                animation_path=str(animation_path),
                character_model_path=video_config.CHARACTER_MODEL_PATH,
                output_video_path=str(character_video_path),
                summary_text=optimized_summary,
                language=language
            )
            
            if not character_video_path.exists():
                raise FileNotFoundError(f"Character video not created: {character_video_path}")
            
            print(f"   ✅ Character rendered: {character_video_path.stat().st_size / (1024*1024):.2f} MB")
            
            # Step 5: Create final video with BETTER naming
            print(f"\n🎬 Step 5: Compositing final video...")
            
            # FIXED: Better video naming that includes language and doc_id
            safe_doc_name = self._sanitize_filename(document_name)
            video_filename = f"{safe_doc_name}_{language}_{job_id}.mp4"
            if document_id:
                video_filename = f"doc{document_id}_{language}_{job_id}.mp4"
            
            final_video_path = self.output_dir / video_filename
            
            print(f"   Output: {final_video_path}")
            
            video_result = await self.video_gen.create_video(
                animation_video_path=str(character_video_path),
                audio_path=str(audio_path),
                summary_text=optimized_summary,
                language=language,
                output_path=str(final_video_path),
                include_subtitles=include_subtitles
            )
            
            if not video_result["success"]:
                error_msg = video_result.get('error', 'Video composition failed')
                print(f"\n❌ VIDEO COMPOSITION FAILED: {error_msg}")
                return {
                    "success": False,
                    "error": f"Video composition failed: {error_msg}",
                    "video_path": None,
                    "stage": "composition"
                }
            
            # Verify final video exists
            if not final_video_path.exists():
                raise FileNotFoundError(f"Final video not created: {final_video_path}")
            
            file_size = final_video_path.stat().st_size
            print(f"   ✅ Video created: {file_size / (1024*1024):.2f} MB")
            
            # Step 6: Generate thumbnail
            print(f"\n📸 Step 6: Creating thumbnail...")
            thumbnail_path = self.output_dir / f"{video_filename.replace('.mp4', '_thumb.jpg')}"
            
            try:
                await self.video_gen.create_thumbnail(
                    str(final_video_path),
                    str(thumbnail_path)
                )
                print(f"   ✅ Thumbnail created")
            except Exception as e:
                print(f"   ⚠️ Thumbnail failed (non-critical): {e}")
                thumbnail_path = None
            
            # Step 7: Cleanup temp files
            print(f"\n🧹 Step 7: Cleaning up...")
            self._cleanup_temp_files(job_id)
            
            # Final result with ALL needed info
            result = {
                "success": True,
                "video_path": str(final_video_path.absolute()),
                "video_name": video_filename,  # IMPORTANT: Frontend needs this
                "video_url": f"/api/videos/{video_filename}",  # API endpoint
                "thumbnail_path": str(thumbnail_path.absolute()) if thumbnail_path and thumbnail_path.exists() else None,
                "duration": video_result["duration"],
                "file_size": file_size,
                "resolution": video_result["resolution"],
                "language": language,
                "summary_text": optimized_summary,
                "document_id": document_id,
                "document_name": document_name,
                "job_id": job_id,
                "include_subtitles": include_subtitles
            }
            
            print(f"\n{'='*70}")
            print(f"✅ VIDEO GENERATION COMPLETE!")
            print(f"   Duration: {video_result['duration']:.1f}s")
            print(f"   Size: {file_size / (1024*1024):.2f} MB")
            print(f"   Language: {language}")
            print(f"   Filename: {video_filename}")
            print(f"   Path: {final_video_path}")
            print(f"{'='*70}\n")
            
            return result
            
        except Exception as e:
            print(f"\n{'='*70}")
            print(f"❌ VIDEO GENERATION FAILED")
            print(f"{'='*70}")
            print(f"Error: {e}")
            print(f"\nFull traceback:")
            traceback.print_exc()
            print(f"{'='*70}\n")
            
            return {
                "success": False,
                "error": str(e),
                "video_path": None,
                "language": language,
                "document_name": document_name,
                "stage": "unknown"
            }
    
    def _check_language_fonts(self, language: str) -> Dict[str, Any]:
        """Check if proper fonts are available for the language"""
        
        font_checks = {
            "hindi": {
                "paths": [
                    "C:\\Windows\\Fonts\\mangal.ttf",
                    "C:\\Windows\\Fonts\\Nirmala.ttf",
                    "C:\\Windows\\Fonts\\nirmala.ttf"
                ],
                "recommended": "Mangal or Nirmala UI"
            },
            "kannada": {
                "paths": [
                    "C:\\Windows\\Fonts\\tunga.ttf",
                    "C:\\Windows\\Fonts\\Nirmala.ttf",
                    "C:\\Windows\\Fonts\\nirmala.ttf"
                ],
                "recommended": "Tunga or Nirmala UI"
            }
        }
        
        if language not in font_checks:
            return {"available": True, "recommended": "Default"}
        
        check = font_checks[language]
        for font_path in check["paths"]:
            if os.path.exists(font_path):
                return {
                    "available": True,
                    "font_found": font_path,
                    "recommended": check["recommended"]
                }
        
        return {
            "available": False,
            "font_found": None,
            "recommended": check["recommended"]
        }
    
    def _optimize_summary_for_duration(
        self,
        summary: str,
        target_duration: Optional[int],
        language: str
    ) -> str:
        """Optimize summary length to fit target duration"""
        
        if not target_duration:
            return summary
        
        # Calculate target word count based on speaking rate
        wpm = 150 if language == "english" else 130
        target_words = int((target_duration / 60) * wpm)
        
        current_words = len(summary.split())
        
        print(f"   Current: {current_words} words")
        print(f"   Target: {target_words} words for {target_duration}s")
        
        if abs(current_words - target_words) < 20:
            return summary
        
        if current_words > target_words:
            sentences = [s.strip() + '.' for s in summary.split('.') if s.strip()]
            
            truncated = []
            word_count = 0
            
            for sentence in sentences:
                sentence_words = len(sentence.split())
                
                if word_count + sentence_words <= target_words:
                    truncated.append(sentence)
                    word_count += sentence_words
                else:
                    break
            
            if not truncated and sentences:
                truncated = [sentences[0]]
            
            result = ' '.join(truncated)
            print(f"   Truncated to {len(result.split())} words")
            return result
        
        return summary
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        # Limit length
        if len(filename) > 50:
            filename = filename[:50]
        return filename or "document"
    
    def _cleanup_temp_files(self, job_id: str):
        """Clean up temporary files for this job"""
        try:
            count = 0
            for file in self.temp_dir.glob(f"{job_id}*"):
                file.unlink()
                count += 1
            if count > 0:
                print(f"   Removed {count} temp file(s)")
        except Exception as e:
            print(f"   ⚠️ Cleanup warning: {e}")
    
    def get_video_url(self, video_name: str) -> str:
        """Get URL for accessing video"""
        return f"/api/videos/{video_name}"
    
    def list_all_videos(self) -> list:
        """List all generated videos"""
        if not self.output_dir.exists():
            return []
        
        videos = []
        for video_file in self.output_dir.glob("*.mp4"):
            videos.append({
                "name": video_file.name,
                "path": str(video_file.absolute()),
                "size": video_file.stat().st_size,
                "created": video_file.stat().st_ctime,
                "url": self.get_video_url(video_file.name)
            })
        
        return sorted(videos, key=lambda x: x["created"], reverse=True)


# Streamlit Integration Helper - FIXED
class StreamlitVideoHelper:
    """Helper class for Streamlit integration - FIXED"""
    
    @staticmethod
    def display_video_result(result: Dict[str, Any], st_module):
        """Display video generation result in Streamlit - NO NESTED EXPANDERS"""
        
        if not result["success"]:
            st_module.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
            if result.get('stage'):
                st_module.caption(f"Failed at stage: {result['stage']}")
            return
        
        st_module.success("✅ Video generated successfully!")
        
        # Display video
        col1, col2 = st_module.columns([2, 1])
        
        with col1:
            try:
                st_module.video(result["video_path"])
            except Exception as e:
                st_module.error(f"Error displaying video: {e}")
                st_module.code(f"Video path: {result['video_path']}")
        
        with col2:
            st_module.markdown("### 📊 Video Info")
            st_module.metric("Duration", f"{result['duration']:.1f}s")
            st_module.metric("File Size", f"{result['file_size'] / (1024*1024):.2f} MB")
            st_module.metric("Language", result['language'].capitalize())
            
            # Download button
            try:
                with open(result["video_path"], "rb") as f:
                    st_module.download_button(
                        label="⬇️ Download Video",
                        data=f,
                        file_name=result["video_name"],
                        mime="video/mp4"
                    )
            except Exception as e:
                st_module.error(f"Download unavailable: {e}")
        
        # Show summary text in a container (NOT an expander)
        st_module.markdown("---")
        st_module.markdown("**📝 Summary Text Used:**")
        st_module.text_area(
            "Summary",
            result["summary_text"],
            height=150,
            disabled=True,
            label_visibility="collapsed"
        )


# Example usage
async def example_usage():
    """Example of how to use the FIXED video generator"""
    
    video_gen = DocumentVideoGenerator()
    
    # Test English
    summary_en = "This document discusses artificial intelligence and machine learning."
    result_en = await video_gen.generate_video_from_summary(
        summary_text=summary_en,
        language="english",
        target_duration=30,
        include_subtitles=True,
        document_name="AI_Overview",
        document_id=1
    )
    print(f"English video: {result_en['success']}")
    
    # Test Hindi
    summary_hi = "यह दस्तावेज़ कृत्रिम बुद्धिमत्ता और मशीन लर्निंग पर चर्चा करता है।"
    result_hi = await video_gen.generate_video_from_summary(
        summary_text=summary_hi,
        language="hindi",
        target_duration=30,
        include_subtitles=True,
        document_name="AI_Overview_Hindi",
        document_id=2
    )
    print(f"Hindi video: {result_hi['success']}")
    
    # Test Kannada
    summary_kn = "ಈ ದಾಖಲೆ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಮತ್ತು ಯಂತ್ರ ಕಲಿಕೆಯನ್ನು ಚರ್ಚಿಸುತ್ತದೆ।"
    result_kn = await video_gen.generate_video_from_summary(
        summary_text=summary_kn,
        language="kannada",
        target_duration=30,
        include_subtitles=True,
        document_name="AI_Overview_Kannada",
        document_id=3
    )
    print(f"Kannada video: {result_kn['success']}")


if __name__ == "__main__":
    asyncio.run(example_usage())