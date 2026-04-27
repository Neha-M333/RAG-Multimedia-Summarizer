# Architecture

## System Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                    │
│     Multi-page navigation, visualizations, session      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                   Business Logic Layer                   │
│                                                          │
│   ┌─────────────────────┐   ┌────────────────────────┐  │
│   │  Advanced RAG Engine│   │  Multimedia Processor  │  │
│   │  · Query analysis   │   │  · Audio transcription │  │
│   │  · Summarization    │   │  · Video scene detect  │  │
│   │  · Answer validation│   │  · Frame OCR           │  │
│   └─────────────────────┘   └────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    Data Access Layer                     │
│                                                          │
│   ┌─────────────────────┐   ┌────────────────────────┐  │
│   │  Enhanced DB Manager│   │  Vector Store          │  │
│   │  · Connection pool  │   │  (ChromaDB)            │  │
│   │  · Query cache      │   │  · Embeddings          │  │
│   │  · Analytics        │   │  · Semantic search     │  │
│   └─────────────────────┘   └────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                      Storage Layer                       │
│        SQLite (metadata)  ·  ChromaDB  ·  File store    │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
User uploads file
       │
       ▼
Document Processor
· Type detection
· Content extraction (PDF / OCR / Whisper / OpenCV)
· Metadata generation
       │
       ▼
RAG Engine
· Adaptive text chunking
· Embedding generation
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
  SQLite DB       ChromaDB       File Store
  (metadata)      (vectors)      (raw files)
       │              │
       └──────┬───────┘
              │
       User asks a question
              │
              ▼
       Semantic Search
       · Vector similarity scoring
       · Metadata filtering
              │
              ▼
       RAG Answer Generation
       · Context assembly
       · LLM inference
       · Self-validation
              │
              ▼
       Response to User
       · Answer
       · Source citations
       · Confidence score
       · Follow-up questions
```

---

## Key Components

### Advanced RAG Engine (`backend/advanced_rag_engine.py`)

Handles the full question-answering pipeline. Detects query complexity (`SIMPLE` → `EXPERT`), selects a matching processing strategy (chunk size, temperature, reasoning depth), and validates the final answer against its sources before returning it.

### Multimedia Processor (`backend/multimedia_processor.py`)

Wraps FFmpeg, Whisper, and OpenCV into a unified API for audio transcription, video scene detection, and OCR. All three pipelines converge into a single structured result dict.

### Enhanced Database Manager (`backend/enhanced_db_manager.py`)

Manages both SQLite (structured metadata) and ChromaDB (vector embeddings) through a single interface. Includes a connection pool, an in-memory LRU cache for repeated queries, and an analytics tracker that logs cost, latency, and cache hits.

---

## Design Decisions

**Why SQLite + ChromaDB together?** SQLite handles structured metadata queries (filter by file type, date, size) while ChromaDB handles unstructured semantic similarity. Combining them lets the search layer apply both types of filter simultaneously.

**Why adaptive chunking?** Simple factual queries work best with small, precise chunks. Complex analytical queries need larger chunks with more context. Automatically sizing chunks to query complexity improves answer quality without manual tuning.

**Why local LLM support?** Data-sensitive deployments (legal, healthcare, HR) may not be able to send documents to a third-party API. The Ollama integration makes the system viable for fully air-gapped environments.
