# 🚀 Quick Start Guide

Get up and running with the AI Summarization System in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 4GB+ RAM
- 10GB+ free disk space

## Installation (Method 1: Automated)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/ai-summarization-system.git
cd ai-summarization-system
```

### Step 2: Run Setup Script
```bash
python setup.py
```

The script will:
- Check system requirements
- Create necessary directories
- Install dependencies
- Download AI models
- Set up configuration

### Step 3: Start Application
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

## Installation (Method 2: Manual)

### Step 1: Create Virtual Environment
```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr ffmpeg
```

**macOS:**
```bash
brew install tesseract ffmpeg
```

**Windows:**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download FFmpeg: https://ffmpeg.org/download.html
- Add both to system PATH

### Step 4: Configure Environment
Create a `.env` file:
```bash
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-3.5-turbo
```

### Step 5: Create Directories
```bash
mkdir -p data/uploads data/processed data/databases/chromadb
```

### Step 6: Launch
```bash
streamlit run app.py
```

## First Use Tutorial

### 1. Upload Your First Document

1. Navigate to **📤 Upload Documents** in sidebar
2. Click **Browse files**
3. Select a PDF, Excel, or audio file
4. Click **🚀 Process Documents**
5. Wait for processing to complete

### 2. Chat with Your Document

1. Go to **💬 Chat** page
2. Type a question like:
   - "Summarize this document"
   - "What are the main points?"
   - "Extract key information"
3. Get AI-powered responses with source citations

### 3. Switch Languages

1. Use the sidebar language selector
2. Choose: English, Hindi, or Kannada
3. All responses will be in selected language

### 4. View History

1. Navigate to **📊 History & Analytics**
2. Review past conversations
3. View document library
4. Check usage statistics

## Example Use Cases

### Research Paper Analysis
```
1. Upload: research_paper.pdf
2. Ask: "What are the key findings?"
3. Ask: "Summarize the methodology"
4. Ask: "What are the limitations?"
```

### Financial Report Review
```
1. Upload: quarterly_report.xlsx
2. Ask: "What's the revenue trend?"
3. Ask: "Compare Q1 vs Q2 performance"
4. Ask: "Identify cost increases"
```

### Meeting Transcription
```
1. Upload: meeting_recording.mp3
2. Ask: "List all action items"
3. Ask: "Who made decisions?"
4. Ask: "Summarize key discussions"
```

### Multilingual Documents
```
1. Upload: english_manual.pdf
2. Switch to Hindi/Kannada
3. Ask questions in your language
4. Get translated responses
```

## Common Commands

### Start Application
```bash
streamlit run app.py
```

### Stop Application
Press `Ctrl+C` in terminal

### Clear Database
```bash
rm -rf data/databases/*
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### View Logs
```bash
tail -f ~/.streamlit/streamlit.log
```

## Troubleshooting

### "OpenAI API Key not found"
- Check `.env` file exists
- Verify API key is correct
- Restart application

### "Tesseract not found"
```bash
# Install Tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
# Windows: Download from official site
```

### "FFmpeg not found"
```bash
# Install FFmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
# Windows: Download from official site
```

### "Out of memory"
- Process smaller documents
- Reduce chunk size in config
- Close other applications

### "API rate limit exceeded"
- Check OpenAI usage dashboard
- Upgrade API plan
- Reduce frequency of requests

## Configuration Tips

### Use GPT-4 for Better Results
Edit `.env`:
```bash
LLM_MODEL=gpt-4
```

### Adjust Processing Settings
Edit `utils/config.py`:
```python
CHUNK_SIZE = 1500  # Larger chunks
CHUNK_OVERLAP = 300  # More overlap
TOP_K_RESULTS = 10  # More search results
```

### Change Upload Limits
Edit `utils/config.py`:
```python
MAX_FILE_SIZE = 500  # Increase to 500MB
```

## Best Practices

### Document Upload
- ✅ Use clear, high-quality scans
- ✅ Organize files by topic
- ✅ Name files descriptively
- ❌ Don't upload corrupted files
- ❌ Avoid extremely large files (>200MB)

### Asking Questions
- ✅ Be specific and clear
- ✅ One question at a time
- ✅ Use natural language
- ❌ Don't ask unrelated questions
- ❌ Avoid vague queries

### Language Selection
- ✅ Match document language when possible
- ✅ Switch languages for specific needs
- ✅ Use English for technical terms

### Performance
- ✅ Process documents during off-peak
- ✅ Keep database clean
- ✅ Clear old conversations
- ❌ Don't upload hundreds of files at once

## Next Steps

1. **Explore Features**: Try all document types
2. **Customize**: Adjust settings to your needs
3. **Integrate**: Use with your workflow
4. **Share**: Collaborate with team members

## Getting Help

- 📖 Read full documentation: `README.md`
- 🐛 Report issues: GitHub Issues
- 💬 Ask questions: GitHub Discussions
- 📧 Email support: support@yourdomain.com

## Useful Resources

- [LangChain Docs](https://python.langchain.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [RAG Tutorial](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## Video Tutorials

Coming soon:
- [ ] Installation walkthrough
- [ ] First document upload
- [ ] Advanced features
- [ ] Deployment guide

---

**Ready to get started?** Run `streamlit run app.py` and open `http://localhost:8501`

Happy analyzing! 🚀