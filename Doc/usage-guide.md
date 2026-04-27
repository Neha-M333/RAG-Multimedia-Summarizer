# Usage Guide

## Via the Web UI

### Upload & Process a Document

1. Open the app at [http://localhost:8501](http://localhost:8501)
2. Navigate to **📤 Upload & Process**
3. Drag and drop a file or click to browse
4. Select processing options:
   - Generate Summary
   - Extract Keywords
   - Generate Questions
   - Advanced Analysis
5. Click **🚀 Process Documents**

Supported formats: PDF, Excel, CSV, MP3/WAV, MP4/MOV, PNG/JPG

---

### Chat with Documents

1. Go to **💬 Intelligent Chat**
2. Type your question naturally — e.g. *"What are the key findings in the report?"*
3. Each answer includes:
   - The answer text
   - Source citations
   - Confidence score
   - Suggested follow-up questions

---

### View Analytics

Go to **📊 Analytics & Insights** to explore document statistics, chat history, cost tracking, and cache performance.

---

## Via Python (Programmatic Use)

### Process a PDF

```python
from backend.document_processor import DocumentProcessor
from backend.enhanced_db_manager import EnhancedDatabaseManager
from backend.advanced_rag_engine import AdvancedRAGEngine, QueryComplexity

processor = DocumentProcessor()
db_manager = EnhancedDatabaseManager("data/db.sqlite", "data/chromadb")
rag_engine = AdvancedRAGEngine(api_key="your-key")

# Extract content
result = processor.process_document("report.pdf", "pdf")

# Store metadata
doc_id = db_manager.add_document(
    file_name="report.pdf",
    file_type="pdf",
    metadata=result['metadata']
)

# Chunk and vectorize
chunks = rag_engine.chunk_text_adaptive(result['full_text'], complexity=QueryComplexity.MODERATE)
db_manager.add_chunks_to_vector_db(
    doc_id,
    [c['content'] for c in chunks],
    [c['metadata'] for c in chunks]
)
```

---

### Ask a Question

```python
# Find relevant content
relevant_docs = db_manager.semantic_search(
    query="What are the main conclusions?",
    top_k=5
)

# Generate answer
response = rag_engine.generate_answer_advanced(
    query="What are the main conclusions?",
    context_documents=relevant_docs,
    language="English"
)

print(response['answer'])
print(f"Confidence: {response['confidence']}")
```

---

### Summarize a Document

```python
# Executive summary (concise, business-focused)
summary = rag_engine.summarize_advanced(
    text=document_text,
    style="executive",
    language="English",
    target_length=300
)

# Other styles: "technical", "academic", "bullet", "narrative"
```

---

### Process Audio or Video

```python
from backend.multimedia_processor import AdvancedMultimediaProcessor

processor = AdvancedMultimediaProcessor()

# Transcribe audio
audio_result = processor.process_audio_advanced(
    file_path="interview.mp3",
    language="en",
    enable_diarization=True       # Speaker identification
)

# Analyze video
video_result = processor.process_video_advanced(
    file_path="presentation.mp4",
    extract_audio=True,
    detect_scenes=True,
    extract_text=True             # OCR on frames
)
```

---

### Multi-Document Synthesis

```python
synthesis = rag_engine.multi_document_synthesis(
    documents=[doc1, doc2, doc3],
    query="Compare the approaches and identify common themes",
    language="English"
)

print(synthesis['synthesis'])
```

---

→ Next: [API Reference](api-reference.md)
