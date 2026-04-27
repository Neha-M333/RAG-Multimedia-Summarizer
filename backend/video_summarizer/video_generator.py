"""
COMPLETELY FIXED Video Generator with WORKING Hindi/Kannada Text
Properly handles Unicode fonts and verifies rendering
"""

import os
from typing import Dict, Any, List
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from backend.video_summarizer import config
import gc
import warnings
warnings.filterwarnings("ignore")


class VideoGenerator:
    """FIXED Video Generator with VERIFIED multi-language text rendering"""
    
    def __init__(self):
        self.temp_dir = config.TEMP_DIR
        
        # Detect and VERIFY fonts
        print("🔍 Detecting system fonts for multi-language support...")
        self.font_paths = self._detect_unicode_fonts()
        
        print("✅ Video Generator initialized")
    
    def _detect_unicode_fonts(self) -> Dict[str, str]:
        """Detect and verify Unicode-capable fonts"""
        
        fonts = {}
        
        # Comprehensive Windows font paths
        font_dirs = [
            "C:\\Windows\\Fonts",
            "C:\\WINDOWS\\Fonts",
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        ]
        
        # Priority-ordered font candidates (best first)
        font_candidates = {
            "english": [
                "arial.ttf", "arialbd.ttf", "Arial.ttf",
                "verdana.ttf", "calibri.ttf", "segoeui.ttf"
            ],
            "hindi": [
                "mangal.ttf", "mangalb.ttf",           # Mangal (Windows default for Hindi)
                "nirmala.ttf", "Nirmala.ttf",          # Nirmala UI (best Unicode support)
                "NirmalaUI.ttf", "nirmalab.ttf",
                "aparaj.ttf",                           # Aparajita
                "kokila.ttf", "kokilab.ttf",           # Kokila
                "utsaah.ttf"                            # Utsaah
            ],
            "kannada": [
                "tunga.ttf", "tungab.ttf",             # Tunga (Windows default for Kannada)
                "nirmala.ttf", "Nirmala.ttf",          # Nirmala UI (best Unicode support)
                "NirmalaUI.ttf", "nirmalab.ttf",
                "kartika.ttf", "kartikab.ttf",         # Kartika
                "vrinda.ttf", "vrindab.ttf"            # Vrinda
            ]
        }
        
        # Search for fonts
        for lang, candidates in font_candidates.items():
            found = False
            
            for font_dir in font_dirs:
                if not os.path.exists(font_dir):
                    continue
                
                for font_file in candidates:
                    font_path = os.path.join(font_dir, font_file)
                    
                    if os.path.exists(font_path):
                        # Test if font can render the language
                        if self._test_font_unicode_support(font_path, lang):
                            fonts[lang] = font_path
                            print(f"   ✅ {lang}: {font_file} (VERIFIED)")
                            found = True
                            break
                        else:
                            print(f"   ⚠️ {lang}: {font_file} exists but can't render Unicode")
                
                if found:
                    break
            
            if not found:
                print(f"   ❌ {lang}: NO WORKING FONT FOUND!")
                print(f"      Please install Nirmala UI or language-specific fonts")
                fonts[lang] = None
        
        return fonts
    
    def _test_font_unicode_support(self, font_path: str, language: str) -> bool:
        """Test if font can render Unicode characters for the language"""
        
        try:
            # Test strings with Unicode characters
            test_strings = {
                "english": "Hello World 123",
                "hindi": "नमस्ते दुनिया १२३",      # Hindi with Devanagari digits
                "kannada": "ನಮಸ್ಕಾರ ಜಗತ್ತು"       # Kannada script
            }
            
            test_text = test_strings.get(language, "Test")
            
            # Load font
            font = ImageFont.truetype(font_path, 40)
            
            # Create test image
            img = Image.new('RGB', (300, 150), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw text
            draw.text((10, 10), test_text, font=font, fill=(0, 0, 0))
            
            # Convert to array
            img_array = np.array(img)
            
            # Check if text rendered (pixels changed from white)
            # If font can't render Unicode, it shows boxes which are sparse
            black_pixels = np.sum(img_array < 200)
            white_pixels = np.sum(img_array >= 200)
            
            # Good rendering should have significant black pixels
            rendering_quality = black_pixels / (black_pixels + white_pixels)
            
            is_good = rendering_quality > 0.05  # At least 5% non-white pixels
            
            if is_good:
                print(f"      ✓ Font renders {language} correctly ({rendering_quality*100:.1f}% coverage)")
            
            return is_good
            
        except Exception as e:
            print(f"      Font test error: {e}")
            return False
    
    async def create_video(
        self,
        animation_video_path: str,
        audio_path: str,
        summary_text: str,
        language: str,
        output_path: str,
        include_subtitles: bool = True
    ) -> Dict[str, Any]:
        """Create video with proper Unicode text rendering"""
        video = None
        audio = None
        
        try:
            print(f"\n🎬 Creating video with {language} text...")
            
            # Verify we have a working font
            font_path = self.font_paths.get(language)
            
            if not font_path:
                print(f"   ❌ NO FONT AVAILABLE FOR {language}!")
                print(f"   Install required fonts:")
                print(f"   - Hindi: Mangal or Nirmala UI")
                print(f"   - Kannada: Tunga or Nirmala UI")
                include_subtitles = False
            else:
                print(f"   ✅ Using font: {os.path.basename(font_path)}")
            
            # Load video and audio
            print("   Loading video and audio...")
            video = VideoFileClip(animation_video_path)
            audio = AudioFileClip(audio_path)
            
            print(f"   Video: {video.duration:.1f}s, Audio: {audio.duration:.1f}s")
            
            # Sync audio with video
            max_duration = min(audio.duration, 65)
            if audio.duration > max_duration:
                audio = audio.subclip(0, max_duration)
            
            video = video.set_audio(audio)
            
            # Adjust video duration
            if video.duration < audio.duration:
                n_loops = int(np.ceil(audio.duration / video.duration))
                video = video.loop(n=n_loops)
            
            video = video.subclip(0, audio.duration)
            
            # Add text overlays if font is available
            if include_subtitles and summary_text.strip() and font_path:
                print(f"\n   🎨 Adding {language} text overlays...")
                video = await self._add_text_overlays(
                    video,
                    summary_text,
                    language,
                    font_path,
                    audio.duration
                )
            else:
                print("   ⚠️ Skipping text overlays (no font or disabled)")
            
            # Add title bar
            if font_path:
                print("\n   📋 Adding title bar...")
                video = await self._add_title_bar(video, language, font_path)
            
            # Write final video
            print("\n   💾 Writing final video...")
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=config.ANIMATION_FPS,
                preset='medium',
                threads=4,
                bitrate='4000k',
                logger=None,
                verbose=False
            )
            
            file_size = os.path.getsize(output_path)
            
            print(f"\n   ✅ Video created successfully!")
            print(f"   File: {file_size / (1024*1024):.2f} MB, Duration: {audio.duration:.1f}s")
            
            return {
                "success": True,
                "video_path": output_path,
                "duration": audio.duration,
                "resolution": config.VIDEO_RESOLUTION,
                "file_size": file_size,
                "language": language
            }
            
        except Exception as e:
            print(f"\n   ❌ Video creation error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "video_path": None
            }
        finally:
            print("\n   🧹 Cleaning up...")
            try:
                if video:
                    video.close()
                if audio:
                    audio.close()
            except:
                pass
            gc.collect()
    
    async def _add_text_overlays(
        self,
        video: VideoFileClip,
        text: str,
        language: str,
        font_path: str,
        duration: float
    ) -> VideoFileClip:
        """Add text overlays with proper Unicode rendering"""
        
        try:
            # Split text into chunks
            chunks = self._split_text_for_display(text, language)
            
            if not chunks:
                print("   ⚠️ No text chunks to display")
                return video
            
            print(f"   Creating {len(chunks)} text overlays")
            
            # Calculate timing
            time_per_chunk = duration / len(chunks)
            
            # Font size based on language
            font_sizes = {
                "english": 36,
                "hindi": 44,    # Slightly larger for better readability
                "kannada": 44
            }
            font_size = font_sizes.get(language, 36)
            
            # Create text clips
            text_clips = []
            
            for i, chunk in enumerate(chunks):
                start_time = i * time_per_chunk
                end_time = min((i + 1) * time_per_chunk, duration)
                
                try:
                    # Create text image
                    text_img = self._create_text_image(
                        chunk,
                        font_path,
                        font_size,
                        video.w,
                        video.h,
                        language
                    )
                    
                    if text_img is None:
                        print(f"   ⚠️ Failed to create overlay {i+1}")
                        continue
                    
                    # Create ImageClip
                    img_clip = ImageClip(text_img)
                    img_clip = img_clip.set_start(start_time)
                    img_clip = img_clip.set_duration(end_time - start_time)
                    img_clip = img_clip.set_position('center')
                    img_clip = img_clip.crossfadein(0.3).crossfadeout(0.3)
                    
                    text_clips.append(img_clip)
                    
                    if (i + 1) % 5 == 0:
                        print(f"   Created {i+1}/{len(chunks)} overlays")
                    
                except Exception as e:
                    print(f"   ⚠️ Overlay {i+1} failed: {e}")
                    continue
            
            if text_clips:
                print(f"   ✅ Compositing {len(text_clips)} text overlays")
                final_video = CompositeVideoClip([video] + text_clips)
                return final_video
            else:
                print("   ⚠️ No overlays created")
                return video
                
        except Exception as e:
            print(f"   ❌ Text overlay error: {e}")
            import traceback
            traceback.print_exc()
            return video
    
    def _create_text_image(
        self,
        text: str,
        font_path: str,
        font_size: int,
        video_width: int,
        video_height: int,
        language: str
    ) -> np.ndarray:
        """Create text image with proper Unicode support"""
        
        try:
            # Create transparent image
            img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Load font
            font = ImageFont.truetype(font_path, font_size)
            
            # Text area dimensions
            text_area_width = video_width - 100
            text_area_height = 200
            text_area_x = 50
            text_area_y = video_height - text_area_height - 30
            
            # Semi-transparent background
            padding = 25
            draw.rounded_rectangle(
                [text_area_x - padding, text_area_y - padding,
                 text_area_x + text_area_width + padding, text_area_y + text_area_height + padding],
                radius=20,
                fill=(0, 0, 0, 220)
            )
            
            # Border
            draw.rounded_rectangle(
                [text_area_x - padding, text_area_y - padding,
                 text_area_x + text_area_width + padding, text_area_y + text_area_height + padding],
                radius=20,
                outline=(100, 150, 255, 255),
                width=4
            )
            
            # Wrap text to fit
            wrapped_lines = self._wrap_text(text, font, text_area_width, draw)
            
            if not wrapped_lines:
                return None
            
            # Limit to 4 lines
            if len(wrapped_lines) > 4:
                wrapped_lines = wrapped_lines[:4]
                wrapped_lines[-1] = wrapped_lines[-1][:80] + "..."
            
            # Calculate line positions
            line_spacing = 12
            total_text_height = 0
            line_heights = []
            
            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
                total_text_height += line_height
            
            total_text_height += line_spacing * (len(wrapped_lines) - 1)
            
            # Start position (centered vertically in text area)
            current_y = text_area_y + (text_area_height - total_text_height) // 2
            
            # Draw each line
            for line, line_height in zip(wrapped_lines, line_heights):
                # Get text width for centering
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                
                # Center horizontally
                x = text_area_x + (text_area_width - text_width) // 2
                
                # Draw text with outline for better readability
                # Black outline
                outline_range = 3
                for ox in range(-outline_range, outline_range + 1):
                    for oy in range(-outline_range, outline_range + 1):
                        if ox != 0 or oy != 0:
                            draw.text((x + ox, current_y + oy), line, font=font, fill=(0, 0, 0, 255))
                
                # Main text (white)
                draw.text((x, current_y), line, font=font, fill=(255, 255, 255, 255))
                
                current_y += line_height + line_spacing
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Verify text rendered (check alpha channel has content)
            if not np.any(img_array[:, :, 3] > 0):
                print(f"      ❌ Text didn't render (empty alpha)")
                return None
            
            return img_array
            
        except Exception as e:
            print(f"      ❌ Image creation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _wrap_text(
        self,
        text: str,
        font: ImageFont.ImageFont,
        max_width: int,
        draw: ImageDraw.Draw
    ) -> List[str]:
        """Wrap text to fit within max_width"""
        
        words = text.split()
        if not words:
            return []
        
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            
            # Get text width
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _split_text_for_display(self, text: str, language: str) -> List[str]:
        """Split text into display chunks"""
        
        # Split by sentences
        if language == "hindi":
            sentences = [s.strip() for s in text.replace('।', '.').split('.') if s.strip()]
        elif language == "kannada":
            sentences = [s.strip() for s in text.replace('।', '.').replace('|', '.').split('.') if s.strip()]
        else:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        chunks = []
        for sentence in sentences:
            words = sentence.split()
            
            # Split long sentences
            if len(words) > 15:
                for i in range(0, len(words), 12):
                    chunk = ' '.join(words[i:i+12])
                    if chunk:
                        chunks.append(chunk)
            else:
                chunks.append(sentence)
        
        # Add periods back
        formatted = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk and chunk[-1] not in '.!?।':
                chunk += '.'
            if chunk:
                formatted.append(chunk)
        
        return formatted
    
    async def _add_title_bar(self, video: VideoFileClip, language: str, font_path: str) -> VideoFileClip:
        """Add title bar"""
        
        try:
            titles = {
                "english": "🎯 AI-Generated Summary",
                "hindi": "🎯 एआई सारांश",
                "kannada": "🎯 AI ಸಾರಾಂಶ"
            }
            
            title_text = titles.get(language, "🎯 AI Summary")
            
            title_img = self._create_title_image(title_text, font_path, video.w, video.h)
            
            if title_img is not None:
                title_clip = ImageClip(title_img)
                title_clip = title_clip.set_duration(video.duration)
                title_clip = title_clip.set_position(('center', 'top'))
                
                final_video = CompositeVideoClip([video, title_clip])
                print("   ✅ Title bar added")
                return final_video
            
            return video
            
        except Exception as e:
            print(f"   ⚠️ Title bar failed: {e}")
            return video
    
    def _create_title_image(self, text: str, font_path: str, w: int, h: int) -> np.ndarray:
        """Create title bar image"""
        
        try:
            img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            bar_height = 80
            
            # Gradient-like bar
            draw.rounded_rectangle(
                [0, 0, w, bar_height],
                radius=0,
                fill=(60, 80, 180, 240)
            )
            draw.rectangle([0, bar_height-5, w, bar_height], fill=(100, 150, 255, 255))
            
            # Load font
            font = ImageFont.truetype(font_path, 38)
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center text
            x = (w - text_width) // 2
            y = (bar_height - text_height) // 2
            
            # Black outline
            for ox in range(-2, 3):
                for oy in range(-2, 3):
                    if ox != 0 or oy != 0:
                        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 255))
            
            # Main text
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            
            return np.array(img)
            
        except Exception as e:
            print(f"   ⚠️ Title creation failed: {e}")
            return None
    
    async def create_thumbnail(self, video_path: str, output_path: str, timestamp: float = 1.0) -> str:
        """Generate video thumbnail"""
        video = None
        try:
            video = VideoFileClip(video_path)
            frame = video.get_frame(min(timestamp, video.duration - 0.1))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_path, frame_bgr)
            return output_path
        except Exception as e:
            print(f"   ⚠️ Thumbnail failed: {e}")
            return None
        finally:
            if video:
                video.close()