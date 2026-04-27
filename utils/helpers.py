"""
Helper utility functions for the AI Summarization System
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

def get_file_hash(file_path: str) -> str:
    """Generate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def validate_file_type(file_name: str, allowed_extensions: List[str]) -> bool:
    """Check if file extension is allowed"""
    ext = Path(file_name).suffix.lower()
    return ext in allowed_extensions

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def export_to_json(data: Any, file_path: str) -> bool:
    """Export data to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False

def export_to_csv(data: List[Dict], file_path: str) -> bool:
    """Export data to CSV file"""
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def load_json(file_path: str) -> Optional[Any]:
    """Load data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

def create_timestamp() -> str:
    """Create formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def split_text_by_sentences(text: str, max_sentences: int = 5) -> List[str]:
    """Split text into chunks by sentences"""
    import re
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            current_chunk.append(sentence)
            if len(current_chunk) >= max_sentences:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = []
    
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
    
    return chunks

def extract_metadata_from_path(file_path: str) -> Dict:
    """Extract metadata from file path"""
    path = Path(file_path)
    stat = path.stat()
    
    return {
        'name': path.name,
        'extension': path.suffix,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'absolute_path': str(path.absolute())
    }

def ensure_directory(directory: str) -> bool:
    """Ensure directory exists, create if not"""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False

def batch_process(items: List, batch_size: int = 10):
    """Process items in batches"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result

def calculate_similarity_score(text1: str, text2: str) -> float:
    """Calculate simple similarity score between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def format_chat_message(role: str, content: str, timestamp: Optional[str] = None) -> Dict:
    """Format chat message"""
    return {
        'role': role,
        'content': content,
        'timestamp': timestamp or create_timestamp()
    }

def parse_time_range(time_str: str) -> Optional[datetime]:
    """Parse relative time strings like '1 hour ago', '2 days ago'"""
    import re
    from datetime import timedelta
    
    match = re.match(r'(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago', time_str.lower())
    if not match:
        return None
    
    value, unit = int(match.group(1)), match.group(2)
    
    delta_map = {
        'second': timedelta(seconds=value),
        'minute': timedelta(minutes=value),
        'hour': timedelta(hours=value),
        'day': timedelta(days=value),
        'week': timedelta(weeks=value),
        'month': timedelta(days=value * 30),  # Approximate
        'year': timedelta(days=value * 365)   # Approximate
    }
    
    return datetime.now() - delta_map.get(unit, timedelta())

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    import re
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())

def count_sentences(text: str) -> int:
    """Count sentences in text"""
    import re
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

def estimate_reading_time(text: str, words_per_minute: int = 200) -> str:
    """Estimate reading time for text"""
    words = count_words(text)
    minutes = words / words_per_minute
    
    if minutes < 1:
        return "< 1 minute"
    elif minutes < 60:
        return f"{int(minutes)} minutes"
    else:
        hours = int(minutes / 60)
        mins = int(minutes % 60)
        return f"{hours}h {mins}m"

def highlight_keywords(text: str, keywords: List[str], 
                      highlight_format: str = "**{}**") -> str:
    """Highlight keywords in text"""
    import re
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(highlight_format.format(keyword), text)
    return text

def generate_summary_stats(text: str) -> Dict:
    """Generate summary statistics for text"""
    word_count = count_words(text)
    return {
        'word_count': word_count,
        'sentence_count': count_sentences(text),
        'character_count': len(text),
        'reading_time': estimate_reading_time(text),
        'average_word_length': sum(len(word) for word in text.split()) / max(word_count, 1)
    }

class TextPreprocessor:
    """Text preprocessing utilities"""
    
    @staticmethod
    def remove_extra_spaces(text: str) -> str:
        """Remove extra spaces"""
        return ' '.join(text.split())
    
    @staticmethod
    def normalize_line_breaks(text: str) -> str:
        """Normalize line breaks"""
        return text.replace('\r\n', '\n').replace('\r', '\n')
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        import re
        return re.sub(r'http[s]?://\S+', '', text)
    
    @staticmethod
    def remove_emails(text: str) -> str:
        """Remove email addresses from text"""
        import re
        return re.sub(r'\S+@\S+', '', text)
    
    @staticmethod
    def remove_numbers(text: str) -> str:
        """Remove numbers from text"""
        import re
        return re.sub(r'\d+', '', text)
    
    @staticmethod
    def to_lowercase(text: str) -> str:
        """Convert text to lowercase"""
        return text.lower()
    
    @staticmethod
    def remove_punctuation(text: str) -> str:
        """Remove punctuation"""
        import string
        return text.translate(str.maketrans('', '', string.punctuation))
    
    @staticmethod
    def remove_stopwords(text: str, language: str = 'english') -> str:
        """Remove common stopwords"""
        # Basic stopwords for English
        stopwords_en = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have'
        }
        
        words = text.lower().split()
        filtered_words = [w for w in words if w not in stopwords_en]
        return ' '.join(filtered_words)

class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def is_valid_pdf(file_path: str) -> bool:
        """Check if file is a valid PDF"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        except:
            return False
    
    @staticmethod
    def is_valid_size(file_path: str, max_size_mb: int = 200) -> bool:
        """Check if file size is within limit"""
        try:
            size = os.path.getsize(file_path)
            return size <= (max_size_mb * 1024 * 1024)
        except:
            return False
    
    @staticmethod
    def get_mime_type(file_path: str) -> Optional[str]:
        """Get MIME type of file"""
        import mimetypes
        return mimetypes.guess_type(file_path)[0]
    
    @staticmethod
    def is_text_file(file_path: str) -> bool:
        """Check if file is a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except:
            return False

def log_error(error: Exception, context: str = "") -> None:
    """Log error with context"""
    timestamp = create_timestamp()
    error_msg = f"[{timestamp}] Error in {context}: {str(error)}"
    print(error_msg)
    
    # Optionally log to file
    log_file = Path("data/error.log")
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(error_msg + "\n")
    except:
        pass

def create_backup(source: str, backup_dir: str) -> bool:
    """Create backup of a file or directory"""
    import shutil
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_path = Path(source)
        backup_path = Path(backup_dir) / f"{source_path.name}_{timestamp}"
        
        ensure_directory(backup_dir)
        
        if source_path.is_file():
            shutil.copy2(source, backup_path)
        else:
            shutil.copytree(source, backup_path)
        
        return True
    except Exception as e:
        log_error(e, "create_backup")
        return False

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    try:
        return numerator / denominator if denominator != 0 else default
    except:
        return default

def percentage(part: float, whole: float) -> float:
    """Calculate percentage"""
    return safe_divide(part * 100, whole, 0.0)

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def get_file_extension(filename: str) -> str:
    """Get file extension without the dot"""
    return Path(filename).suffix.lstrip('.')

def is_empty_file(file_path: str) -> bool:
    """Check if file is empty"""
    try:
        return os.path.getsize(file_path) == 0
    except:
        return True

def retry_on_failure(func, max_attempts: int = 3, delay: float = 1.0):
    """Retry a function on failure"""
    import time
    
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                raise e

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

# Convenience exports
__all__ = [
    'get_file_hash',
    'format_file_size',
    'validate_file_type',
    'clean_text',
    'truncate_text',
    'export_to_json',
    'export_to_csv',
    'load_json',
    'create_timestamp',
    'sanitize_filename',
    'split_text_by_sentences',
    'extract_metadata_from_path',
    'ensure_directory',
    'batch_process',
    'merge_dicts',
    'calculate_similarity_score',
    'format_chat_message',
    'parse_time_range',
    'extract_urls',
    'count_words',
    'count_sentences',
    'estimate_reading_time',
    'highlight_keywords',
    'generate_summary_stats',
    'TextPreprocessor',
    'FileValidator',
    'log_error',
    'create_backup',
    'chunk_list',
    'flatten_dict',
    'safe_divide',
    'percentage',
    'format_duration',
    'get_file_extension',
    'is_empty_file',
    'retry_on_failure',
    'deep_merge_dicts'
]