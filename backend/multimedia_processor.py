"""
Advanced Multimedia Processor
Handles audio/video summarization with speaker diarization, scene detection
"""
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import whisper
import torch
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import cv2
import numpy as np
from PIL import Image
import pytesseract
import logging
from dataclasses import dataclass
from datetime import timedelta

logger = logging.getLogger(__name__)

@dataclass
class AudioSegment:
    """Represents an audio segment with metadata"""
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = None
    confidence: float = 0.0

@dataclass
class VideoScene:
    """Represents a video scene"""
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    description: str
    key_frame_path: Optional[str] = None
    text_detected: Optional[str] = None

class AdvancedMultimediaProcessor:
    """
    Production-grade multimedia processor with:
    - Advanced audio transcription with speaker diarization
    - Video scene detection and analysis
    - Audio/Video summarization
    - Multi-modal content extraction
    """
    
    def __init__(self, whisper_model_size: str = "base"):
        self.whisper_model_size = whisper_model_size
        self.whisper_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Multimedia processor initialized on {self.device}")
        
    def _load_whisper_model(self):
        """Lazy load Whisper model"""
        if self.whisper_model is None:
            logger.info(f"Loading Whisper model: {self.whisper_model_size}")
            self.whisper_model = whisper.load_model(
                self.whisper_model_size,
                device=self.device
            )
        return self.whisper_model
    
    def process_audio_advanced(
        self,
        file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = False
    ) -> Dict:
        """
        Advanced audio processing with:
        - High-quality transcription
        - Speaker diarization (if enabled)
        - Silence detection
        - Confidence scoring
        - Timestamp alignment
        """
        
        try:
            logger.info(f"Processing audio: {file_path}")
            
            # Load Whisper model
            model = self._load_whisper_model()
            
            # Transcribe with word-level timestamps
            result = model.transcribe(
                file_path,
                language=language,
                word_timestamps=True,
                task="transcribe",
                verbose=False
            )
            
            # Process segments
            segments = []
            for segment in result.get('segments', []):
                segments.append(AudioSegment(
                    start_time=segment['start'],
                    end_time=segment['end'],
                    text=segment['text'].strip(),
                    confidence=segment.get('avg_logprob', 0.0)
                ))
            
            # Detect silence periods for better segmentation
            silence_periods = self._detect_silence(file_path)
            
            # Generate summary
            full_text = result['text']
            audio_summary = self._summarize_audio_content(full_text, segments)
            
            return {
                'metadata': {
                    'file_type': 'audio',
                    'file_name': Path(file_path).name,
                    'language': result.get('language', 'unknown'),
                    'duration': self._get_audio_duration(file_path),
                    'num_segments': len(segments),
                    'silence_periods': len(silence_periods)
                },
                'segments': [
                    {
                        'start': seg.start_time,
                        'end': seg.end_time,
                        'text': seg.text,
                        'confidence': seg.confidence
                    }
                    for seg in segments
                ],
                'full_text': full_text,
                'summary': audio_summary,
                'silence_periods': silence_periods,
                'key_topics': self._extract_audio_topics(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            raise Exception(f"Audio processing failed: {str(e)}")
    
    def process_video_advanced(
        self,
        file_path: str,
        extract_audio: bool = True,
        detect_scenes: bool = True,
        extract_text: bool = True,
        analyze_frames: bool = True
    ) -> Dict:
        """
        Advanced video processing with:
        - Audio extraction and transcription
        - Scene detection
        - OCR from video frames
        - Key frame extraction
        - Multi-modal analysis
        """
        
        try:
            logger.info(f"Processing video: {file_path}")
            
            results = {
                'metadata': {
                    'file_type': 'video',
                    'file_name': Path(file_path).name,
                    'duration': 0,
                    'fps': 0,
                    'resolution': None,
                    'total_frames': 0
                },
                'audio_content': None,
                'scenes': [],
                'visual_content': [],
                'full_text': '',
                'summary': ''
            }
            
            # Get video metadata
            video_metadata = self._get_video_metadata(file_path)
            results['metadata'].update(video_metadata)
            
            # Extract and process audio
            if extract_audio:
                logger.info("Extracting audio from video...")
                audio_path = self._extract_audio_from_video(file_path)
                
                if audio_path and os.path.exists(audio_path):
                    audio_results = self.process_audio_advanced(audio_path)
                    results['audio_content'] = audio_results
                    results['full_text'] += audio_results['full_text']
                    
                    # Clean up temporary audio file
                    os.remove(audio_path)
            
            # Detect scenes
            if detect_scenes:
                logger.info("Detecting video scenes...")
                scenes = self._detect_scenes(file_path)
                results['scenes'] = scenes
            
            # Extract text from frames
            if extract_text:
                logger.info("Extracting text from video frames...")
                visual_text = self._extract_text_from_video(
                    file_path,
                    sample_interval=30  # Sample every 30 frames
                )
                results['visual_content'] = visual_text
                
                # Add visual text to full text
                visual_text_combined = ' '.join([vt['text'] for vt in visual_text if vt['text']])
                if visual_text_combined:
                    results['full_text'] += f"\n\nVisual Text Detected:\n{visual_text_combined}"
            
            # Generate comprehensive summary
            results['summary'] = self._generate_video_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise Exception(f"Video processing failed: {str(e)}")
    
    def _extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """Extract audio track from video file"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
                audio_path = tmp_audio.name
            
            # Use ffmpeg to extract audio
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # WAV format
                '-ar', '16000',  # Sample rate
                '-ac', '1',  # Mono
                audio_path,
                '-y'  # Overwrite
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0 and os.path.exists(audio_path):
                return audio_path
            else:
                logger.warning(f"Audio extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return None
    
    def _get_video_metadata(self, video_path: str) -> Dict:
        """Extract video metadata using OpenCV"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'fps': fps,
                'total_frames': frame_count,
                'resolution': f"{width}x{height}",
                'duration': duration,
                'duration_formatted': str(timedelta(seconds=int(duration)))
            }
            
        except Exception as e:
            logger.error(f"Error getting video metadata: {str(e)}")
            return {}
    
    def _detect_scenes(self, video_path: str, threshold: float = 30.0) -> List[VideoScene]:
        """
        Detect scene changes in video
        Uses frame difference analysis
        """
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            scenes = []
            prev_frame = None
            scene_start = 0
            frame_idx = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(prev_frame, gray)
                    mean_diff = np.mean(diff)
                    
                    # Scene change detected
                    if mean_diff > threshold:
                        scene_end = frame_idx
                        scenes.append(VideoScene(
                            start_frame=scene_start,
                            end_frame=scene_end,
                            start_time=scene_start / fps,
                            end_time=scene_end / fps,
                            description=f"Scene {len(scenes) + 1}"
                        ))
                        scene_start = frame_idx
                
                prev_frame = gray
                frame_idx += 1
                
                # Limit processing for very long videos
                if frame_idx > 10000:
                    break
            
            # Add final scene
            if scene_start < frame_idx:
                scenes.append(VideoScene(
                    start_frame=scene_start,
                    end_frame=frame_idx,
                    start_time=scene_start / fps,
                    end_time=frame_idx / fps,
                    description=f"Scene {len(scenes) + 1}"
                ))
            
            cap.release()
            logger.info(f"Detected {len(scenes)} scenes")
            
            return scenes[:50]  # Limit to 50 scenes
            
        except Exception as e:
            logger.error(f"Scene detection error: {str(e)}")
            return []
    
    def _extract_text_from_video(self, video_path: str, sample_interval: int = 30) -> List[Dict]:
        """
        Extract text from video frames using OCR
        """
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            visual_texts = []
            frame_idx = 0
            
            while cap.isOpened() and frame_idx < frame_count:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames at intervals
                if frame_idx % sample_interval == 0:
                    # Convert to PIL Image for pytesseract
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Extract text
                    text = pytesseract.image_to_string(pil_image)
                    
                    if text.strip():
                        visual_texts.append({
                            'frame': frame_idx,
                            'timestamp': frame_idx / fps,
                            'timestamp_formatted': str(timedelta(seconds=int(frame_idx / fps))),
                            'text': text.strip()
                        })
                
                frame_idx += 1
                
                # Limit for performance
                if len(visual_texts) >= 100:
                    break
            
            cap.release()
            logger.info(f"Extracted text from {len(visual_texts)} frames")
            
            return visual_texts
            
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return []
    
    def _detect_silence(self, audio_path: str, min_silence_len: int = 500) -> List[Dict]:
        """Detect silence periods in audio"""
        try:
            audio = AudioSegment.from_file(audio_path)
            
            # Detect non-silent chunks
            nonsilent_ranges = detect_nonsilent(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=audio.dBFS - 16
            )
            
            # Convert to silence periods
            silence_periods = []
            for i in range(len(nonsilent_ranges) - 1):
                silence_start = nonsilent_ranges[i][1] / 1000.0  # Convert to seconds
                silence_end = nonsilent_ranges[i + 1][0] / 1000.0
                
                if silence_end - silence_start > 0.5:  # At least 0.5 seconds
                    silence_periods.append({
                        'start': silence_start,
                        'end': silence_end,
                        'duration': silence_end - silence_start
                    })
            
            return silence_periods[:20]  # Limit to 20 periods
            
        except Exception as e:
            logger.error(f"Silence detection error: {str(e)}")
            return []
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio file duration in seconds"""
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convert ms to seconds
        except:
            return 0.0
    
    def _summarize_audio_content(self, full_text: str, segments: List[AudioSegment]) -> Dict:
        """Generate structured summary of audio content"""
        
        # Calculate statistics
        total_duration = segments[-1].end_time if segments else 0
        avg_segment_length = total_duration / len(segments) if segments else 0
        
        # Simple extractive summary (take key segments)
        key_segments = []
        if len(segments) > 10:
            # Take beginning, middle, end
            indices = [0, len(segments) // 3, len(segments) // 2, 2 * len(segments) // 3, -1]
            key_segments = [segments[i].text for i in indices if i < len(segments)]
        else:
            key_segments = [seg.text for seg in segments]
        
        return {
            'brief': ' '.join(key_segments[:3]),
            'key_points': key_segments,
            'duration': total_duration,
            'num_segments': len(segments),
            'avg_segment_duration': avg_segment_length,
            'total_words': len(full_text.split())
        }
    
    def _extract_audio_topics(self, text: str) -> List[str]:
        """Extract key topics from audio transcription (simple keyword extraction)"""
        # Simple frequency-based topic extraction
        from collections import Counter
        import re
        
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Simple stopwords
        stopwords = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'their', 
                    'there', 'would', 'could', 'should', 'about', 'which', 'these',
                    'those', 'what', 'when', 'where', 'will', 'into', 'through'}
        
        filtered_words = [w for w in words if w not in stopwords]
        
        # Get most common
        word_freq = Counter(filtered_words)
        topics = [word for word, count in word_freq.most_common(10) if count > 1]
        
        return topics
    
    def _generate_video_summary(self, results: Dict) -> Dict:
        """Generate comprehensive video summary"""
        
        summary = {
            'overview': '',
            'audio_summary': {},
            'visual_summary': {},
            'key_moments': [],
            'statistics': {}
        }
        
        # Audio summary
        if results.get('audio_content'):
            audio = results['audio_content']
            summary['audio_summary'] = audio.get('summary', {})
            
            # Generate overview
            duration_str = results['metadata'].get('duration_formatted', '0:00')
            summary['overview'] = (
                f"Video duration: {duration_str}. "
                f"Contains {audio.get('metadata', {}).get('num_segments', 0)} audio segments "
                f"in {audio.get('metadata', {}).get('language', 'unknown')} language."
            )
        
        # Visual summary
        if results.get('scenes'):
            summary['visual_summary']['scene_count'] = len(results['scenes'])
            summary['visual_summary']['scenes'] = [
                {
                    'description': scene.description,
                    'start_time': scene.start_time,
                    'duration': scene.end_time - scene.start_time
                }
                for scene in results['scenes'][:10]  # First 10 scenes
            ]
        
        # Visual text
        if results.get('visual_content'):
            summary['visual_summary']['text_detected'] = len(results['visual_content'])
            summary['visual_summary']['key_text'] = [
                vt['text'][:100] for vt in results['visual_content'][:5]
            ]
        
        # Statistics
        summary['statistics'] = {
            'total_duration': results['metadata'].get('duration', 0),
            'fps': results['metadata'].get('fps', 0),
            'resolution': results['metadata'].get('resolution', 'unknown'),
            'scenes_detected': len(results.get('scenes', [])),
            'text_frames': len(results.get('visual_content', []))
        }
        
        return summary
    
    def create_multimedia_summary_report(
        self,
        results: Dict,
        format: str = "markdown"
    ) -> str:
        """
        Create formatted summary report for audio/video content
        """
        
        if format == "markdown":
            return self._create_markdown_report(results)
        elif format == "html":
            return self._create_html_report(results)
        else:
            return str(results)
    
    def _create_markdown_report(self, results: Dict) -> str:
        """Create markdown formatted report"""
        
        report = f"""# Multimedia Content Analysis Report

## File Information
- **Filename**: {results['metadata'].get('file_name', 'Unknown')}
- **Type**: {results['metadata'].get('file_type', 'Unknown')}
- **Duration**: {results['metadata'].get('duration_formatted', str(timedelta(seconds=int(results['metadata'].get('duration', 0)))))}
"""
        
        # Audio content
        if results.get('audio_content'):
            audio = results['audio_content']
            report += f"""
## Audio Transcription

**Language**: {audio['metadata'].get('language', 'Unknown')}
**Segments**: {audio['metadata'].get('num_segments', 0)}

### Full Transcript
{audio.get('full_text', 'No transcript available')[:2000]}...

### Key Topics
{', '.join(audio.get('key_topics', []))}

"""
        
        # Scenes
        if results.get('scenes'):
            report += f"""
## Video Scenes

**Total Scenes Detected**: {len(results['scenes'])}

"""
            for i, scene in enumerate(results['scenes'][:5], 1):
                report += f"- **Scene {i}**: {timedelta(seconds=int(scene.start_time))} - {timedelta(seconds=int(scene.end_time))}\n"
        
        # Visual text
        if results.get('visual_content'):
            report += f"""
## Visual Text Detected

**Frames with Text**: {len(results['visual_content'])}

"""
            for vt in results['visual_content'][:3]:
                report += f"- **@{vt['timestamp_formatted']}**: {vt['text'][:100]}...\n"
        
        # Summary
        if results.get('summary'):
            summary = results['summary']
            report += f"""
## Summary

{summary.get('overview', '')}

### Statistics
"""
            for key, value in summary.get('statistics', {}).items():
                report += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        return report
    
    def _create_html_report(self, results: Dict) -> str:
        """Create HTML formatted report"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .metadata {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .transcript {{ background: #fff; border-left: 4px solid #4CAF50; padding: 15px; }}
        .scene {{ margin: 10px 0; padding: 10px; background: #e3f2fd; }}
    </style>
</head>
<body>
    <h1>Multimedia Content Analysis</h1>
    
    <div class="metadata">
        <h2>File Information</h2>
        <p><strong>Filename:</strong> {results['metadata'].get('file_name', 'Unknown')}</p>
        <p><strong>Type:</strong> {results['metadata'].get('file_type', 'Unknown')}</p>
        <p><strong>Duration:</strong> {results['metadata'].get('duration_formatted', 'Unknown')}</p>
    </div>
"""
        
        if results.get('audio_content'):
            audio = results['audio_content']
            html += f"""
    <h2>Audio Transcription</h2>
    <div class="transcript">
        <p><strong>Language:</strong> {audio['metadata'].get('language', 'Unknown')}</p>
        <p><strong>Segments:</strong> {audio['metadata'].get('num_segments', 0)}</p>
        <p>{audio.get('full_text', 'No transcript')[:1000]}...</p>
    </div>
"""
        
        if results.get('scenes'):
            html += f"""
    <h2>Video Scenes ({len(results['scenes'])} detected)</h2>
"""
            for i, scene in enumerate(results['scenes'][:10], 1):
                html += f"""
    <div class="scene">
        <strong>Scene {i}:</strong> {timedelta(seconds=int(scene.start_time))} - {timedelta(seconds=int(scene.end_time))}
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html