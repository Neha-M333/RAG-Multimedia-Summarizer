@echo off
REM AI Document Intelligence System - Windows Installation Script
REM This script handles all dependency conflicts automatically

echo ==================================
echo AI Document Intelligence System
echo Automated Installation Script
echo ==================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Clean up conflicting packages
echo.
echo Step 1: Cleaning up conflicting packages...
pip uninstall -y googletrans deep-translator httpx idna 2>nul
echo [OK] Cleanup complete

REM Upgrade pip
echo.
echo Step 2: Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
echo [OK] Pip upgraded

REM Install PyTorch
echo.
echo Step 3: Installing PyTorch...
echo Select your platform:
echo 1) CPU only (default)
echo 2) NVIDIA GPU (CUDA 11.8)
echo 3) NVIDIA GPU (CUDA 12.1)
set /p pytorch_choice="Enter choice [1-3]: "

if "%pytorch_choice%"=="2" (
    echo [OK] Installing PyTorch with CUDA 11.8...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
) else if "%pytorch_choice%"=="3" (
    echo [OK] Installing PyTorch with CUDA 12.1...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
) else (
    echo [OK] Installing PyTorch (CPU only)...
    pip install torch torchvision torchaudio
)

REM Install core dependencies
echo.
echo Step 4: Installing core dependencies...
pip install streamlit>=1.28.0 python-dotenv>=1.0.0 openai>=1.3.0 tiktoken>=0.5.1
echo [OK] Core dependencies installed

REM Install LangChain
echo.
echo Step 5: Installing LangChain ecosystem...
pip install langchain>=0.1.0 langchain-community>=0.0.10 langchain-openai>=0.0.2
echo [OK] LangChain installed

REM Install database packages
echo.
echo Step 6: Installing database packages...
pip install chromadb>=0.4.18 sqlite-utils>=3.35.0
echo [OK] Databases installed

REM Install document processing
echo.
echo Step 7: Installing document processing libraries...
pip install pdfplumber>=0.10.3 PyPDF2>=3.0.1 pytesseract>=0.3.10 Pillow>=10.1.0
pip install opencv-python>=4.8.1.78 pandas>=2.1.3 openpyxl>=3.1.2 xlrd>=2.0.1
echo [OK] Document processing libraries installed

REM Install ML packages
echo.
echo Step 8: Installing ML and embeddings...
pip install sentence-transformers>=2.2.2 transformers>=4.35.0
pip install openai-whisper>=20231117 SpeechRecognition>=3.10.0
echo [OK] ML packages installed

REM Install multimedia processing
echo.
echo Step 9: Installing multimedia processing...
pip install pydub>=0.25.1 ffmpeg-python>=0.2.0 moviepy>=1.0.3
echo [OK] Multimedia packages installed

REM Install visualization
echo.
echo Step 10: Installing visualization libraries...
pip install plotly>=5.18.0 matplotlib>=3.8.2 seaborn>=0.13.0
echo [OK] Visualization libraries installed

REM Install data science packages
echo.
echo Step 11: Installing data science packages...
pip install numpy>=1.24.3 scipy>=1.11.4 scikit-learn>=1.3.2
echo [OK] Data science packages installed

REM Install utilities
echo.
echo Step 12: Installing utilities...
pip install requests>=2.31.0 aiohttp>=3.9.1 translate>=3.6.1
pip install pydantic>=2.5.2 pydantic-settings>=2.1.0 tqdm>=4.66.1
pip install loguru>=0.7.2 colorlog>=6.8.0
echo [OK] Utilities installed

REM Install production packages
echo.
echo Step 13: Installing production packages...
pip install gunicorn>=21.2.0 uvicorn[standard]>=0.25.0 python-multipart>=0.0.6
pip install prometheus-client>=0.19.0 psutil>=5.9.6
echo [OK] Production packages installed

REM Verify installation
echo.
echo Step 14: Verifying installation...
python -c "import streamlit; import openai; import chromadb; import torch; print('All core packages imported successfully!')"
if errorlevel 1 (
    echo [ERROR] Some packages failed to import
    pause
    exit /b 1
)
echo [OK] Installation verified

REM Check for system dependencies
echo.
echo ==================================
echo System Dependencies Check
echo ==================================

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg is NOT installed
    echo   Install with: choco install ffmpeg
    echo   Or download from: https://ffmpeg.org/download.html
) else (
    echo [OK] FFmpeg is installed
)

where tesseract >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Tesseract is NOT installed
    echo   Download from: https://github.com/UB-Mannheim/tesseract/wiki
) else (
    echo [OK] Tesseract is installed
)

REM Final summary
echo.
echo ==================================
echo Installation Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Add your OpenAI API key to .env
echo 3. Run: streamlit run app.py
echo.
echo [OK] Setup finished successfully!
echo.
pause