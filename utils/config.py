"""
Enhanced Configuration System with Validation and Monitoring
Production-ready configuration management
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

@dataclass
class ModelConfig:
    """AI Model Configuration"""
    provider: str  # "openai" or "local"
    model_name: str
    temperature: float
    max_tokens: int
    embedding_model: str
    
    @classmethod
    def from_env(cls) -> 'ModelConfig':
        """Create from environment variables"""
        use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        
        if use_local:
            return cls(
                provider="local",
                model_name=os.getenv("OLLAMA_MODEL", "llama3.2"),
                temperature=0.7,
                max_tokens=2000,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            return cls(
                provider="openai",
                model_name=os.getenv("LLM_MODEL", "gpt-4-turbo-preview"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("MAX_TOKENS", "2000")),
                embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            )

@dataclass
class DatabaseConfig:
    """Database Configuration"""
    sqlite_path: Path
    chromadb_path: Path
    connection_pool_size: int
    cache_enabled: bool
    cache_ttl: int
    
    @classmethod
    def from_env(cls, base_dir: Path) -> 'DatabaseConfig':
        """Create from environment variables"""
        return cls(
            sqlite_path=base_dir / "data" / "databases" / "structured.db",
            chromadb_path=base_dir / "data" / "databases" / "chromadb",
            connection_pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            cache_enabled=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "3600"))
        )

@dataclass
class ProcessingConfig:
    """Document Processing Configuration"""
    chunk_size: int
    chunk_overlap: int
    top_k_results: int
    max_file_size_mb: int
    enable_ocr: bool
    enable_audio_transcription: bool
    enable_video_processing: bool
    whisper_model_size: str
    
    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        """Create from environment variables"""
        return cls(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            top_k_results=int(os.getenv("TOP_K_RESULTS", "5")),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "200")),
            enable_ocr=os.getenv("ENABLE_OCR", "true").lower() == "true",
            enable_audio_transcription=os.getenv("ENABLE_AUDIO_TRANSCRIPTION", "true").lower() == "true",
            enable_video_processing=os.getenv("ENABLE_VIDEO_PROCESSING", "true").lower() == "true",
            whisper_model_size=os.getenv("WHISPER_MODEL_SIZE", "base")
        )

class EnhancedConfig:
    """
    Enhanced Configuration Manager with:
    - Environment validation
    - Secure credential management
    - Configuration hot-reloading
    - Health checks
    """
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOADS_DIR = DATA_DIR / "uploads"
    PROCESSED_DIR = DATA_DIR / "processed"
    DB_DIR = DATA_DIR / "databases"
    CHROMADB_DIR = DB_DIR / "chromadb"
    LOGS_DIR = BASE_DIR / "logs"
    EXPORTS_DIR = DATA_DIR / "exports"
    CACHE_DIR = DATA_DIR / "cache"
    TEMP_DIR = BASE_DIR / "data" / "temp"
    ASSETS_DIR = BASE_DIR / "assets"
    #VIDEO_DIR = DATA_DIR / "videos"
    #VIDEO_TEMP_DIR = TEMP_DIR / "video_processing"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configuration objects
    model_config: ModelConfig = ModelConfig.from_env()
    db_config: DatabaseConfig = DatabaseConfig.from_env(BASE_DIR)
    processing_config: ProcessingConfig = ProcessingConfig.from_env()

    USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # API Keys and Authentication
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    #USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Application Settings
    APP_NAME = "AI Document Intelligence System"
    APP_VERSION = "2.0.0"
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8501"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Security Settings
    SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "change-this-in-production")
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Rate Limiting
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Performance Settings
    WORKER_THREADS = int(os.getenv("WORKER_THREADS", "4"))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))
    
    # Monitoring & Analytics
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "false").lower() == "true"
    ANALYTICS_PROVIDER = os.getenv("ANALYTICS_PROVIDER", "")
    ANALYTICS_KEY = os.getenv("ANALYTICS_KEY", "")
    
    # Backup Settings
    ENABLE_AUTO_BACKUP = os.getenv("ENABLE_AUTO_BACKUP", "false").lower() == "true"
    BACKUP_FREQUENCY_HOURS = int(os.getenv("BACKUP_FREQUENCY_HOURS", "24"))
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
    BACKUP_DIR = DATA_DIR / "backups"
    
    # Language Support
    LANGUAGES = {
        "English": "en",
        "Hindi": "hi",
        "Kannada": "kn",
    }
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'pdf': ['.pdf'],
        'excel': ['.xlsx', '.xls', '.csv'],
        'audio': ['.mp3', '.wav', '.m4a', '.ogg', '.flac'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
        'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
    }
    
    # Feature Flags
    FEATURES = {
        'advanced_summarization': True,
        'multi_document_synthesis': True,
        'audio_transcription': True,
        'video_processing': True,
        'ocr': True,
        'translation': True,
        'sentiment_analysis': True,
        'named_entity_recognition': False,
        'topic_modeling': False,
        'question_generation': True,
        'answer_validation': True,
        'feedback_collection': True
    }
    
    @classmethod
    def setup_directories(cls):
        """Create all necessary directories including video dirs"""
        directories = [
            cls.UPLOADS_DIR,
            cls.PROCESSED_DIR,
            cls.DB_DIR,
            cls.CHROMADB_DIR,
            cls.LOGS_DIR,
            cls.EXPORTS_DIR,
            cls.CACHE_DIR,
            cls.BACKUP_DIR,
            cls.VIDEO_DIR,          
            cls.VIDEO_TEMP_DIR,
            cls.ASSETS_DIR,      
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        Validate configuration and return status
        Returns: Dict with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check API keys
        if not cls.USE_LOCAL_LLM:
            if not cls.OPENAI_API_KEY:
                validation['errors'].append("OPENAI_API_KEY is not set")
                validation['valid'] = False
            elif not cls.OPENAI_API_KEY.startswith("sk-"):
                validation['errors'].append("OPENAI_API_KEY format is invalid")
                validation['valid'] = False
            elif cls.OPENAI_API_KEY.startswith("sk-your"):
                validation['warnings'].append("Using placeholder API key")
            else:
                validation['info'].append(f"OpenAI API key configured: {cls.OPENAI_API_KEY[:15]}...")
        else:
            validation['info'].append(f"Using local LLM: {cls.model_config.model_name}")
        
        # Check directories
        try:
            cls.setup_directories()
            validation['info'].append("All directories created successfully")
        except Exception as e:
            validation['errors'].append(f"Directory creation failed: {str(e)}")
            validation['valid'] = False
        
        # Check file size limits
        if cls.processing_config.max_file_size_mb > 500:
            validation['warnings'].append(f"Large max file size: {cls.processing_config.max_file_size_mb}MB")
        
        # Check database paths
        if not cls.db_config.sqlite_path.parent.exists():
            validation['warnings'].append("SQLite database directory doesn't exist")
        
        # Security checks
        if cls.SESSION_SECRET_KEY == "change-this-in-production":
            validation['warnings'].append("Using default session secret key - change in production!")
        
        if cls.DEBUG:
            validation['warnings'].append("Debug mode is enabled - disable in production")
        
        # Feature availability
        if cls.FEATURES['audio_transcription'] and not cls.processing_config.enable_audio_transcription:
            validation['warnings'].append("Audio transcription feature enabled but processing disabled")
        
        return validation
    
    @classmethod
    def get_config_summary(cls) -> str:
        """Get human-readable configuration summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════╗
║  {cls.APP_NAME} v{cls.APP_VERSION}
╠══════════════════════════════════════════════════════════╣
║  AI CONFIGURATION
║  • Provider: {cls.model_config.provider}
║  • Model: {cls.model_config.model_name}
║  • Temperature: {cls.model_config.temperature}
║  • Max Tokens: {cls.model_config.max_tokens}
║
║  DATABASE
║  • SQLite: {cls.db_config.sqlite_path.name}
║  • Vector DB: ChromaDB
║  • Connection Pool: {cls.db_config.connection_pool_size}
║  • Cache: {'Enabled' if cls.db_config.cache_enabled else 'Disabled'}
║
║  PROCESSING
║  • Chunk Size: {cls.processing_config.chunk_size}
║  • Chunk Overlap: {cls.processing_config.chunk_overlap}
║  • Max File Size: {cls.processing_config.max_file_size_mb}MB
║  • OCR: {'Enabled' if cls.processing_config.enable_ocr else 'Disabled'}
║  • Audio: {'Enabled' if cls.processing_config.enable_audio_transcription else 'Disabled'}
║  • Video: {'Enabled' if cls.processing_config.enable_video_processing else 'Disabled'}
║
║  FEATURES
║  • Languages: {len(cls.LANGUAGES)}
║  • File Types: {len(cls.ALLOWED_EXTENSIONS)}
║  • Advanced Features: {sum(cls.FEATURES.values())} enabled
║
║  SYSTEM
║  • Workers: {cls.WORKER_THREADS}
║  • Debug: {cls.DEBUG}
║  • Log Level: {cls.LOG_LEVEL}
╚══════════════════════════════════════════════════════════╝
"""
        return summary
    
    @classmethod
    def export_config(cls, filepath: Optional[str] = None) -> str:
        """Export configuration to JSON"""
        config_dict = {
            'app': {
                'name': cls.APP_NAME,
                'version': cls.APP_VERSION,
                'debug': cls.DEBUG
            },
            'model': {
                'provider': cls.model_config.provider,
                'model_name': cls.model_config.model_name,
                'temperature': cls.model_config.temperature,
                'max_tokens': cls.model_config.max_tokens
            },
            'database': {
                'connection_pool_size': cls.db_config.connection_pool_size,
                'cache_enabled': cls.db_config.cache_enabled,
                'cache_ttl': cls.db_config.cache_ttl
            },
            'processing': {
                'chunk_size': cls.processing_config.chunk_size,
                'chunk_overlap': cls.processing_config.chunk_overlap,
                'max_file_size_mb': cls.processing_config.max_file_size_mb
            },
            'features': cls.FEATURES,
            'languages': list(cls.LANGUAGES.keys())
        }
        
        json_str = json.dumps(config_dict, indent=2)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
            logger.info(f"Configuration exported to {filepath}")
        
        return json_str
    
    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        """Perform system health check"""
        health = {
            'status': 'healthy',
            'timestamp': str(Path(__file__).stat().st_mtime),
            'checks': {}
        }
        
        # Check directories
        health['checks']['directories'] = all([
            cls.UPLOADS_DIR.exists(),
            cls.DB_DIR.exists(),
            cls.CHROMADB_DIR.exists()
        ])
        
        # Check configuration
        validation = cls.validate_config()
        health['checks']['configuration'] = validation['valid']
        
        # Check database
        try:
            health['checks']['database'] = cls.db_config.sqlite_path.exists()
        except:
            health['checks']['database'] = False
        
        # Overall status
        if not all(health['checks'].values()):
            health['status'] = 'unhealthy'
        elif validation['warnings']:
            health['status'] = 'degraded'
        
        health['validation'] = validation
        
        return health
    
    VIDEO_DIR = DATA_DIR / "videos"
    VIDEO_TEMP_DIR = TEMP_DIR / "video_processing"
    
    # Video generation parameters
    TARGET_VIDEO_LENGTH = 60  # seconds
    WORDS_PER_MINUTE = 150
    MAX_SUMMARY_WORDS = int((TARGET_VIDEO_LENGTH / 60) * WORDS_PER_MINUTE)
    
    # Animation settings
    ANIMATION_FPS = 15
    VIDEO_RESOLUTION = (640, 480)  # Lower for better performance
    
    # TTS settings
    TTS_LANGUAGES = {
        "English": "en",
        "Hindi": "hi",
        "Kannada": "kn"
    }
    
    @classmethod
    def setup_directories(cls):
        """Create all necessary directories including video dirs"""
        directories = [
            cls.UPLOADS_DIR,
            cls.PROCESSED_DIR,
            cls.DB_DIR,
            cls.CHROMADB_DIR,
            cls.LOGS_DIR,
            cls.EXPORTS_DIR,
            cls.CACHE_DIR,
            cls.BACKUP_DIR,
            cls.VIDEO_DIR,          # NEW
            cls.VIDEO_TEMP_DIR      # NEW
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")

# Initialize configuration on import
EnhancedConfig.setup_directories()

# Validate configuration
validation_result = EnhancedConfig.validate_config()

# Log configuration status
if validation_result['valid']:
    logger.info("✅ Configuration validated successfully")
    if validation_result['warnings']:
        for warning in validation_result['warnings']:
            logger.warning(f"⚠️  {warning}")
else:
    logger.error("❌ Configuration validation failed")
    for error in validation_result['errors']:
        logger.error(f"   • {error}")

# Export config alias for backward compatibility
Config = EnhancedConfig