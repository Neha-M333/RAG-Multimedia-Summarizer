# Configuration Reference

All configuration is managed through the `.env` file in the project root.

---

## Full Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LOCAL_LLM` | `false` | Set `true` to use Ollama instead of OpenAI |
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `LLM_MODEL` | `gpt-4-turbo-preview` | Model name |
| `LLM_TEMPERATURE` | `0.7` | Response randomness (0 = deterministic, 1 = creative) |
| `MAX_TOKENS` | `2000` | Maximum tokens per response |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name (local LLM only) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `CHUNK_SIZE` | `1500` | Text chunk size for vectorization |
| `CHUNK_OVERLAP` | `300` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Number of search results returned per query |
| `MAX_FILE_SIZE_MB` | `200` | Maximum upload size |
| `SQLITE_DB_PATH` | `data/databases/structured.db` | SQLite database path |
| `CHROMADB_PATH` | `data/databases/chromadb` | ChromaDB storage path |
| `DB_POOL_SIZE` | `5` | Database connection pool size |
| `ENABLE_CACHING` | `true` | Enable query result caching |
| `CACHE_TTL` | `3600` | Cache time-to-live in seconds |
| `WORKER_THREADS` | `4` | Parallel processing threads |
| `ENABLE_OCR` | `true` | Enable Tesseract OCR |
| `ENABLE_AUDIO_TRANSCRIPTION` | `true` | Enable Whisper transcription |
| `ENABLE_VIDEO_PROCESSING` | `true` | Enable video analysis |
| `WHISPER_MODEL_SIZE` | `base` | Whisper model: `tiny`, `base`, `small`, `medium`, `large` |

---

## Tuning for Performance

**Low memory / slow machine:**
```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
WHISPER_MODEL_SIZE=tiny
USE_LOCAL_LLM=false
```

**High throughput / production:**
```env
DB_POOL_SIZE=10
ENABLE_CACHING=true
CACHE_TTL=7200
WORKER_THREADS=8
```

---

## Advanced: Custom Processing Strategy

You can define a custom strategy in code:

```python
from backend.advanced_rag_engine import ProcessingStrategy

custom_strategy = ProcessingStrategy(
    chunk_size=2000,
    chunk_overlap=400,
    temperature=0.8,
    max_tokens=1500,
    use_reasoning_chain=True
)
```

---

→ Next: [Usage Guide](usage-guide.md)
