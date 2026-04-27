# Troubleshooting

## FFmpeg not found

```bash
# Verify
ffmpeg -version

# Add to PATH if installed but not found
export PATH=$PATH:/usr/local/bin
```

---

## Tesseract OCR errors

```bash
# Verify installation
tesseract --version

# Install all language packs
apt-get install tesseract-ocr-all
```

---

## Out of memory errors

Reduce memory usage by lowering chunk size and using a smaller Whisper model:

```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
WHISPER_MODEL_SIZE=tiny
```

---

## Slow performance

```env
# Enable caching
ENABLE_CACHING=true

# Increase connection pool
DB_POOL_SIZE=10

# Switch to local LLM to avoid network latency
USE_LOCAL_LLM=true
```

---

## ChromaDB collection errors

Delete and reinitialize the ChromaDB directory:

```bash
rm -rf data/databases/chromadb
mkdir -p data/databases/chromadb
```

---

## OpenAI API errors

- Check that `OPENAI_API_KEY` is set correctly in `.env`
- Verify the model name — `gpt-4-turbo-preview` requires GPT-4 API access
- Check your OpenAI usage quota at https://platform.openai.com/usage

---

## Still stuck?

Open an issue on GitHub with:
- Your OS and Python version (`python --version`)
- The full error traceback
- Your `.env` settings (redact the API key)
