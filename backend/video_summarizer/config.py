import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# Audio2Face Configuration
AUDIO2FACE_URL = os.getenv("AUDIO2FACE_URL", "http://localhost:8011")
AUDIO2FACE_ENDPOINT = f"{AUDIO2FACE_URL}/a2f/audio"

# Supported Languages with CORRECT TTS codes
SUPPORTED_LANGUAGES = {
    "english": {
        "code": "en",
        "tts_lang": "en",  # English
        "name": "English",
        "native_name": "English"
    },
    "hindi": {
        "code": "hi",
        "tts_lang": "hi",  # Hindi - CORRECT code for gTTS
        "name": "Hindi",
        "native_name": "हिंदी"
    },
    "kannada": {
        "code": "kn",
        "tts_lang": "kn",  # Kannada - CORRECT code for gTTS (may fallback to ta)
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ"
    }
}

# File Processing Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_FILE_TYPES = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
    "application/vnd.ms-powerpoint": [".ppt"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.ms-excel": [".xls"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/csv": [".csv"],
    "image/png": [".png"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/jpg": [".jpg"],
    "audio/mpeg": [".mp3"],
    "audio/wav": [".wav"],
    "audio/ogg": [".ogg"]
}

# Summary Configuration
TARGET_VIDEO_LENGTH = 60  # seconds
WORDS_PER_MINUTE = 150  # Average speaking rate
MAX_SUMMARY_WORDS = None
#MAX_SUMMARY_WORDS = int((TARGET_VIDEO_LENGTH / 60) * WORDS_PER_MINUTE)

# Character Animation Settings
CHARACTER_MODEL_PATH = "assets/character_model.glb"
ANIMATION_FPS = 15
VIDEO_RESOLUTION = (640, 480)  # Much smaller, uses less memory

# RAG Configuration
VECTOR_DB_PATH = "data/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
TEMP_DIR = "temp"
ASSETS_DIR = "assets"

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, VECTOR_DB_PATH]:
    os.makedirs(directory, exist_ok=True)