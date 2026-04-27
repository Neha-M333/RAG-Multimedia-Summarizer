# API Reference

## AdvancedRAGEngine

`from backend.advanced_rag_engine import AdvancedRAGEngine`

---

### `analyze_query_complexity(query)`

Determines how complex a query is so the engine can adapt its processing strategy.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's question |

**Returns:** `QueryComplexity` enum — one of `SIMPLE`, `MODERATE`, `COMPLEX`, `EXPERT`

---

### `generate_answer_advanced(query, context_documents, language, use_chain_of_thought)`

Generates a validated, cited answer to a question using retrieved document chunks.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | User question |
| `context_documents` | `List[Dict]` | Retrieved chunks from `semantic_search` |
| `language` | `str` | Response language (e.g. `"English"`, `"Hindi"`) |
| `use_chain_of_thought` | `bool` | Enable step-by-step reasoning (recommended for complex queries) |

**Returns:** `Dict` with keys:
- `answer` — the generated response
- `confidence` — float 0–1
- `complexity` — detected query complexity
- `tokens_used` — token count
- `cost` — estimated cost in USD

---

### `summarize_advanced(text, style, language, target_length, include_metadata)`

Generates a summary in the chosen style.

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Source text to summarize |
| `style` | `str` | `executive`, `technical`, `academic`, `bullet`, `narrative` |
| `language` | `str` | Output language |
| `target_length` | `int` | Desired word count |
| `include_metadata` | `bool` | Append compression ratio and quality metrics |

**Returns:** `Dict` with keys: `summary`, `metadata`, `compression_ratio`, `cost`

---

### `validate_answer(query, answer, sources)`

Self-validates the generated answer against its source documents.

**Returns:** `Dict` with `is_valid`, `confidence`, `issues`

---

### `explain_reasoning(query, answer, sources)`

Returns a step-by-step explanation of how the answer was derived.

---

### `multi_document_synthesis(documents, query, language)`

Cross-analyzes multiple documents and synthesizes a unified response.

**Returns:** `Dict` with `synthesis`, `common_themes`, `differences`

---

## EnhancedDatabaseManager

`from backend.enhanced_db_manager import EnhancedDatabaseManager`

---

### `semantic_search(query, top_k, filter_metadata, use_cache)`

Runs a vector similarity search over all stored document chunks.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query |
| `top_k` | `int` | Number of results to return |
| `filter_metadata` | `Dict` | Optional metadata filters |
| `use_cache` | `bool` | Return cached result if available |

**Returns:** `List[Dict]` — each item has `content`, `score`, `metadata`, `doc_id`

---

### `add_document(file_name, file_type, metadata)`

Stores document metadata in SQLite.

**Returns:** `str` — the new document ID

---

### `add_chunks_to_vector_db(doc_id, chunks, metadata_list)`

Vectorizes and stores text chunks in ChromaDB.

---

### `get_analytics_dashboard()`

Returns comprehensive usage analytics.

**Returns:** `Dict` with:
- `documents.total` — document count
- `chat.total_messages` — total chat messages
- `chat.total_cost` — cumulative API cost
- `performance.cache_hit_rate` — cache efficiency
- `usage_trends` — day-by-day usage data

---

### `optimize_database()`

Runs VACUUM and index optimization on SQLite.

---

### `export_data(format)`

Exports all data. `format` is `"json"` or `"csv"`.

---

## AdvancedMultimediaProcessor

`from backend.multimedia_processor import AdvancedMultimediaProcessor`

---

### `process_audio_advanced(file_path, language, enable_diarization)`

Transcribes audio using Whisper.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `str` | Path to audio file |
| `language` | `str` | Language code (e.g. `"en"`) or `None` for auto-detect |
| `enable_diarization` | `bool` | Identify individual speakers |

**Returns:** `Dict` with `segments`, `full_text`, `summary`, `key_topics`

---

### `process_video_advanced(file_path, extract_audio, detect_scenes, extract_text)`

Full video analysis pipeline.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `str` | Path to video file |
| `extract_audio` | `bool` | Transcribe audio track |
| `detect_scenes` | `bool` | Detect scene changes |
| `extract_text` | `bool` | OCR text from frames |

**Returns:** `Dict` with `audio_content`, `scenes`, `visual_content`, `summary`

---

### `create_multimedia_summary_report(results, format)`

Generates a human-readable report from video/audio analysis results.

`format` is `"markdown"` or `"text"`.
