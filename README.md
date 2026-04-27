# 🧠 AI Document Intelligence System v2.0

**Professional-grade AI platform for document processing, intelligent analysis, and multilingual support**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Key Features

### 📄 Advanced Document Processing
- **Multi-format Support**: PDF, Excel, CSV, Audio, Video, Images
- **Intelligent OCR**: Automatic text extraction with fallback OCR
- **Audio Transcription**: High-accuracy speech-to-text with Whisper
- **Video Analysis**: Scene detection, frame extraction, visual text recognition
- **Structured Data**: Excel/CSV parsing with statistical analysis

### 🤖 Advanced AI Capabilities
- **Context-Aware Responses**: Chain-of-thought reasoning for complex queries
- **Query Complexity Detection**: Automatic strategy adaptation
- **Confidence Scoring**: Built-in answer validation
- **Multi-Document Synthesis**: Cross-document analysis and comparison
- **Multiple Summarization Styles**: Executive, Technical, Academic, Bullet Points, Narrative
- **Follow-up Generation**: Intelligent related question suggestions

### 🌍 Multilingual Support
- English, Hindi, Kannada, Spanish, French, German, Chinese, Japanese
- Real-time translation capabilities
- Language-aware response generation

### ⚡ Performance & Scalability
- **Vector Search**: Semantic search with ChromaDB
- **Connection Pooling**: Optimized database performance
- **Query Caching**: Intelligent result caching
- **Async Processing**: Parallel document processing
- **Batch Operations**: Efficient bulk processing

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🔧 Installation

### Prerequisites

```bash
# System requirements
Python 3.10+
FFmpeg (for video processing)
Tesseract OCR (for optical character recognition)
```

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg tesseract-ocr tesseract-ocr-eng \
    tesseract-ocr-hin tesseract-ocr-kan python3-dev build-essential
```

**MacOS:**
```bash
brew install ffmpeg tesseract tesseract-lang
```

**Windows:**
```bash
# Install via Chocolatey
choco install ffmpeg tesseract

# Or download installers:
# FFmpeg: https://ffmpeg.org/download.html
# Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
```

### Python Installation

1. **Clone Repository**
```bash
git clone https://github.com/your-org/ai-document-intelligence.git
cd ai-document-intelligence
```

2. **Create Virtual Environment**
```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate
```

3. **Install Dependencies**
```bash
# Install all requirements
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### requirements.txt
```txt
# Core
streamlit>=1.28.0
python-dotenv>=1.0.0

# AI & ML
openai>=1.0.0
langchain>=0.1.0
langchain-community>=0.0.10
sentence-transformers>=2.2.0
openai-whisper>=20230918

# Database
chromadb>=0.4.0
sqlite-utils>=3.35

# Document Processing
pdfplumber>=0.10.0
pytesseract>=0.3.10
opencv-python>=4.8.0
Pillow>=10.0.0
openpyxl>=3.1.0
pandas>=2.0.0

# Audio/Video
pydub>=0.25.0
SpeechRecognition>=3.10.0

# Visualization
plotly>=5.17.0

# Utilities
numpy>=1.24.0
requests>=2.31.0
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

### Quick Configuration

**.env file:**
```bash
# AI Configuration
USE_LOCAL_LLM=false  # Set to true for Ollama
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4-turbo-preview

# OR for Local LLM
# USE_LOCAL_LLM=true
# OLLAMA_MODEL=llama3.2
# OLLAMA_BASE_URL=http://localhost:11434

# Database
SQLITE_DB_PATH=data/databases/structured.db
CHROMADB_PATH=data/databases/chromadb

# Processing
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
TOP_K_RESULTS=5
MAX_FILE_SIZE_MB=200

# Features
ENABLE_OCR=true
ENABLE_AUDIO_TRANSCRIPTION=true
ENABLE_VIDEO_PROCESSING=true
WHISPER_MODEL_SIZE=base

# Performance
DB_POOL_SIZE=5
ENABLE_CACHING=true
CACHE_TTL=3600
WORKER_THREADS=4
```

## 🚀 Quick Start

### 1. Start the Application

```bash
# Run Streamlit app
streamlit run app.py

# Or with custom port
streamlit run app.py --server.port 8502
```

### 2. Upload Documents

1. Navigate to **📤 Upload & Process**
2. Drag and drop files or click to browse
3. Select processing options:
   - Generate Summary
   - Extract Keywords
   - Generate Questions
   - Advanced Analysis
4. Click **🚀 Process Documents**

### 3. Chat with Documents

1. Go to **💬 Intelligent Chat**
2. Configure chat settings (optional)
3. Ask questions about your documents
4. Get AI-powered answers with:
   - Source citations
   - Confidence scores
   - Follow-up questions

### 4. View Analytics

1. Visit **📊 Analytics & Insights**
2. Explore:
   - Document statistics
   - Chat analytics
   - Performance metrics
   - Usage trends

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                    │
│  (Enhanced UI, Multi-page Navigation, Visualizations)   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│               Application Layer                          │
├──────────────────────────────────────────────────────────┤
│  • Session Management    • Route Handling                │
│  • Error Handling        • Analytics Tracking            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                  Business Logic Layer                    │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────────┐     │
│  │ Advanced RAG    │  │ Multimedia Processor     │     │
│  │ Engine          │  │ - Audio Transcription    │     │
│  │ - Query Analysis│  │ - Video Analysis         │     │
│  │ - Summarization │  │ - OCR Processing         │     │
│  │ - Validation    │  │ - Scene Detection        │     │
│  └─────────────────┘  └──────────────────────────┘     │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                   Data Access Layer                      │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────────────┐    │
│  │ Enhanced DB      │  │ Vector Store             │    │
│  │ Manager          │  │ (ChromaDB)               │    │
│  │ - Connection Pool│  │ - Embeddings             │    │
│  │ - Query Cache    │  │ - Semantic Search        │    │
│  │ - Analytics      │  │ - Similarity Scoring     │    │
│  └──────────────────┘  └──────────────────────────┘    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                  Storage Layer                           │
├──────────────────────────────────────────────────────────┤
│  SQLite DB    │  ChromaDB   │  File Storage            │
└──────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. Advanced RAG Engine (`backend/advanced_rag_engine.py`)
**Responsibilities:**
- Query complexity detection
- Adaptive processing strategies
- Chain-of-thought reasoning
- Answer validation
- Multi-document synthesis

**Key Features:**
```python
# Automatic query complexity detection
complexity = engine.analyze_query_complexity(query)

# Adaptive chunking based on complexity
chunks = engine.chunk_text_adaptive(text, complexity)

# Advanced answer generation with validation
answer = engine.generate_answer_advanced(
    query=query,
    context_documents=docs,
    use_chain_of_thought=True
)

# Self-validation
validation = engine.validate_answer(query, answer, sources)
```

#### 2. Multimedia Processor (`backend/multimedia_processor.py`)
**Responsibilities:**
- Audio transcription with timestamps
- Video scene detection
- Frame-based OCR
- Multi-modal content extraction

**Key Features:**
```python
# Advanced audio processing
audio_result = processor.process_audio_advanced(
    file_path=audio_file,
    enable_diarization=True
)

# Comprehensive video analysis
video_result = processor.process_video_advanced(
    file_path=video_file,
    detect_scenes=True,
    extract_text=True
)

# Generate multimedia report
report = processor.create_multimedia_summary_report(
    results=video_result,
    format="markdown"
)
```

#### 3. Enhanced Database Manager (`backend/enhanced_db_manager.py`)
**Responsibilities:**
- Connection pooling
- Query caching
- Analytics tracking
- Performance monitoring

**Key Features:**
```python
# Connection pooling
with db_manager.pool.get_connection() as conn:
    cursor = conn.cursor()
    # Execute queries

# Cached semantic search
results = db_manager.semantic_search(
    query=query,
    top_k=5,
    use_cache=True
)

# Comprehensive analytics
analytics = db_manager.get_analytics_dashboard()
```

### Data Flow

```
┌──────────────┐
│ User Upload  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ Document Processor           │
│ • Type Detection             │
│ • Content Extraction         │
│ • Metadata Generation        │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ RAG Engine                   │
│ • Text Chunking              │
│ • Embedding Generation       │
└──────┬───────────────────────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ SQLite DB  │ │ ChromaDB   │ │ File Store │
│ (Metadata) │ │ (Vectors)  │ │ (Raw Files)│
└────────────┘ └────────────┘ └────────────┘
       │              │              │
       └──────────────┴──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │ User Query   │
              └──────┬───────┘
                     │
                     ▼
       ┌─────────────────────────────┐
       │ Semantic Search             │
       │ • Vector Similarity         │
       │ • Relevance Scoring         │
       └──────┬──────────────────────┘
              │
              ▼
       ┌─────────────────────────────┐
       │ RAG Answer Generation       │
       │ • Context Assembly          │
       │ • LLM Inference             │
       │ • Answer Validation         │
       └──────┬──────────────────────┘
              │
              ▼
       ┌─────────────────────────────┐
       │ Response to User            │
       │ • Answer                    │
       │ • Sources                   │
       │ • Confidence Score          │
       │ • Follow-up Questions       │
       └─────────────────────────────┘
```

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LOCAL_LLM` | false | Use Ollama instead of OpenAI |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `LLM_MODEL` | gpt-4-turbo-preview | Model name |
| `LLM_TEMPERATURE` | 0.7 | Response randomness (0-1) |
| `MAX_TOKENS` | 2000 | Max response length |
| `CHUNK_SIZE` | 1500 | Text chunk size |
| `CHUNK_OVERLAP` | 300 | Chunk overlap size |
| `TOP_K_RESULTS` | 5 | Number of search results |
| `MAX_FILE_SIZE_MB` | 200 | Max upload size |
| `DB_POOL_SIZE` | 5 | Database connection pool |
| `ENABLE_CACHING` | true | Enable query cache |
| `CACHE_TTL` | 3600 | Cache time-to-live (seconds) |
| `WORKER_THREADS` | 4 | Parallel processing threads |
| `WHISPER_MODEL_SIZE` | base | Whisper model (tiny/base/small/medium/large) |

### Advanced Configuration

**Processing Strategies:**
```python
from backend.advanced_rag_engine import QueryComplexity, ProcessingStrategy

# Define custom strategy
custom_strategy = ProcessingStrategy(
    chunk_size=2000,
    chunk_overlap=400,
    temperature=0.8,
    max_tokens=1500,
    use_reasoning_chain=True
)
```

**Database Optimization:**
```python
# Optimize database
db_manager.optimize_database()

# Clear cache
db_manager.clear_cache()

# Export data
backup_json = db_manager.export_data(format='json')
```

## 📖 Usage Guide

### Document Processing

#### Upload and Process PDF
```python
from backend.document_processor import DocumentProcessor
from backend.enhanced_db_manager import EnhancedDatabaseManager
from backend.advanced_rag_engine import AdvancedRAGEngine

# Initialize components
processor = DocumentProcessor()
db_manager = EnhancedDatabaseManager("data/db.sqlite", "data/chromadb")
rag_engine = AdvancedRAGEngine(api_key="your-key")

# Process PDF
result = processor.process_document("document.pdf", "pdf")

# Store in database
doc_id = db_manager.add_document(
    file_name="document.pdf",
    file_type="pdf",
    metadata=result['metadata']
)

# Chunk and vectorize
chunks = rag_engine.chunk_text_adaptive(
    result['full_text'],
    complexity=QueryComplexity.MODERATE
)

db_manager.add_chunks_to_vector_db(
    doc_id,
    [c['content'] for c in chunks],
    [c['metadata'] for c in chunks]
)
```

#### Process Audio/Video
```python
from backend.multimedia_processor import AdvancedMultimediaProcessor

processor = AdvancedMultimediaProcessor()

# Process audio
audio_result = processor.process_audio_advanced(
    file_path="interview.mp3",
    language="en",
    enable_diarization=True
)

# Process video
video_result = processor.process_video_advanced(
    file_path="presentation.mp4",
    extract_audio=True,
    detect_scenes=True,
    extract_text=True
)

# Generate report
report = processor.create_multimedia_summary_report(
    results=video_result,
    format="markdown"
)
```

### Intelligent Q&A

#### Basic Query
```python
# Search for relevant documents
relevant_docs = db_manager.semantic_search(
    query="What are the main findings?",
    top_k=5
)

# Generate answer
response = rag_engine.generate_answer_advanced(
    query="What are the main findings?",
    context_documents=relevant_docs,
    language="English"
)

print(response['answer'])
print(f"Confidence: {response['confidence']}")
print(f"Complexity: {response['complexity']}")
```

#### Complex Query with Reasoning
```python
# Enable chain-of-thought reasoning
response = rag_engine.generate_answer_advanced(
    query="Compare the methodologies and explain why approach A is better",
    context_documents=relevant_docs,
    use_chain_of_thought=True
)

# Get reasoning explanation
reasoning = rag_engine.explain_reasoning(
    query=query,
    answer=response['answer'],
    sources=relevant_docs
)

# Validate answer
validation = rag_engine.validate_answer(
    query=query,
    answer=response['answer'],
    sources=relevant_docs
)
```

### Advanced Summarization

#### Multiple Styles
```python
# Executive summary
exec_summary = rag_engine.summarize_advanced(
    text=document_text,
    style="executive",
    language="English",
    target_length=300
)

# Technical summary
tech_summary = rag_engine.summarize_advanced(
    text=document_text,
    style="technical",
    language="English",
    target_length=500
)

# Academic abstract
academic = rag_engine.summarize_advanced(
    text=document_text,
    style="academic",
    language="English",
    target_length=250
)
```

#### Multi-Document Synthesis
```python
# Synthesize across documents
synthesis = rag_engine.multi_document_synthesis(
    documents=[doc1, doc2, doc3],
    query="Compare the approaches and identify common themes",
    language="English"
)

print(synthesis['synthesis'])
```

### Analytics and Monitoring

#### Get Dashboard Analytics
```python
# Comprehensive analytics
analytics = db_manager.get_analytics_dashboard()

print(f"Total Documents: {analytics['documents']['total']}")
print(f"Total Chats: {analytics['chat']['total_messages']}")
print(f"Cache Hit Rate: {analytics['performance']['cache_hit_rate']:.2%}")
print(f"Total Cost: ${analytics['chat']['total_cost']:.4f}")
```

#### Performance Monitoring
```python
# Get statistics
stats = db_manager.get_statistics()

print(f"Queries Executed: {stats['performance']['queries_executed']}")
print(f"Avg Query Time: {stats['performance']['avg_query_time']:.3f}s")
print(f"Cache Hits: {stats['cache_stats']['hits']}")
print(f"Cache Hit Rate: {stats['cache_stats']['hit_rate']:.2%}")
```

## 🔌 API Reference

### Advanced RAG Engine

#### `analyze_query_complexity(query: str) -> QueryComplexity`
Analyzes query to determine processing complexity.

**Returns:** `SIMPLE`, `MODERATE`, `COMPLEX`, or `EXPERT`

#### `generate_answer_advanced(query, context_documents, language, use_chain_of_thought)`
Generates intelligent answer with validation.

**Parameters:**
- `query` (str): User question
- `context_documents` (List[Dict]): Relevant document chunks
- `language` (str): Response language
- `use_chain_of_thought` (bool): Enable reasoning chain

**Returns:** Dict with `answer`, `confidence`, `complexity`, `tokens_used`, `cost`

#### `summarize_advanced(text, style, language, target_length, include_metadata)`
Advanced summarization with multiple styles.

**Parameters:**
- `text` (str): Text to summarize
- `style` (str): `executive`, `technical`, `academic`, `bullet`, `narrative`
- `language` (str): Target language
- `target_length` (int): Desired word count
- `include_metadata` (bool): Include quality metrics

**Returns:** Dict with `summary`, `metadata`, `compression_ratio`, `cost`

### Enhanced Database Manager

#### `semantic_search(query, top_k, filter_metadata, use_cache)`
Performs semantic search with caching.

**Parameters:**
- `query` (str): Search query
- `top_k` (int): Number of results
- `filter_metadata` (Dict): Metadata filters
- `use_cache` (bool): Use query cache

**Returns:** List of documents with relevance scores

#### `get_analytics_dashboard() -> Dict`
Returns comprehensive system analytics.

**Returns:** Dict with `documents`, `chat`, `performance`, `usage_trends`

### Multimedia Processor

#### `process_audio_advanced(file_path, language, enable_diarization)`
Advanced audio transcription.

**Parameters:**
- `file_path` (str): Audio file path
- `language` (str): Audio language (optional)
- `enable_diarization` (bool): Enable speaker identification

**Returns:** Dict with `segments`, `full_text`, `summary`, `key_topics`

#### `process_video_advanced(file_path, extract_audio, detect_scenes, extract_text)`
Comprehensive video analysis.

**Parameters:**
- `file_path` (str): Video file path
- `extract_audio` (bool): Extract and transcribe audio
- `detect_scenes` (bool): Detect scene changes
- `extract_text` (bool): OCR from frames

**Returns:** Dict with `audio_content`, `scenes`, `visual_content`, `summary`

## 🚀 Deployment

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    tesseract-ocr-kan \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/uploads data/databases data/logs

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - USE_LOCAL_LLM=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  # Optional: Ollama for local LLM
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

### Production Deployment

**Using Gunicorn + Nginx:**
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:server
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🐛 Troubleshooting

### Common Issues

**1. FFmpeg not found**
```bash
# Verify installation
ffmpeg -version

# Add to PATH if needed
export PATH=$PATH:/usr/local/bin
```

**2. Tesseract OCR errors**
```bash
# Verify installation
tesseract --version

# Install language packs
apt-get install tesseract-ocr-all
```

**3. Out of memory errors**
```python
# Reduce chunk size
CHUNK_SIZE=1000
CHUNK_OVERLAP=150

# Use smaller Whisper model
WHISPER_MODEL_SIZE=tiny
```

**4. Slow performance**
```python
# Enable caching
ENABLE_CACHING=true

# Increase connection pool
DB_POOL_SIZE=10

# Use local LLM
USE_LOCAL_LLM=true
```

##