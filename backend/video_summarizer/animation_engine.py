# """
# 🎭 PROFESSIONAL Animation Engine with FIXED Text Scrolling
# Features:
# - Professional business character design
# - Character WRITES the summary with pen/pointer
# - FIXED: Real-time text scrolling synchronized with audio
# - Multi-language support (English, Hindi, Kannada)
# - Smooth animations and natural expressions
# """

# import os
# import json
# import numpy as np
# from typing import Dict, Any, List
# import librosa
# import cv2
# from PIL import Image, ImageDraw, ImageFont
# from backend.video_summarizer import config


# class Audio2FaceAnimator:
#     """
#     Professional animated character that speaks AND writes summaries
#     """
    
#     def __init__(self):
#         print("🎭 Initializing Professional Character Animator...")
#         self.sample_rate = 22050
#         self.frame_rate = config.ANIMATION_FPS
        
#         # Professional character colors
#         self.character_colors = {
#             "suit": (40, 60, 100),
#             "shirt": (255, 255, 255),
#             "skin": (255, 220, 180),
#             "tie": (180, 40, 40),
#             "eyes": (50, 50, 50),
#             "eye_white": (255, 255, 255),
#             "mouth": (255, 150, 150),
#             "outline": (30, 30, 30),
#             "accent": (220, 180, 50)
#         }
        
#         print("✅ Professional Character Animator initialized")
    
#     async def generate_lipsync_animation(
#         self,
#         audio_path: str,
#         language: str,
#         output_path: str
#     ) -> Dict[str, Any]:
#         """Generate animation with lip-sync"""
#         try:
#             print(f"   🎯 Generating professional character animation for {language}...")
            
#             # Load and analyze audio
#             audio, sr = librosa.load(audio_path, sr=self.sample_rate)
#             duration = len(audio) / sr
            
#             print(f"   Audio duration: {duration:.2f}s")
            
#             # Analyze audio for expressions and mouth movements
#             frames = await self._analyze_audio_for_animation(audio, sr, duration)
            
#             print(f"   Generated {len(frames)} animation frames")
            
#             # Save animation data
#             animation_data = {
#                 "duration": duration,
#                 "frame_rate": self.frame_rate,
#                 "frames": frames,
#                 "language": language
#             }
            
#             with open(output_path, 'w') as f:
#                 json.dump(animation_data, f)
            
#             return {
#                 "success": True,
#                 "animation_path": output_path,
#                 "frames": frames,
#                 "duration": duration,
#                 "frame_count": len(frames)
#             }
            
#         except Exception as e:
#             print(f"   ❌ Animation generation failed: {e}")
#             import traceback
#             traceback.print_exc()
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "frames": []
#             }
    
#     async def _analyze_audio_for_animation(
#         self,
#         audio: np.ndarray,
#         sr: int,
#         duration: float  # ADDED: Pass duration explicitly
#     ) -> List[Dict]:
#         """Analyze audio to create realistic mouth shapes and expressions"""
        
#         num_frames = int(duration * self.frame_rate)
#         samples_per_frame = len(audio) // num_frames if num_frames > 0 else len(audio)
        
#         frames = []
        
#         # Get amplitude envelope for mouth movements
#         hop_length = samples_per_frame
#         rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
#         rms = rms / (np.max(rms) + 1e-8)
        
#         # Get spectral features
#         spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=hop_length)[0]
#         spectral_centroid = spectral_centroid / (np.max(spectral_centroid) + 1e-8)
        
#         for i in range(num_frames):
#             # Get audio features for this frame
#             if i < len(rms):
#                 mouth_open = float(rms[i])
#                 energy = float(spectral_centroid[i]) if i < len(spectral_centroid) else 0.0
#             else:
#                 mouth_open = 0.0
#                 energy = 0.0
            
#             # Determine expression based on audio
#             if mouth_open > 0.6:
#                 expression = "speaking_excited"
#                 blink = False
#             elif mouth_open > 0.3:
#                 expression = "speaking_normal"
#                 blink = (i % 60) < 3
#             elif mouth_open > 0.1:
#                 expression = "speaking_soft"
#                 blink = (i % 90) < 3
#             else:
#                 expression = "neutral"
#                 blink = (i % 120) < 3
            
#             # Natural head movements
#             head_bob = np.sin(i * 0.08) * 3
            
#             # Arm movement for pointing/writing
#             arm_movement = np.sin(i * 0.15) * 15
            
#             # FIXED: Calculate timestamp and store total_duration in each frame
#             timestamp = i / self.frame_rate
            
#             frame = {
#                 "frame_number": i,
#                 "timestamp": timestamp,
#                 "total_duration": duration,  # FIXED: Store in each frame
#                 "total_frames": num_frames,  # ADDED: For progress calculation
#                 "mouth_open": mouth_open,
#                 "expression": expression,
#                 "blink": blink,
#                 "head_bob": head_bob,
#                 "energy": energy,
#                 "arm_movement": arm_movement,
#                 "progress": timestamp / duration if duration > 0 else 0  # ADDED: Pre-calculate progress
#             }
            
#             frames.append(frame)
        
#         return frames
    
#     async def apply_animation_to_character(
#         self,
#         animation_path: str,
#         character_model_path: str,
#         output_video_path: str,
#         summary_text: str = "",
#         language: str = "english"
#     ) -> str:
#         """Apply animation to professional character and render video"""
#         try:
#             print("   🎨 Rendering professional character with writing animation...")
            
#             # Load animation data
#             with open(animation_path, 'r') as f:
#                 animation_data = json.load(f)
            
#             frames = animation_data['frames']
#             duration = animation_data['duration']
            
#             # Create video writer
#             fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#             video_writer = cv2.VideoWriter(
#                 output_video_path,
#                 fourcc,
#                 self.frame_rate,
#                 config.VIDEO_RESOLUTION
#             )
            
#             print(f"   Rendering {len(frames)} frames with scrolling text...")
#             print(f"   Total duration: {duration:.2f}s")
            
#             for i, frame_data in enumerate(frames):
#                 # FIXED: Ensure total_duration is set
#                 if 'total_duration' not in frame_data or frame_data['total_duration'] is None:
#                     frame_data['total_duration'] = duration
                
#                 # Render frame with character and scrolling text
#                 frame_img = self._render_professional_character_frame(
#                     frame_data,
#                     summary_text,
#                     language
#                 )
                
#                 # Convert PIL to OpenCV
#                 frame_cv = cv2.cvtColor(np.array(frame_img), cv2.COLOR_RGB2BGR)
#                 frame_cv = cv2.resize(frame_cv, config.VIDEO_RESOLUTION)
                
#                 video_writer.write(frame_cv)
                
#                 if (i + 1) % 30 == 0:
#                     progress_pct = (i + 1) / len(frames) * 100
#                     print(f"   Progress: {i + 1}/{len(frames)} frames ({progress_pct:.1f}%)")
            
#             video_writer.release()
            
#             print(f"   ✅ Professional character video rendered!")
#             return output_video_path
            
#         except Exception as e:
#             print(f"   ⚠️ Character rendering failed: {e}")
#             import traceback
#             traceback.print_exc()
#             raise
    
#     def _render_professional_character_frame(
#         self,
#         frame_data: Dict,
#         text_to_show: str,
#         language: str
#     ) -> Image.Image:
#         """Render a single frame with professional character and text"""
        
#         # Create canvas with professional gradient background
#         width, height = config.VIDEO_RESOLUTION
#         img = Image.new('RGB', (width, height), color=(245, 250, 255))
#         draw = ImageDraw.Draw(img)
        
#         # Professional gradient background
#         self._draw_professional_gradient(img, draw)
        
#         # Calculate positions
#         center_x = width // 5
#         center_y = height // 2
        
#         # Apply head bob
#         head_bob = frame_data.get('head_bob', 0)
#         center_y += int(head_bob)
        
#         # Character dimensions
#         head_radius = 60
#         body_width = 80
#         body_height = 110
        
#         # Draw body (suit)
#         body_top = center_y + head_radius - 15
#         self._draw_rounded_rectangle(
#             draw,
#             [center_x - body_width//2, body_top,
#              center_x + body_width//2, body_top + body_height],
#             radius=25,
#             fill=self.character_colors["suit"],
#             outline=self.character_colors["outline"],
#             width=3
#         )
        
#         # Draw white shirt collar
#         collar_points = [
#             (center_x - 25, body_top),
#             (center_x - 15, body_top + 30),
#             (center_x, body_top + 35),
#             (center_x + 15, body_top + 30),
#             (center_x + 25, body_top)
#         ]
#         draw.polygon(collar_points, fill=self.character_colors["shirt"])
        
#         # Draw tie
#         tie_points = [
#             (center_x - 8, body_top + 35),
#             (center_x + 8, body_top + 35),
#             (center_x + 5, body_top + 70),
#             (center_x, body_top + 75),
#             (center_x - 5, body_top + 70)
#         ]
#         draw.polygon(tie_points, fill=self.character_colors["tie"], 
#                     outline=self.character_colors["outline"], width=2)
        
#         # Draw head
#         draw.ellipse(
#             [center_x - head_radius, center_y - head_radius,
#              center_x + head_radius, center_y + head_radius],
#             fill=self.character_colors["skin"],
#             outline=self.character_colors["outline"],
#             width=3
#         )
        
#         # Draw hairstyle
#         hair_points = [
#             (center_x - head_radius, center_y - head_radius + 10),
#             (center_x - head_radius + 20, center_y - head_radius - 5),
#             (center_x, center_y - head_radius - 8),
#             (center_x + head_radius - 20, center_y - head_radius - 5),
#             (center_x + head_radius, center_y - head_radius + 10)
#         ]
#         draw.polygon(hair_points, fill=(50, 40, 30), 
#                     outline=self.character_colors["outline"], width=2)
        
#         # Draw eyes
#         blink = frame_data.get('blink', False)
#         eye_y = center_y - 15
#         eye_spacing = 25
#         eye_size = 14
        
#         if not blink:
#             # Eye whites
#             draw.ellipse(
#                 [center_x - eye_spacing - eye_size, eye_y - eye_size,
#                  center_x - eye_spacing + eye_size, eye_y + eye_size],
#                 fill=self.character_colors["eye_white"],
#                 outline=self.character_colors["outline"],
#                 width=2
#             )
#             draw.ellipse(
#                 [center_x + eye_spacing - eye_size, eye_y - eye_size,
#                  center_x + eye_spacing + eye_size, eye_y + eye_size],
#                 fill=self.character_colors["eye_white"],
#                 outline=self.character_colors["outline"],
#                 width=2
#             )
            
#             # Pupils
#             pupil_size = 6
#             pupil_offset = 5
#             draw.ellipse(
#                 [center_x - eye_spacing + pupil_offset - pupil_size, eye_y - pupil_size,
#                  center_x - eye_spacing + pupil_offset + pupil_size, eye_y + pupil_size],
#                 fill=self.character_colors["eyes"]
#             )
#             draw.ellipse(
#                 [center_x + eye_spacing + pupil_offset - pupil_size, eye_y - pupil_size,
#                  center_x + eye_spacing + pupil_offset + pupil_size, eye_y + pupil_size],
#                 fill=self.character_colors["eyes"]
#             )
            
#             # Highlights
#             draw.ellipse(
#                 [center_x - eye_spacing + pupil_offset - 3, eye_y - 5,
#                  center_x - eye_spacing + pupil_offset, eye_y - 2],
#                 fill=(255, 255, 255)
#             )
#             draw.ellipse(
#                 [center_x + eye_spacing + pupil_offset - 3, eye_y - 5,
#                  center_x + eye_spacing + pupil_offset, eye_y - 2],
#                 fill=(255, 255, 255)
#             )
#         else:
#             # Blinking
#             draw.arc(
#                 [center_x - eye_spacing - eye_size, eye_y - 4,
#                  center_x - eye_spacing + eye_size, eye_y + 4],
#                 start=0, end=180,
#                 fill=self.character_colors["outline"],
#                 width=3
#             )
#             draw.arc(
#                 [center_x + eye_spacing - eye_size, eye_y - 4,
#                  center_x + eye_spacing + eye_size, eye_y + 4],
#                 start=0, end=180,
#                 fill=self.character_colors["outline"],
#                 width=3
#             )
        
#         # Draw nose
#         nose_points = [
#             (center_x - 4, center_y - 5),
#             (center_x + 4, center_y - 5),
#             (center_x, center_y + 5)
#         ]
#         draw.polygon(nose_points, fill=self.character_colors["skin"], 
#                     outline=self.character_colors["outline"], width=2)
        
#         # Draw mouth with lip-sync
#         mouth_y = center_y + 20
#         mouth_open = frame_data.get('mouth_open', 0.0)
#         self._draw_professional_mouth(draw, center_x, mouth_y, mouth_open)
        
#         # Draw arms
#         arm_movement = frame_data.get('arm_movement', 0)
#         self._draw_professional_arms(draw, center_x, body_top, arm_movement, width)
        
#         # FIXED: Draw text area with proper scrolling
#         if text_to_show:
#             self._draw_professional_text_area(img, draw, text_to_show, language, 
#                                              width, height, frame_data)
        
#         return img
    
#     def _draw_professional_mouth(self, draw: ImageDraw.Draw, center_x: int, 
#                                   mouth_y: int, mouth_open: float):
#         """Draw professional mouth expression"""
#         mouth_width = 35
        
#         if mouth_open > 0.15:
#             mouth_height = int(5 + mouth_open * 25)
#             draw.ellipse(
#                 [center_x - mouth_width//2, mouth_y - mouth_height//2,
#                  center_x + mouth_width//2, mouth_y + mouth_height//2],
#                 fill=(255, 120, 120),
#                 outline=self.character_colors["outline"],
#                 width=2
#             )
#         else:
#             draw.arc(
#                 [center_x - mouth_width//2, mouth_y - 12,
#                  center_x + mouth_width//2, mouth_y + 12],
#                 start=0, end=180,
#                 fill=self.character_colors["outline"],
#                 width=3
#             )
    
#     def _draw_professional_arms(self, draw: ImageDraw.Draw, center_x: int, 
#                                  body_top: int, arm_movement: float, screen_width: int):
#         """Draw professional arms with pointing gesture"""
#         arm_width = 20
#         arm_length = 45
        
#         # Left arm
#         left_arm_x = center_x - 50
#         left_arm_y = body_top + 25
        
#         draw.ellipse(
#             [left_arm_x - arm_width, left_arm_y,
#              left_arm_x + arm_width, left_arm_y + arm_length],
#             fill=self.character_colors["suit"],
#             outline=self.character_colors["outline"],
#             width=2
#         )
        
#         draw.ellipse(
#             [left_arm_x - 15, left_arm_y + arm_length - 5,
#              left_arm_x + 15, left_arm_y + arm_length + 25],
#             fill=self.character_colors["skin"],
#             outline=self.character_colors["outline"],
#             width=2
#         )
        
#         # Right arm (pointing)
#         right_arm_x = center_x + 50
#         right_arm_y = body_top + 25
        
#         pointer_target_x = screen_width // 2 + int(arm_movement)
#         pointer_target_y = body_top + 20
        
#         draw.line(
#             [(right_arm_x, right_arm_y + 20),
#              (pointer_target_x - 30, pointer_target_y)],
#             fill=self.character_colors["suit"],
#             width=25
#         )
        
#         draw.ellipse(
#             [pointer_target_x - 40, pointer_target_y - 15,
#              pointer_target_x - 10, pointer_target_y + 15],
#             fill=self.character_colors["skin"],
#             outline=self.character_colors["outline"],
#             width=2
#         )
        
#         draw.ellipse(
#             [pointer_target_x - 15, pointer_target_y - 5,
#              pointer_target_x, pointer_target_y + 5],
#             fill=self.character_colors["skin"],
#             outline=self.character_colors["outline"],
#             width=2
#         )
    
#     def _draw_professional_text_area(
#         self,
#         img: Image.Image,
#         draw: ImageDraw.Draw,
#         text: str,
#         language: str,
#         width: int,
#         height: int,
#         frame_data: Dict
#     ):
#         """Draw scrolling text area synchronized with audio - FIXED VERSION"""
        
#         # Text area dimensions
#         text_area_x = width // 2 + 10
#         text_area_y = 60
#         text_area_width = width - text_area_x - 30
#         text_area_height = height - 120
        
#         # Draw shadow
#         shadow_offset = 5
#         self._draw_rounded_rectangle(
#             draw,
#             [text_area_x + shadow_offset, text_area_y + shadow_offset,
#              text_area_x + text_area_width + shadow_offset, 
#              text_area_y + text_area_height + shadow_offset],
#             radius=15,
#             fill=(200, 200, 200),
#             outline=None,
#             width=0
#         )
        
#         # Draw main text area
#         self._draw_rounded_rectangle(
#             draw,
#             [text_area_x, text_area_y,
#              text_area_x + text_area_width, text_area_y + text_area_height],
#             radius=15,
#             fill=(255, 255, 255),
#             outline=(100, 150, 200),
#             width=4
#         )
        
#         # Get font
#         try:
#             font_path, font_size = self._get_multilingual_font(language)
#             if font_path:
#                 try:
#                     font = ImageFont.truetype(font_path, font_size)
#                 except:
#                     font = ImageFont.load_default()
#                     font_size = 20
#             else:
#                 font = ImageFont.load_default()
#                 font_size = 20
            
#             # Wrap ALL text
#             wrapped_lines = self._wrap_text_multilingual(
#                 text,
#                 text_area_width - 40,
#                 font,
#                 language
#             )
            
#             if not wrapped_lines:
#                 return
            
#             # FIXED: Get progress from frame_data
#             # Use pre-calculated progress or calculate from timestamp/duration
#             progress = frame_data.get('progress', 0)
            
#             if progress == 0:
#                 current_time = frame_data.get('timestamp', 0)
#                 total_duration = frame_data.get('total_duration', 1)
#                 if total_duration > 0:
#                     progress = current_time / total_duration
            
#             # Clamp progress to 0-1
#             progress = max(0, min(1, progress))
            
#             line_height = font_size + 8
#             visible_lines = (text_area_height - 40) // line_height
#             total_lines = len(wrapped_lines)
            
#             # Calculate scroll offset based on progress
#             if total_lines <= visible_lines:
#                 # All text fits - no scrolling needed
#                 scroll_offset = 0
#                 start_line = 0
#             else:
#                 # FIXED: Smooth scrolling based on audio progress
#                 # Calculate total scrollable distance in pixels
#                 max_scroll_lines = total_lines - visible_lines
#                 max_scroll_pixels = max_scroll_lines * line_height
                
#                 # Current scroll position in pixels
#                 scroll_offset = int(progress * max_scroll_pixels)
                
#                 # Calculate which line to start from
#                 start_line = scroll_offset // line_height
                
#                 # Partial line offset for smooth scrolling
#                 partial_offset = scroll_offset % line_height
            
#             # Starting Y position with smooth scrolling offset
#             text_x = text_area_x + 20
#             if total_lines <= visible_lines:
#                 text_y = text_area_y + 20
#             else:
#                 text_y = text_area_y + 20 - (scroll_offset % line_height)
            
#             # Determine currently spoken line based on progress
#             mouth_open = frame_data.get('mouth_open', 0)
#             current_line_idx = int(progress * total_lines)
            
#             # Draw visible lines
#             end_line = min(start_line + visible_lines + 2, total_lines)
            
#             for idx in range(start_line, end_line):
#                 if idx >= total_lines:
#                     break
                    
#                 line = wrapped_lines[idx]
                
#                 # Check if line is within visible area
#                 if text_y < text_area_y + 10:
#                     text_y += line_height
#                     continue
                    
#                 if text_y > text_area_y + text_area_height - 20:
#                     break
                
#                 # Highlight currently spoken line
#                 is_current_line = (idx == current_line_idx and mouth_open > 0.2)
                
#                 if is_current_line:
#                     # Draw highlight behind text
#                     try:
#                         bbox = font.getbbox(line)
#                         highlight_width = bbox[2] - bbox[0]
#                         draw.rectangle(
#                             [text_x - 5, text_y - 2,
#                              text_x + highlight_width + 5, text_y + font_size + 2],
#                             fill=(255, 255, 200)  # Light yellow highlight
#                         )
#                     except:
#                         pass
                    
#                     # Draw text in darker color for emphasis
#                     draw.text(
#                         (text_x, text_y),
#                         line,
#                         fill=(0, 0, 100),
#                         font=font
#                     )
#                 else:
#                     # Regular text color
#                     draw.text(
#                         (text_x, text_y),
#                         line,
#                         fill=(30, 30, 30),
#                         font=font
#                     )
                
#                 text_y += line_height
            
#             # Draw scroll indicator if needed
#             if total_lines > visible_lines:
#                 self._draw_scroll_indicator(
#                     draw,
#                     text_area_x + text_area_width - 15,
#                     text_area_y + 20,
#                     text_area_height - 40,
#                     progress
#                 )
            
#         except Exception as e:
#             print(f"   ⚠️ Text rendering error: {e}")
#             import traceback
#             traceback.print_exc()
#             # Fallback: just draw some text
#             draw.text(
#                 (text_area_x + 20, text_area_y + 20),
#                 text[:100] + "...",
#                 fill=(30, 30, 30)
#             )

#     def _draw_scroll_indicator(self, draw: ImageDraw.Draw, x: int, y: int, 
#                                 height: int, progress: float):
#         """Draw a scroll progress indicator"""
#         # Scroll track
#         draw.rectangle(
#             [x, y, x + 8, y + height],
#             fill=(220, 220, 220),
#             outline=(150, 150, 150),
#             width=1
#         )
        
#         # Scroll thumb
#         thumb_height = max(20, height // 10)
#         thumb_y = y + int((height - thumb_height) * progress)
        
#         draw.rectangle(
#             [x + 1, thumb_y, x + 7, thumb_y + thumb_height],
#             fill=(100, 150, 200),
#             outline=(70, 120, 170),
#             width=1
#         )
    
#     def _get_multilingual_font(self, language: str) -> tuple:
#         """Get appropriate font path and size for each language"""
#         font_configs = {
#             "english": ("arial.ttf", 22),
#             "hindi": ("mangal.ttf", 24),
#             "kannada": ("tunga.ttf", 24)
#         }
        
#         font_name, size = font_configs.get(language, ("arial.ttf", 22))
        
#         font_locations = [
#             f"C:\\Windows\\Fonts\\{font_name}",
#             f"/usr/share/fonts/truetype/{font_name}",
#             f"/System/Library/Fonts/{font_name}",
#             font_name
#         ]
        
#         for font_path in font_locations:
#             if os.path.exists(font_path):
#                 return (font_path, size)
        
#         # Try Nirmala UI as fallback for Hindi/Kannada
#         if language in ["hindi", "kannada"]:
#             nirmala_paths = [
#                 "C:\\Windows\\Fonts\\Nirmala.ttf",
#                 "C:\\Windows\\Fonts\\nirmala.ttf",
#                 "C:\\Windows\\Fonts\\NirmalaUI.ttf"
#             ]
#             for nirmala_path in nirmala_paths:
#                 if os.path.exists(nirmala_path):
#                     return (nirmala_path, size)
        
#         return (None, size)
    
#     def _wrap_text_multilingual(self, text: str, max_width: int, 
#                                  font: ImageFont.ImageFont, language: str) -> List[str]:
#         """Wrap text properly for different languages"""
#         lines = []
        
#         # Split into sentences
#         if language == "hindi":
#             sentences = text.replace('।', '.').split('.')
#         elif language == "kannada":
#             sentences = text.replace('।', '.').replace('|', '.').split('.')
#         else:
#             sentences = text.split('.')
        
#         for sentence in sentences:
#             sentence = sentence.strip()
#             if not sentence:
#                 continue
            
#             sentence += '.'
#             words = sentence.split()
#             current_line = []
            
#             for word in words:
#                 test_line = ' '.join(current_line + [word])
                
#                 try:
#                     bbox = font.getbbox(test_line)
#                     text_width = bbox[2] - bbox[0]
                    
#                     if text_width <= max_width:
#                         current_line.append(word)
#                     else:
#                         if current_line:
#                             lines.append(' '.join(current_line))
#                         current_line = [word]
#                 except:
#                     if len(test_line) <= 40:
#                         current_line.append(word)
#                     else:
#                         if current_line:
#                             lines.append(' '.join(current_line))
#                         current_line = [word]
            
#             if current_line:
#                 lines.append(' '.join(current_line))
        
#         return lines
    
#     def _draw_rounded_rectangle(self, draw: ImageDraw.Draw, coords: list, 
#                                  radius: int, fill: tuple, outline: tuple, width: int):
#         """Draw rounded rectangle"""
#         x1, y1, x2, y2 = coords
        
#         draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
#         draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        
#         draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
#         draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
#         draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
#         draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)
        
#         if outline and width > 0:
#             draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=width)
#             draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=width)
#             draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=width)
#             draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=width)
#             draw.line([(x1 + radius, y1), (x2 - radius, y1)], fill=outline, width=width)
#             draw.line([(x1 + radius, y2), (x2 - radius, y2)], fill=outline, width=width)
#             draw.line([(x1, y1 + radius), (x1, y2 - radius)], fill=outline, width=width)
#             draw.line([(x2, y1 + radius), (x2, y2 - radius)], fill=outline, width=width)
    
#     def _draw_professional_gradient(self, img: Image.Image, draw: ImageDraw.Draw):
#         """Draw professional gradient background"""
#         width, height = img.size
        
#         for y in range(height):
#             ratio = y / height
#             r = int(230 + ratio * 15)
#             g = int(240 + ratio * 10)
#             b = int(250 + ratio * 5)
#             draw.line([(0, y), (width, y)], fill=(r, g, b))

"""
🎭 PROFESSIONAL Animation Engine - COMPLETE FIXED VERSION
Features:
- Professional business character design
- FIXED: Text scrolls synchronized with audio
- Multi-language support (English, Hindi, Kannada)
- Smooth animations and natural expressions
"""

import os
import json
import numpy as np
from typing import Dict, Any, List
import librosa
import cv2
from PIL import Image, ImageDraw, ImageFont
from backend.video_summarizer import config


class Audio2FaceAnimator:
    def __init__(self):
        print("🎭 Initializing Professional Character Animator...")
        self.sample_rate = 22050
        self.frame_rate = config.ANIMATION_FPS
        
        self.character_colors = {
            "suit": (40, 60, 100),
            "shirt": (255, 255, 255),
            "skin": (255, 220, 180),
            "tie": (180, 40, 40),
            "eyes": (50, 50, 50),
            "eye_white": (255, 255, 255),
            "mouth": (255, 150, 150),
            "outline": (30, 30, 30),
            "accent": (220, 180, 50)
        }
        print("✅ Professional Character Animator initialized")
    
    async def generate_lipsync_animation(
        self, audio_path: str, language: str, output_path: str
    ) -> Dict[str, Any]:
        try:
            print(f"   🎯 Generating animation for {language}...")
            
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            duration = len(audio) / sr
            
            print(f"   Audio duration: {duration:.2f}s")
            
            frames = await self._analyze_audio_for_animation(audio, sr, duration)
            
            print(f"   Generated {len(frames)} frames")
            
            animation_data = {
                "duration": duration,
                "frame_rate": self.frame_rate,
                "frames": frames,
                "language": language
            }
            
            with open(output_path, 'w') as f:
                json.dump(animation_data, f)
            
            return {
                "success": True,
                "animation_path": output_path,
                "frames": frames,
                "duration": duration,
                "frame_count": len(frames)
            }
        except Exception as e:
            print(f"   ❌ Animation failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), "frames": []}
    
    async def _analyze_audio_for_animation(
        self, audio: np.ndarray, sr: int, duration: float
    ) -> List[Dict]:
        num_frames = int(duration * self.frame_rate)
        samples_per_frame = len(audio) // num_frames if num_frames > 0 else len(audio)
        
        frames = []
        
        hop_length = samples_per_frame
        rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
        rms = rms / (np.max(rms) + 1e-8)
        
        spectral = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=hop_length)[0]
        spectral = spectral / (np.max(spectral) + 1e-8)
        
        for i in range(num_frames):
            mouth_open = float(rms[i]) if i < len(rms) else 0.0
            energy = float(spectral[i]) if i < len(spectral) else 0.0
            
            if mouth_open > 0.6:
                expression, blink = "speaking_excited", False
            elif mouth_open > 0.3:
                expression, blink = "speaking_normal", (i % 60) < 3
            elif mouth_open > 0.1:
                expression, blink = "speaking_soft", (i % 90) < 3
            else:
                expression, blink = "neutral", (i % 120) < 3
            
            timestamp = i / self.frame_rate
            progress = timestamp / duration if duration > 0 else 0
            
            frames.append({
                "frame_number": i,
                "timestamp": timestamp,
                "total_duration": duration,
                "total_frames": num_frames,
                "progress": progress,
                "mouth_open": mouth_open,
                "expression": expression,
                "blink": blink,
                "head_bob": np.sin(i * 0.08) * 3,
                "energy": energy,
                "arm_movement": np.sin(i * 0.15) * 15
            })
        
        return frames
    
    async def apply_animation_to_character(
        self, animation_path: str, character_model_path: str,
        output_video_path: str, summary_text: str = "", language: str = "english"
    ) -> str:
        try:
            print("   🎨 Rendering character with scrolling text...")
            
            with open(animation_path, 'r') as f:
                animation_data = json.load(f)
            
            frames = animation_data['frames']
            duration = animation_data['duration']
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                output_video_path, fourcc, self.frame_rate, config.VIDEO_RESOLUTION
            )
            
            print(f"   Rendering {len(frames)} frames...")
            
            for i, frame_data in enumerate(frames):
                frame_data['total_duration'] = duration
                
                frame_img = self._render_frame(frame_data, summary_text, language)
                frame_cv = cv2.cvtColor(np.array(frame_img), cv2.COLOR_RGB2BGR)
                frame_cv = cv2.resize(frame_cv, config.VIDEO_RESOLUTION)
                video_writer.write(frame_cv)
                
                if (i + 1) % 30 == 0:
                    print(f"   Progress: {(i+1)/len(frames)*100:.1f}%")
            
            video_writer.release()
            print(f"   ✅ Video rendered!")
            return output_video_path
            
        except Exception as e:
            print(f"   ⚠️ Rendering failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _render_frame(self, frame_data: Dict, text: str, language: str) -> Image.Image:
        width, height = config.VIDEO_RESOLUTION
        img = Image.new('RGB', (width, height), (245, 250, 255))
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(height):
            r = int(230 + (y/height) * 15)
            g = int(240 + (y/height) * 10)
            b = int(250 + (y/height) * 5)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        center_x = width // 5
        center_y = height // 2 + int(frame_data.get('head_bob', 0))
        
        # Draw character
        self._draw_character(draw, center_x, center_y, frame_data, width)
        
        # Draw scrolling text
        if text:
            self._draw_scrolling_text(draw, text, language, width, height, frame_data)
        
        return img
    
    def _draw_character(self, draw, cx, cy, frame_data, width):
        colors = self.character_colors
        head_r, body_w, body_h = 60, 80, 110
        body_top = cy + head_r - 15
        
        # Body
        self._rounded_rect(draw, [cx-body_w//2, body_top, cx+body_w//2, body_top+body_h],
                          15, colors["suit"], colors["outline"], 3)
        
        # Collar
        draw.polygon([(cx-25, body_top), (cx-15, body_top+30), (cx, body_top+35),
                     (cx+15, body_top+30), (cx+25, body_top)], fill=colors["shirt"])
        
        # Tie
        draw.polygon([(cx-8, body_top+35), (cx+8, body_top+35), (cx+5, body_top+70),
                     (cx, body_top+75), (cx-5, body_top+70)], 
                    fill=colors["tie"], outline=colors["outline"], width=2)
        
        # Head
        draw.ellipse([cx-head_r, cy-head_r, cx+head_r, cy+head_r],
                    fill=colors["skin"], outline=colors["outline"], width=3)
        
        # Hair
        draw.polygon([(cx-head_r, cy-head_r+10), (cx-head_r+20, cy-head_r-5),
                     (cx, cy-head_r-8), (cx+head_r-20, cy-head_r-5),
                     (cx+head_r, cy-head_r+10)], fill=(50,40,30), outline=colors["outline"], width=2)
        
        # Eyes
        eye_y, eye_sp, eye_sz = cy - 15, 25, 14
        blink = frame_data.get('blink', False)
        
        if not blink:
            for ox in [-eye_sp, eye_sp]:
                draw.ellipse([cx+ox-eye_sz, eye_y-eye_sz, cx+ox+eye_sz, eye_y+eye_sz],
                           fill=colors["eye_white"], outline=colors["outline"], width=2)
                draw.ellipse([cx+ox+5-6, eye_y-6, cx+ox+5+6, eye_y+6], fill=colors["eyes"])
                draw.ellipse([cx+ox+2, eye_y-5, cx+ox+5, eye_y-2], fill=(255,255,255))
        else:
            for ox in [-eye_sp, eye_sp]:
                draw.arc([cx+ox-eye_sz, eye_y-4, cx+ox+eye_sz, eye_y+4], 0, 180, 
                        fill=colors["outline"], width=3)
        
        # Nose
        draw.polygon([(cx-4, cy-5), (cx+4, cy-5), (cx, cy+5)],
                    fill=colors["skin"], outline=colors["outline"], width=2)
        
        # Mouth
        mouth_y = cy + 20
        mouth_open = frame_data.get('mouth_open', 0)
        if mouth_open > 0.15:
            h = int(5 + mouth_open * 25)
            draw.ellipse([cx-17, mouth_y-h//2, cx+17, mouth_y+h//2],
                        fill=(255,120,120), outline=colors["outline"], width=2)
        else:
            draw.arc([cx-17, mouth_y-12, cx+17, mouth_y+12], 0, 180, fill=colors["outline"], width=3)
        
        # Arms
        arm_mv = frame_data.get('arm_movement', 0)
        
        # Left arm
        draw.ellipse([cx-70, body_top+25, cx-30, body_top+70], fill=colors["suit"], 
                    outline=colors["outline"], width=2)
        draw.ellipse([cx-65, body_top+60, cx-35, body_top+90], fill=colors["skin"],
                    outline=colors["outline"], width=2)
        
        # Right arm (pointing)
        ptr_x = width//2 + int(arm_mv)
        ptr_y = body_top + 20
        draw.line([(cx+50, body_top+45), (ptr_x-30, ptr_y)], fill=colors["suit"], width=25)
        draw.ellipse([ptr_x-40, ptr_y-15, ptr_x-10, ptr_y+15], fill=colors["skin"],
                    outline=colors["outline"], width=2)
        draw.ellipse([ptr_x-15, ptr_y-5, ptr_x, ptr_y+5], fill=colors["skin"],
                    outline=colors["outline"], width=2)
    
    def _draw_scrolling_text(self, draw, text, language, width, height, frame_data):
        # Text area
        tx, ty = width//2 + 10, 60
        tw, th = width - tx - 30, height - 120
        
        # Shadow
        self._rounded_rect(draw, [tx+5, ty+5, tx+tw+5, ty+th+5], 15, (200,200,200), None, 0)
        # Main area
        self._rounded_rect(draw, [tx, ty, tx+tw, ty+th], 15, (255,255,255), (100,150,200), 4)
        
        # Get font
        font, font_size = self._get_font(language)
        
        # Wrap text
        lines = self._wrap_text(text, tw-40, font, language)
        if not lines:
            return
        
        # Calculate scrolling - FIXED
        progress = frame_data.get('progress', 0)
        if progress == 0:
            ts = frame_data.get('timestamp', 0)
            dur = frame_data.get('total_duration', 1)
            progress = ts / dur if dur > 0 else 0
        progress = max(0, min(1, progress))
        
        line_h = font_size + 8
        visible = (th - 40) // line_h
        total = len(lines)
        
        if total <= visible:
            scroll_off = 0
            start_line = 0
        else:
            max_scroll = (total - visible) * line_h
            scroll_off = int(progress * max_scroll)
            start_line = scroll_off // line_h
        
        # Current spoken line
        mouth = frame_data.get('mouth_open', 0)
        current_line = int(progress * total)
        
        # Draw lines
        text_y = ty + 20 - (scroll_off % line_h)
        
        for idx in range(start_line, min(start_line + visible + 2, total)):
            if text_y < ty + 10:
                text_y += line_h
                continue
            if text_y > ty + th - 20:
                break
            
            line = lines[idx]
            is_current = (idx == current_line and mouth > 0.2)
            
            if is_current:
                try:
                    bbox = font.getbbox(line)
                    lw = bbox[2] - bbox[0]
                    draw.rectangle([tx+15, text_y-2, tx+20+lw, text_y+font_size+2], fill=(255,255,200))
                except:
                    pass
                draw.text((tx+20, text_y), line, fill=(0,0,100), font=font)
            else:
                draw.text((tx+20, text_y), line, fill=(30,30,30), font=font)
            
            text_y += line_h
        
        # Scroll indicator
        if total > visible:
            self._scroll_indicator(draw, tx+tw-15, ty+20, th-40, progress)
    
    def _scroll_indicator(self, draw, x, y, h, progress):
        draw.rectangle([x, y, x+8, y+h], fill=(220,220,220), outline=(150,150,150), width=1)
        thumb_h = max(20, h//10)
        thumb_y = y + int((h - thumb_h) * progress)
        draw.rectangle([x+1, thumb_y, x+7, thumb_y+thumb_h], fill=(100,150,200), outline=(70,120,170))
    
    def _get_font(self, language):
        fonts = {"english": ("arial.ttf", 22), "hindi": ("mangal.ttf", 24), "kannada": ("tunga.ttf", 24)}
        name, size = fonts.get(language, ("arial.ttf", 22))
        
        paths = [f"C:\\Windows\\Fonts\\{name}", f"/usr/share/fonts/truetype/{name}",
                f"C:\\Windows\\Fonts\\Nirmala.ttf", f"C:\\Windows\\Fonts\\nirmala.ttf"]
        
        for p in paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size), size
                except:
                    pass
        return ImageFont.load_default(), 20
    
    def _wrap_text(self, text, max_w, font, language):
        if language == "hindi":
            sentences = text.replace('।', '.').split('.')
        elif language == "kannada":
            sentences = text.replace('।', '.').replace('|', '.').split('.')
        else:
            sentences = text.split('.')
        
        lines = []
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            sent += '.'
            
            words = sent.split()
            current = []
            
            for word in words:
                test = ' '.join(current + [word])
                try:
                    w = font.getbbox(test)[2] - font.getbbox(test)[0]
                    if w <= max_w:
                        current.append(word)
                    else:
                        if current:
                            lines.append(' '.join(current))
                        current = [word]
                except:
                    if len(test) <= 40:
                        current.append(word)
                    else:
                        if current:
                            lines.append(' '.join(current))
                        current = [word]
            
            if current:
                lines.append(' '.join(current))
        
        return lines
    
    def _rounded_rect(self, draw, coords, r, fill, outline, width):
        x1, y1, x2, y2 = coords
        draw.rectangle([x1+r, y1, x2-r, y2], fill=fill)
        draw.rectangle([x1, y1+r, x2, y2-r], fill=fill)
        draw.pieslice([x1, y1, x1+r*2, y1+r*2], 180, 270, fill=fill)
        draw.pieslice([x2-r*2, y1, x2, y1+r*2], 270, 360, fill=fill)
        draw.pieslice([x1, y2-r*2, x1+r*2, y2], 90, 180, fill=fill)
        draw.pieslice([x2-r*2, y2-r*2, x2, y2], 0, 90, fill=fill)
        
        if outline and width > 0:
            draw.arc([x1, y1, x1+r*2, y1+r*2], 180, 270, fill=outline, width=width)
            draw.arc([x2-r*2, y1, x2, y1+r*2], 270, 360, fill=outline, width=width)
            draw.arc([x1, y2-r*2, x1+r*2, y2], 90, 180, fill=outline, width=width)
            draw.arc([x2-r*2, y2-r*2, x2, y2], 0, 90, fill=outline, width=width)
            draw.line([(x1+r, y1), (x2-r, y1)], fill=outline, width=width)
            draw.line([(x1+r, y2), (x2-r, y2)], fill=outline, width=width)
            draw.line([(x1, y1+r), (x1, y2-r)], fill=outline, width=width)
            draw.line([(x2, y1+r), (x2, y2-r)], fill=outline, width=width)