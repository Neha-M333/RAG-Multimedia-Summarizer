# Installation & Setup

## Prerequisites

- Python 3.10 or higher
- FFmpeg (audio/video processing)
- Tesseract OCR (image text extraction)

---

## System Dependencies

### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg tesseract-ocr tesseract-ocr-eng \
    tesseract-ocr-hin tesseract-ocr-kan python3-dev build-essential
```

### macOS
```bash
brew install ffmpeg tesseract tesseract-lang
```

### Windows
```bash
# Via Chocolatey
choco install ffmpeg tesseract

# Or download manually:
# FFmpeg: https://ffmpeg.org/download.html
# Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
```

---

## Python Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ai-document-intelligence.git
cd ai-document-intelligence

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development (includes linting, testing tools)
pip install -r requirements-dev.txt
```

---

## Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and fill in your settings. At minimum, set one of:

**Option A — OpenAI (cloud)**
```env
USE_LOCAL_LLM=false
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4-turbo-preview
```

**Option B — Ollama (local, no API key needed)**
```env
USE_LOCAL_LLM=true
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Verify Installation

```bash
ffmpeg -version
tesseract --version
python -c "import streamlit; import chromadb; print('All good!')"
```

---

## Run the App

```bash
streamlit run app.py

# Custom port
streamlit run app.py --server.port 8502
```

Open [http://localhost:8501](http://localhost:8501).

---

→ Next: [Configuration Reference](configuration.md)
