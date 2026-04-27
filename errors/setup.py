"""
Setup script for AI Summarization System
Run: python setup.py
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required, but {version.major}.{version.minor} found")
        return False

def check_command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def check_dependencies():
    """Check system dependencies"""
    print_info("Checking system dependencies...")
    
    dependencies = {
        'tesseract': 'Tesseract OCR',
        'ffmpeg': 'FFmpeg'
    }
    
    missing = []
    for cmd, name in dependencies.items():
        if check_command_exists(cmd):
            print_success(f"{name} found")
        else:
            print_warning(f"{name} not found")
            missing.append(name)
    
    if missing:
        print_warning(f"\nMissing dependencies: {', '.join(missing)}")
        print_info("Installation instructions:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr ffmpeg")
        print("  macOS: brew install tesseract ffmpeg")
        print("  Windows: Download from official websites")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print_info("Creating directory structure...")
    
    directories = [
        'data/uploads',
        'data/processed',
        'data/databases/chromadb',
        'backend',
        'utils',
        'pages'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Created {directory}")
    
    # Create __init__.py files
    for module in ['backend', 'utils']:
        init_file = Path(module) / '__init__.py'
        init_file.touch(exist_ok=True)

def create_env_file():
    """Create .env file from template"""
    print_info("Setting up environment file...")
    
    env_file = Path('.env')
    if env_file.exists():
        print_warning(".env file already exists, skipping...")
        return
    
    print_info("Please enter your OpenAI API key:")
    api_key = input("API Key: ").strip()
    
    env_content = f"""# OpenAI API Configuration
OPENAI_API_KEY={api_key}

# Model Selection
LLM_MODEL=gpt-3.5-turbo

# Database Configuration
SQLITE_DB_PATH=data/databases/structured.db
CHROMADB_PATH=data/databases/chromadb

# Application Settings
MAX_FILE_SIZE_MB=200
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print_success(".env file created")

def install_python_dependencies():
    """Install Python packages"""
    print_info("Installing Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print_success("Python packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install Python packages")
        return False

def download_models():
    """Download required ML models"""
    print_info("Downloading AI models (this may take a while)...")
    
    try:
        # Download sentence-transformers model
        print_info("Downloading sentence-transformers model...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print_success("Sentence transformer model downloaded")
        
        # Download Whisper model
        print_info("Downloading Whisper model...")
        import whisper
        whisper.load_model("base")
        print_success("Whisper model downloaded")
        
        return True
    except Exception as e:
        print_error(f"Failed to download models: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print_info("Running basic tests...")
    
    try:
        # Test imports
        print_info("Testing imports...")
        import streamlit
        import pandas
        import openai
        import langchain
        print_success("All imports successful")
        
        # Test database creation
        print_info("Testing database setup...")
        from backend.database_manager import DatabaseManager
        from utils.config import Config
        
        db = DatabaseManager(
            str(Config.SQLITE_DB),
            str(Config.CHROMADB_DIR)
        )
        print_success("Database setup successful")
        
        return True
    except Exception as e:
        print_error(f"Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print_header("AI Summarization System Setup")
    
    # Check Python version
    if not check_python_version():
        print_error("Setup aborted: Python version too old")
        sys.exit(1)
    
    # Check system dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        response = input("\nContinue anyway? (y/n): ").lower()
        if response != 'y':
            print_error("Setup aborted")
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print_error("Setup aborted: Failed to install dependencies")
        sys.exit(1)
    
    # Download models
    print_info("\nDo you want to download AI models now?")
    print_info("(This will download ~500MB of data)")
    response = input("Download models? (y/n): ").lower()
    if response == 'y':
        download_models()
    else:
        print_warning("Skipping model download. They will be downloaded on first use.")
    
    # Run tests
    print_info("\nRunning system tests...")
    if run_tests():
        print_success("All tests passed!")
    else:
        print_warning("Some tests failed. System may not work correctly.")
    
    # Final message
    print_header("Setup Complete!")
    print_success("AI Summarization System is ready to use!")
    print_info("\nNext steps:")
    print("  1. Make sure your OpenAI API key is set in .env")
    print("  2. Run: streamlit run app.py")
    print("  3. Open browser at: http://localhost:8501")
    print("\nFor help, check README.md or visit the GitHub repo")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nSetup failed with error: {e}")
        sys.exit(1)