# 📚 API Documentation

Comprehensive API documentation for the AI Summarization System backend modules.

## Table of Contents
- [Document Processor](#document-processor)
- [Database Manager](#database-manager)
- [RAG Engine](#rag-engine)
- [Translator](#translator)
- [Helper Utilities](#helper-utilities)
- [Usage Examples](#usage-examples)

---

## Document Processor

### Class: `DocumentProcessor`

Handles multi-format document processing (PDF, Excel, Audio, Video).

#### Methods

##### `process_document(file_path: str, file_type: str) -> Dict`

Main entry point for processing any document type.

**Parameters:**
- `file_path` (str): Path to the document file
- `file_type` (str): Type of document ('pdf', 'excel', 'audio', 'video')

**Returns:**
- Dict containing:
  - `metadata`: Document metadata
  - `content`: Processed content
  - `full_text`: Complete extracted text

**Example:**
```python
from backend.document_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.process_document("report.pdf", "pdf")

print(result['metadata'])  # {'file_type': 'pdf', 'pages': 10, ...}
print(result['full_text'])  # Extracted text content
```

##### `process_pdf(file_path: str) -> Dict`

Extract text from PDF using pdfplumber and OCR fallback.

**Parameters:**
- `file_path` (str): Path to PDF file

**Returns:**
- Dict with metadata, content array, and full_text

**Example:**
```python
result = processor.process_pdf("document.pdf")
for page in result['content']:
    print(f"Page {page['page']}: {page['content'][:100]}...")
```

##### `process_excel(file_path: str) -> Dict`

Process Excel/CSV files with structured data extraction.

**Parameters:**
- `file_path` (str): Path to Excel/CSV file

**Returns:**
- Dict with structured data, metadata, and text representation

**Example:**
```python
result = processor.process_excel("data.xlsx")
for sheet in result['content']:
    print(f"Sheet: {sheet['sheet_name']}")
    print(f"Columns: {sheet['columns']}")
```

##### `process_audio(file_path: str) -> Dict`

Transcribe audio using Whisper.

**Parameters:**
- `file_path` (str): Path to audio file

**Returns:**
- Dict with transcription and metadata

**Example:**
```python
result = processor.process_audio("meeting.mp3")
print(result['full_text'])  # Complete transcription
print(result['metadata']['language'])  # Detected language
```

##### `process_video(file_path: str) -> Dict`

Extract and transcribe audio from video.

**Parameters:**
- `file_path` (str): Path to video file

**Returns:**
- Dict with transcription and metadata

**Example:**
```python
result = processor.process_video("presentation.mp4")
for segment in result['content']:
    print(f"{segment['start']}-{segment['end']}: {segment['text']}")
```

---

## Database Manager

### Class: `DatabaseManager`

Manages SQLite (structured) and ChromaDB (vector) databases.

#### Initialization

```python
from backend.database_manager import DatabaseManager

db = DatabaseManager(
    sqlite_path="data/databases/structured.db",
    chromadb_path="data/databases/chromadb"
)
```

#### Methods

##### `add_document(file_name: str, file_type: str, metadata: Dict) -> int`

Add new document to database.

**Parameters:**
- `file_name` (str): Name of the document
- `file_type` (str): Type of document
- `metadata` (Dict): Additional metadata

**Returns:**
- int: Document ID

**Example:**
```python
doc_id = db.add_document(
    file_name="report.pdf",
    file_type="pdf",
    metadata={"author": "John Doe", "pages": 50}
)
print(f"Document ID: {doc_id}")
```

##### `add_chunks_to_vector_db(document_id: int, chunks: List[str], metadata: List[Dict])`

Add document chunks to vector database for semantic search.

**Parameters:**
- `document_id` (int): ID of the document
- `chunks` (List[str]): List of text chunks
- `metadata` (List[Dict]): Metadata for each chunk

**Example:**
```python
chunks = ["First chunk of text", "Second chunk of text"]
metadata = [{"chunk_index": 0}, {"chunk_index": 1}]

db.add_chunks_to_vector_db(doc_id, chunks, metadata)
```

##### `semantic_search(query: str, top_k: int = 5) -> List[Dict]`

Perform semantic search across all documents.

**Parameters:**
- `query` (str): Search query
- `top_k` (int): Number of results to return

**Returns:**
- List[Dict]: List of relevant chunks with metadata

**Example:**
```python
results = db.semantic_search("machine learning applications", top_k=3)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Source: {result['metadata']['file_name']}")
    print(f"Similarity: {result['distance']}")
    print("---")
```

##### `save_chat_message(...)`

Save chat interaction to database.

**Parameters:**
- `session_id` (str): Unique session identifier
- `user_message` (str): User's message
- `assistant_message` (str): Assistant's response
- `language` (str): Language code
- `source_documents` (Optional[List]): Source documents used

**Example:**
```python
db.save_chat_message(
    session_id="user-123",
    user_message="What is AI?",
    assistant_message="AI is artificial intelligence...",
    language="en",
    source_documents=[{"content": "...", "metadata": {...}}]
)
```

##### `get_chat_history(session_id: str, limit: int = 50) -> List[Dict]`

Retrieve chat history for a session.

**Example:**
```python
history = db.get_chat_history("user-123", limit=10)

for msg in history:
    print(f"[{msg['timestamp']}]")
    print(f"User: {msg['user_message']}")
    print(f"Assistant: {msg['assistant_message']}")
```

##### `get_all_documents() -> List[Dict]`

Get list of all documents.

**Example:**
```python
docs = db.get_all_documents()

for doc in docs:
    print(f"{doc['file_name']} ({doc['file_type']}) - {doc['upload_date']}")
```

---

## RAG Engine

### Class: `RAGEngine`

Retrieval-Augmented Generation engine using LangChain.

#### Initialization

```python
from backend.rag_engine import RAGEngine

rag = RAGEngine(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo"  # or "gpt-4"
)
```

#### Methods

##### `chunk_text(text: str, metadata: Dict = None) -> List[Dict]`

Split text into chunks for processing.

**Parameters:**
- `text` (str): Text to chunk
- `metadata` (Dict): Optional metadata

**Returns:**
- List[Dict]: List of chunks with metadata

**Example:**
```python
text = "Long document text here..." * 100
chunks = rag.chunk_text(text, metadata={"source": "report.pdf"})

print(f"Total chunks: {len(chunks)}")
for i, chunk in enumerate(chunks[:3]):
    print(f"Chunk {i}: {chunk['content'][:100]}...")
```

##### `generate_answer(query: str, context_documents: List[Dict], language: str = "English") -> Dict`

Generate answer using RAG approach.

**Parameters:**
- `query` (str): User's question
- `context_documents` (List[Dict]): Retrieved relevant documents
- `language` (str): Response language

**Returns:**
- Dict containing answer, sources, and source count

**Example:**
```python
# First, get relevant documents
context = db.semantic_search("What is machine learning?", top_k=5)

# Generate answer
response = rag.generate_answer(
    query="What is machine learning?",
    context_documents=context,
    language="English"
)

print(response['answer'])
print(f"Used {response['source_count']} sources")
```

##### `summarize_text(text: str, language: str = "English", max_length: int = 500) -> str`

Generate summary of provided text.

**Parameters:**
- `text` (str): Text to summarize
- `language` (str): Summary language
- `max_length` (int): Maximum summary length in words

**Returns:**
- str: Summary text

**Example:**
```python
long_text = "..." # Your long document
summary = rag.summarize_text(
    text=long_text,
    language="Hindi",
    max_length=300
)

print(summary)
```

##### `extract_keywords(text: str, num_keywords: int = 10) -> List[str]`

Extract key terms from text.

**Example:**
```python
text = "Machine learning and artificial intelligence..."
keywords = rag.extract_keywords(text, num_keywords=5)

print("Keywords:", ", ".join(keywords))
```

##### `generate_questions(text: str, num_questions: int = 5) -> List[str]`

Generate potential questions from text.

**Example:**
```python
questions = rag.generate_questions(text, num_questions=5)

for i, question in enumerate(questions, 1):
    print(f"{i}. {question}")
```

##### `chat_with_context(messages: List[Dict], context: str, language: str) -> str`

Handle multi-turn conversations.

**Example:**
```python
messages = [
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI is..."},
    {"role": "user", "content": "Give me an example"}
]

response = rag.chat_with_context(
    messages=messages,
    context="Document context here...",
    language="English"
)

print(response)
```

---

## Translator

### Class: `Translator`

Multilingual translation for English, Hindi, and Kannada.

#### Initialization

```python
from backend.translator import Translator

translator = Translator(api_key="your-openai-api-key")
```

#### Methods

##### `translate_text(text: str, target_language: str, source_language: str = 'auto') -> Dict`

Translate text to target language.

**Parameters:**
- `text` (str): Text to translate
- `target_language` (str): Target language name
- `source_language` (str): Source language (auto-detect if 'auto')

**Returns:**
- Dict with translated text and metadata

**Example:**
```python
result = translator.translate_text(
    text="Hello, how are you?",
    target_language="Hindi"
)

print(result['translated_text'])  # "नमस्ते, आप कैसे हैं?"
print(result['method'])  # 'openai' or 'google'
```

##### `detect_language(text: str) -> str`

Detect language of text.

**Example:**
```python
text = "नमस्ते"
lang = translator.detect_language(text)
print(f"Detected language: {lang}")  # "Hindi"
```

##### `translate_batch(texts: List[str], target_language: str) -> List[Dict]`

Translate multiple texts.

**Example:**
```python
texts = ["Hello", "Goodbye", "Thank you"]
translations = translator.translate_batch(texts, "Kannada")

for orig, trans in zip(texts, translations):
    print(f"{orig} → {trans['translated_text']}")
```

---

## Helper Utilities

### Module: `utils.helpers`

Collection of utility functions.

#### File Operations

```python
from utils.helpers import *

# Format file size
size = format_file_size(1048576)  # "1.00 MB"

# Validate file type
is_valid = validate_file_type("doc.pdf", ['.pdf', '.docx'])

# Get file hash
hash = get_file_hash("document.pdf")

# Extract metadata
metadata = extract_metadata_from_path("document.pdf")
```

#### Text Processing

```python
# Clean text
clean = clean_text("  Extra   spaces  ")

# Truncate text
short = truncate_text("Long text...", max_length=50)

# Count words and sentences
words = count_words("This is a sentence.")
sentences = count_sentences("First. Second! Third?")

# Estimate reading time
time = estimate_reading_time(long_text)

# Generate stats
stats = generate_summary_stats(text)
print(stats)  # {'word_count': 100, 'sentence_count': 5, ...}
```

#### Text Preprocessing

```python
from utils.helpers import TextPreprocessor

# Remove extra spaces
clean = TextPreprocessor.remove_extra_spaces(text)

# Normalize line breaks
normalized = TextPreprocessor.normalize_line_breaks(text)

# Remove URLs
no_urls = TextPreprocessor.remove_urls(text)

# Remove emails
no_emails = TextPreprocessor.remove_emails(text)

# To lowercase
lower = TextPreprocessor.to_lowercase(text)
```

#### Export Functions

```python
# Export to JSON
export_to_json(data, "output.json")

# Export to CSV
export_to_csv(data_list, "output.csv")

# Load from JSON
data = load_json("input.json")
```

---

## Usage Examples

### Complete Workflow Example

```python
from backend.document_processor import DocumentProcessor
from backend.database_manager import DatabaseManager
from backend.rag_engine import RAGEngine
from utils.config import Config

# Initialize components
processor = DocumentProcessor()
db = DatabaseManager(str(Config.SQLITE_DB), str(Config.CHROMADB_DIR))
rag = RAGEngine(Config.OPENAI_API_KEY)

# 1. Process document
result = processor.process_document("report.pdf", "pdf")

# 2. Add to database
doc_id = db.add_document(
    file_name="report.pdf",
    file_type="pdf",
    metadata=result['metadata']
)

# 3. Chunk and store
chunks = rag.chunk_text(result['full_text'])
db.add_chunks_to_vector_db(
    doc_id,
    [c['content'] for c in chunks],
    [c['metadata'] for c in chunks]
)

# 4. Query the document
query = "What are the main findings?"
context = db.semantic_search(query, top_k=5)
response = rag.generate_answer(query, context, "English")

print(response['answer'])
```

### Multilingual Processing

```python
from backend.translator import Translator

translator = Translator(Config.OPENAI_API_KEY)

# Process English document, query in Hindi
result = processor.process_document("english_doc.pdf", "pdf")

# ... add to database ...

# Query in Hindi
query_hindi = "मुख्य निष्कर्ष क्या हैं?"

# Translate to English for search
query_en = translator.translate_text(query_hindi, "English")['translated_text']

# Search and answer
context = db.semantic_search(query_en, top_k=5)
answer_en = rag.generate_answer(query_en, context, "English")

# Translate answer back to Hindi
answer_hindi = translator.translate_text(
    answer_en['answer'],
    "Hindi"
)['translated_text']

print(answer_hindi)
```

### Batch Document Processing

```python
import os
from pathlib import Path

# Directory with multiple documents
docs_dir = Path("documents")

for file in docs_dir.glob("*.pdf"):
    try:
        # Process
        result = processor.process_document(str(file), "pdf")
        
        # Add to database
        doc_id = db.add_document(
            file_name=file.name,
            file_type="pdf",
            metadata=result['metadata']
        )
        
        # Chunk and store
        chunks = rag.chunk_text(result['full_text'])
        db.add_chunks_to_vector_db(
            doc_id,
            [c['content'] for c in chunks],
            [c['metadata'] for c in chunks]
        )
        
        # Generate summary
        summary = rag.summarize_text(result['full_text'])
        db.save_summary(doc_id, summary)
        
        print(f"✓ Processed: {file.name}")
        
    except Exception as e:
        print(f"✗ Error processing {file.name}: {e}")
```

### Custom Chat Bot

```python
class DocumentChatBot:
    def __init__(self, db_manager, rag_engine):
        self.db = db_manager
        self.rag = rag_engine
        self.conversation_history = []
    
    def ask(self, question, language="English"):
        # Search for relevant context
        context = self.db.semantic_search(question, top_k=5)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        
        # Generate response
        if len(self.conversation_history) > 1:
            # Multi-turn conversation
            context_text = "\n".join([d['content'] for d in context])
            response = self.rag.chat_with_context(
                messages=self.conversation_history,
                context=context_text,
                language=language
            )
        else:
            # First question
            result = self.rag.generate_answer(
                query=question,
                context_documents=context,
                language=language
            )
            response = result['answer']
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "answer": response,
            "sources": context
        }
    
    def clear_history(self):
        self.conversation_history = []

# Usage
bot = DocumentChatBot(db, rag)

response1 = bot.ask("What is machine learning?")
print(response1['answer'])

response2 = bot.ask("Can you give me examples?")
print(response2['answer'])

bot.clear_history()
```

### Audio Transcription Pipeline

```python
# Process multiple audio files
audio_files = ["meeting1.mp3", "meeting2.mp3", "interview.wav"]

for audio_file in audio_files:
    # Transcribe
    result = processor.process_audio(audio_file)
    
    # Store in database
    doc_id = db.add_document(
        file_name=audio_file,
        file_type="audio",
        metadata=result['metadata']
    )
    
    # Extract and store chunks
    chunks = rag.chunk_text(result['full_text'])
    db.add_chunks_to_vector_db(doc_id, 
                                [c['content'] for c in chunks],
                                [c['metadata'] for c in chunks])
    
    # Generate meeting summary
    summary = rag.summarize_text(
        text=result['full_text'],
        language="English",
        max_length=500
    )
    
    # Extract action items
    action_items = rag.generate_answer(
        query="List all action items and tasks mentioned",
        context_documents=[{"content": result['full_text']}],
        language="English"
    )
    
    print(f"\n=== {audio_file} ===")
    print(f"Summary: {summary}")
    print(f"Action Items: {action_items['answer']}")
```

### Excel Data Analysis

```python
# Process Excel file with data analysis
result = processor.process_excel("sales_data.xlsx")

# Store structured data
doc_id = db.add_document(
    file_name="sales_data.xlsx",
    file_type="excel",
    metadata=result['metadata']
)

# Convert to searchable text
chunks = rag.chunk_text(result['full_text'])
db.add_chunks_to_vector_db(doc_id, 
                            [c['content'] for c in chunks],
                            [c['metadata'] for c in chunks])

# Query the data
queries = [
    "What is the total revenue?",
    "Which product had the highest sales?",
    "Compare Q1 and Q2 performance"
]

for query in queries:
    context = db.semantic_search(query, top_k=3)
    response = rag.generate_answer(query, context, "English")
    print(f"\nQ: {query}")
    print(f"A: {response['answer']}")
```

### Document Comparison

```python
def compare_documents(doc_id1, doc_id2, aspect="main differences"):
    """Compare two documents"""
    
    # Get all chunks for both documents
    all_results = db.collection.get()
    
    doc1_chunks = [
        all_results['documents'][i] 
        for i, meta in enumerate(all_results['metadatas'])
        if f"doc_{doc_id1}_" in all_results['ids'][i]
    ]
    
    doc2_chunks = [
        all_results['documents'][i]
        for i, meta in enumerate(all_results['metadatas'])
        if f"doc_{doc_id2}_" in all_results['ids'][i]
    ]
    
    doc1_text = " ".join(doc1_chunks)
    doc2_text = " ".join(doc2_chunks)
    
    # Create comparison prompt
    comparison_context = [
        {"content": f"Document 1: {doc1_text[:5000]}"},
        {"content": f"Document 2: {doc2_text[:5000]}"}
    ]
    
    response = rag.generate_answer(
        query=f"Compare these documents focusing on: {aspect}",
        context_documents=comparison_context,
        language="English"
    )
    
    return response['answer']

# Usage
comparison = compare_documents(1, 2, "methodology and findings")
print(comparison)
```

### Export Chat History

```python
import json
from datetime import datetime

def export_chat_history(session_id, output_file="chat_export.json"):
    """Export chat history to JSON"""
    
    history = db.get_chat_history(session_id, limit=1000)
    
    export_data = {
        "session_id": session_id,
        "export_date": datetime.now().isoformat(),
        "total_messages": len(history),
        "conversations": history
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(history)} messages to {output_file}")

# Usage
export_chat_history("user-123", "chat_backup.json")
```

### Keyword-Based Document Search

```python
def search_by_keywords(keywords, top_k=10):
    """Search documents using multiple keywords"""
    
    results_by_keyword = {}
    
    for keyword in keywords:
        results = db.semantic_search(keyword, top_k=top_k)
        results_by_keyword[keyword] = results
    
    # Merge and rank results
    all_results = []
    for keyword, results in results_by_keyword.items():
        for result in results:
            result['keyword'] = keyword
            all_results.append(result)
    
    # Sort by relevance
    all_results.sort(key=lambda x: x.get('distance', 1))
    
    return all_results[:top_k]

# Usage
keywords = ["machine learning", "neural networks", "AI applications"]
results = search_by_keywords(keywords, top_k=5)

for result in results:
    print(f"\nKeyword: {result['keyword']}")
    print(f"File: {result['metadata'].get('file_name', 'Unknown')}")
    print(f"Content: {result['content'][:200]}...")
```

---

## Error Handling Best Practices

```python
from utils.helpers import log_error

def safe_document_processing(file_path, file_type):
    """Process document with comprehensive error handling"""
    
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file size
        if not FileValidator.is_valid_size(file_path, max_size_mb=200):
            raise ValueError("File too large (>200MB)")
        
        # Process document
        processor = DocumentProcessor()
        result = processor.process_document(file_path, file_type)
        
        # Validate result
        if not result.get('full_text'):
            raise ValueError("No text extracted from document")
        
        return {
            "success": True,
            "result": result,
            "error": None
        }
        
    except FileNotFoundError as e:
        log_error(e, "safe_document_processing")
        return {"success": False, "result": None, "error": str(e)}
    
    except ValueError as e:
        log_error(e, "safe_document_processing")
        return {"success": False, "result": None, "error": str(e)}
    
    except Exception as e:
        log_error(e, "safe_document_processing")
        return {"success": False, "result": None, 
                "error": f"Unexpected error: {str(e)}"}

# Usage
result = safe_document_processing("document.pdf", "pdf")

if result['success']:
    print("Processing successful!")
    print(result['result']['full_text'][:100])
else:
    print(f"Processing failed: {result['error']}")
```

---

## Performance Tips

### 1. Batch Processing
```python
# Process multiple queries efficiently
def batch_query(queries, top_k=5):
    results = {}
    
    for query in queries:
        results[query] = db.semantic_search(query, top_k=top_k)
    
    return results

queries = ["query1", "query2", "query3"]
all_results = batch_query(queries)
```

### 2. Caching Results
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query, top_k=5):
    """Cache search results"""
    return tuple(db.semantic_search(query, top_k=top_k))

# First call - database query
results1 = cached_search("machine learning")

# Second call - cached result
results2 = cached_search("machine learning")  # Much faster!
```

### 3. Async Processing
```python
import asyncio

async def process_document_async(file_path, file_type):
    """Async document processing"""
    loop = asyncio.get_event_loop()
    processor = DocumentProcessor()
    
    result = await loop.run_in_executor(
        None,
        processor.process_document,
        file_path,
        file_type
    )
    
    return result

# Usage
async def main():
    tasks = [
        process_document_async("doc1.pdf", "pdf"),
        process_document_async("doc2.pdf", "pdf"),
        process_document_async("doc3.pdf", "pdf")
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Run
results = asyncio.run(main())
```

---

## API Rate Limiting

```python
import time
from functools import wraps

def rate_limit(max_calls=10, period=60):
    """Rate limiting decorator"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls
            calls[:] = [c for c in calls if c > now - period]
            
            if len(calls) >= max_calls:
                sleep_time = period - (now - calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                calls.pop(0)
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

@rate_limit(max_calls=5, period=60)
def limited_rag_query(query):
    """Limited to 5 calls per minute"""
    context = db.semantic_search(query)
    return rag.generate_answer(query, context)
```

---

## Testing Your Integration

```python
def test_complete_pipeline():
    """Test the complete pipeline"""
    
    print("Testing Document Processor...")
    processor = DocumentProcessor()
    assert processor is not None
    
    print("Testing Database Manager...")
    db = DatabaseManager("test.db", "test_chromadb")
    doc_id = db.add_document("test.pdf", "pdf", {})
    assert doc_id > 0
    
    print("Testing RAG Engine...")
    rag = RAGEngine("test-key")
    chunks = rag.chunk_text("Test text")
    assert len(chunks) > 0
    
    print("Testing Translator...")
    translator = Translator()
    result = translator.detect_language("Hello")
    assert result in ['English', 'en']
    
    print("✓ All tests passed!")

# Run tests
test_complete_pipeline()
```

---

## Additional Resources

### Code Examples Repository
Find more examples at: `examples/` directory

### Community Contributions
Submit your examples via Pull Request

### API Updates
Check CHANGELOG.md for API changes

### Getting Help
- GitHub Issues for bugs
- GitHub Discussions for questions
- API Documentation updates: docs/

---

**API Documentation Version: 1.0**  
**Last Updated: October 2025**

For the latest documentation, visit: https://github.com/yourusername/ai-summarization-system