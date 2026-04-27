"""
Video Generation Integration for AI Document Intelligence System
Converts document summaries to animated videos with narration
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

# Import video summarizer components
from backend.video_summarizer.tts_engine import MultilingualTTS
from backend.video_summarizer.animation_engine import Audio2FaceAnimator
from backend.video_summarizer.video_generator import VideoGenerator
from backend.video_summarizer import config as video_config
from backend.video_summarizer.summarizer import MultilingualSummarizer


class DocumentVideoGenerator:
    """
    Integrates video generation with document summarization
    """
    
    def __init__(self):
        print("🎬 Initializing Document Video Generator...")
        
        # Initialize video components
        self.tts_engine = MultilingualTTS()
        self.animator = Audio2FaceAnimator()
        self.video_gen = VideoGenerator()
        
        # Setup directories
        self.output_dir = Path("data/videos")
        self.temp_dir = Path("data/temp_video")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Video Generator ready")
    
    async def generate_video_from_summary(
        self,
        summary_text: str,
        language: str = "english",
        target_duration: Optional[int] = None,
        include_subtitles: bool = True,
        document_name: str = "document"
    ) -> Dict[str, Any]:
        """
        Generate animated video from document summary
        
        Args:
            summary_text: The summary to convert to video
            language: Language for narration (english/hindi/kannada)
            target_duration: Target video duration in seconds (None for auto)
            include_subtitles: Whether to include text overlays
            document_name: Name of source document for file naming
            
        Returns:
            Dict with video path, duration, and metadata
        """
        
        try:
            print(f"\n{'='*70}")
            print(f"🎬 Generating Video for: {document_name}")
            print(f"{'='*70}")
            
            job_id = str(uuid.uuid4())[:8]
            
            # Validate inputs
            if not summary_text or len(summary_text.strip()) < 20:
                raise ValueError("Summary too short (minimum 20 characters)")
            
            print(f"📝 Summary: {len(summary_text)} characters")
            print(f"🌐 Language: {language}")
            print(f"⏱️ Target duration: {target_duration or 'auto'} seconds")
            
            # Step 1: Optimize summary for target duration
            print("\n🎯 Step 1: Optimizing summary for video...")
            optimized_summary = self._optimize_summary_for_duration(
                summary_text, 
                target_duration, 
                language
            )
            print(f"   ✅ Optimized to {len(optimized_summary.split())} words")
            
            # Step 2: Generate speech
            print("\n🎤 Step 2: Converting text to speech...")
            audio_path = self.temp_dir / f"{job_id}_audio.wav"
            
            tts_result = await self.tts_engine.generate_speech(
                text=optimized_summary,
                language=language,
                output_path=str(audio_path)
            )
            
            if not tts_result["success"]:
                raise Exception(f"TTS failed: {tts_result.get('error', 'Unknown error')}")
            
            actual_duration = tts_result["duration"]
            print(f"   ✅ Speech generated: {actual_duration:.1f}s")
            
            # Step 3: Adjust audio speed if needed
            if target_duration and abs(actual_duration - target_duration) > 5:
                print(f"\n⚙️ Step 3: Adjusting audio speed...")
                adjusted_audio_path = self.temp_dir / f"{job_id}_audio_adjusted.wav"
                audio_path = await self.tts_engine.adjust_audio_speed(
                    str(audio_path),
                    target_duration,
                    str(adjusted_audio_path)
                )
                print(f"   ✅ Audio adjusted to fit {target_duration}s")
            
            # Step 4: Generate character animation
            print(f"\n🎭 Step 4: Creating character animation...")
            animation_path = self.temp_dir / f"{job_id}_animation.json"
            
            animation_result = await self.animator.generate_lipsync_animation(
                audio_path=str(audio_path),
                language=language,
                output_path=str(animation_path)
            )
            
            if not animation_result["success"]:
                raise Exception("Animation generation failed")
            
            print(f"   ✅ Animation created: {len(animation_result['frames'])} frames")
            
            # Step 5: Render character video
            print(f"\n🎨 Step 5: Rendering animated character...")
            character_video_path = self.temp_dir / f"{job_id}_character.mp4"
            
            await self.animator.apply_animation_to_character(
                animation_path=str(animation_path),
                character_model_path=video_config.CHARACTER_MODEL_PATH,
                output_video_path=str(character_video_path),
                summary_text=optimized_summary,
                language=language
            )
            print(f"   ✅ Character rendered")
            
            # Step 6: Create final video
            print(f"\n🎬 Step 6: Compositing final video...")
            final_video_name = f"{document_name}_{job_id}_summary.mp4"
            final_video_path = self.output_dir / final_video_name
            
            video_result = await self.video_gen.create_video(
                animation_video_path=str(character_video_path),
                audio_path=str(audio_path),
                summary_text=optimized_summary,
                language=language,
                output_path=str(final_video_path),
                include_subtitles=include_subtitles
            )
            
            if not video_result["success"]:
                raise Exception("Video composition failed")
            
            print(f"   ✅ Video created: {video_result['file_size'] / (1024*1024):.2f} MB")
            
            # Step 7: Generate thumbnail
            print(f"\n📸 Step 7: Creating thumbnail...")
            thumbnail_path = self.output_dir / f"{document_name}_{job_id}_thumb.jpg"
            await self.video_gen.create_thumbnail(
                str(final_video_path),
                str(thumbnail_path)
            )
            
            # Cleanup temp files
            print(f"\n🧹 Cleaning up temporary files...")
            self._cleanup_temp_files(job_id)
            
            result = {
                "success": True,
                "video_path": str(final_video_path),
                "thumbnail_path": str(thumbnail_path),
                "duration": video_result["duration"],
                "file_size": video_result["file_size"],
                "resolution": video_result["resolution"],
                "language": language,
                "summary_text": optimized_summary,
                "job_id": job_id
            }
            
            print(f"\n{'='*70}")
            print(f"✅ VIDEO GENERATION COMPLETE!")
            print(f"   Duration: {video_result['duration']:.1f}s")
            print(f"   Size: {video_result['file_size'] / (1024*1024):.2f} MB")
            print(f"   Output: {final_video_path.name}")
            print(f"{'='*70}\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Video generation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "video_path": None
            }
    
    def _optimize_summary_for_duration(
        self,
        summary: str,
        target_duration: Optional[int],
        language: str
    ) -> str:
        """
        Optimize summary length to fit target duration
        """
        
        # If no target duration, return as-is
        if not target_duration:
            return summary
        
        # Calculate target word count based on speaking rate
        # English: ~150 WPM, Hindi/Kannada: ~130 WPM
        wpm = 150 if language == "english" else 130
        target_words = int((target_duration / 60) * wpm)
        
        current_words = len(summary.split())
        
        print(f"   Current: {current_words} words")
        print(f"   Target: {target_words} words for {target_duration}s")
        
        # If already close, return as-is
        if abs(current_words - target_words) < 20:
            return summary
        
        # If too long, truncate intelligently
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
            
            # Ensure we have at least some content
            if not truncated and sentences:
                truncated = [sentences[0]]
            
            result = ' '.join(truncated)
            print(f"   Truncated to {len(result.split())} words")
            return result
        
        # If too short, return as-is (better short than padded)
        return summary
    
    def _cleanup_temp_files(self, job_id: str):
        """Clean up temporary files for this job"""
        try:
            for file in self.temp_dir.glob(f"{job_id}*"):
                file.unlink()
                print(f"   Removed: {file.name}")
        except Exception as e:
            print(f"   ⚠️ Cleanup warning: {e}")
    
    def get_video_url(self, video_path: str) -> str:
        """Get URL for accessing video"""
        # Convert absolute path to relative URL
        video_file = Path(video_path).name
        return f"/api/video/download/{video_file}"


# Streamlit Integration Helper
class StreamlitVideoHelper:
    """
    Helper class for Streamlit integration
    FIXED: Avoid nested expanders by using containers/columns instead
    """
    
    @staticmethod
    def display_video_result(result: Dict[str, Any], st_module):
        """
        Display video generation result in Streamlit
        FIXED: Uses st.container() instead of st.expander() to avoid nesting issues
        """
        
        if not result["success"]:
            st_module.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
            return
        
        st_module.success("✅ Video generated successfully!")
        
        # Display video
        col1, col2 = st_module.columns([2, 1])
        
        with col1:
            st_module.video(result["video_path"])
        
        with col2:
            st_module.markdown("### 📊 Video Info")
            st_module.metric("Duration", f"{result['duration']:.1f}s")
            st_module.metric("File Size", f"{result['file_size'] / (1024*1024):.2f} MB")
            st_module.metric("Language", result['language'].capitalize())
            
            # Download button
            with open(result["video_path"], "rb") as f:
                st_module.download_button(
                    label="⬇️ Download Video",
                    data=f,
                    file_name=Path(result["video_path"]).name,
                    mime="video/mp4"
                )
        
        # Show summary text in a container (NOT an expander to avoid nesting)
        st_module.markdown("---")
        st_module.markdown("**📝 Summary Text Used:**")
        st_module.text_area(
            "Summary",
            result["summary_text"],
            height=150,
            disabled=True,
            label_visibility="collapsed"
        )
    
    @staticmethod
    def display_video_standalone(result: Dict[str, Any], st_module):
        """
        Display video result when NOT inside an expander
        This version CAN use expanders safely
        """
        
        if not result["success"]:
            st_module.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
            return
        
        st_module.success("✅ Video generated successfully!")
        
        # Display video
        col1, col2 = st_module.columns([2, 1])
        
        with col1:
            st_module.video(result["video_path"])
        
        with col2:
            st_module.markdown("### 📊 Video Info")
            st_module.metric("Duration", f"{result['duration']:.1f}s")
            st_module.metric("File Size", f"{result['file_size'] / (1024*1024):.2f} MB")
            st_module.metric("Language", result['language'].capitalize())
            
            # Download button
            with open(result["video_path"], "rb") as f:
                st_module.download_button(
                    label="⬇️ Download Video",
                    data=f,
                    file_name=Path(result["video_path"]).name,
                    mime="video/mp4"
                )
        
        # Show summary text in expander (safe when not nested)
        with st_module.expander("📝 Summary Text Used"):
            st_module.text_area(
                "Summary",
                result["summary_text"],
                height=150,
                disabled=True,
                label_visibility="collapsed"
            )


# Example usage function
async def example_usage():
    """Example of how to use the video generator"""
    
    # Initialize generator
    video_gen = DocumentVideoGenerator()
    
    # Example summary (from your document processing)
    summary = """
    This document discusses the importance of artificial intelligence in modern business.
    Key findings include increased efficiency through automation, better decision-making with data analytics,
    and improved customer experiences through personalization. The report concludes that AI adoption
    is critical for competitive advantage in the digital age.
    """
    
    # Generate video
    result = await video_gen.generate_video_from_summary(
        summary_text=summary,
        language="english",
        target_duration=45,  # 45 second video
        include_subtitles=True,
        document_name="AI_Business_Report"
    )
    
    if result["success"]:
        print(f"✅ Video saved to: {result['video_path']}")
    else:
        print(f"❌ Failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(example_usage())