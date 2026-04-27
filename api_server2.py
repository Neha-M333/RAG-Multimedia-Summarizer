"""
FastAPI Backend for GlassVault
Wraps existing backend components with REST API
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path
import uuid
import os

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from backend.document_processor import DocumentProcessor
from backend.database_manager import EnhancedDatabaseManager
from backend.rag_engine import AdvancedRAGEngine
from backend.local_llm import LocalRAGEngine
from backend.multimedia_processor import AdvancedMultimediaProcessor
from backend.translator import Translator
from utils.config import Config

# Initialize FastAPI
app = FastAPI(title="GlassVault API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
multimedia_processor = AdvancedMultimediaProcessor()
db_manager = EnhancedDatabaseManager(
    str(Config.db_config.sqlite_path),
    str(Config.db_config.chromadb_path)
)

# Initialize RAG Engine and Translator
if Config.USE_LOCAL_LLM:
    rag_engine = LocalRAGEngine(model=Config.OLLAMA_MODEL)
else:
    rag_engine = AdvancedRAGEngine(Config.OPENAI_API_KEY, Config.model_config.model_name)

# Initialize translator (works without API key using Google Translate)
translator = Translator(api_key=None)  # None = use Google Translate

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "English"
    top_k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: Optional[str] = None
    complexity: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    upload_date: str
    processed: bool

class SummaryRequest(BaseModel):
    document_id: int
    style: str = "executive"
    language: str = "English"
    target_length: int = 300

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "auto"

# Routes
@app.get("/")
async def root():
    return {
        "message": "GlassVault API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        docs = db_manager.get_all_documents()
        return {
            "status": "healthy",
            "database": "connected",
            "documents": len(docs),
            "llm_provider": "local" if Config.USE_LOCAL_LLM else "openai"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    generate_summary: bool = True,
    extract_keywords: bool = False
):
    """Upload and process a document"""
    try:
        # Save file temporarily
        file_path = Config.UPLOADS_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Detect file type
        file_ext = Path(file.filename).suffix.lower()
        file_type_map = {
            '.pdf': 'pdf',
            '.xlsx': 'excel', '.xls': 'excel', '.csv': 'excel',
            '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio',
            '.mp4': 'video', '.avi': 'video', '.mov': 'video'
        }
        
        file_type = file_type_map.get(file_ext, 'text')
        
        # Process document
        if file_type in ['audio', 'video']:
            if file_type == 'audio':
                result = multimedia_processor.process_audio_advanced(str(file_path))
            else:
                result = multimedia_processor.process_video_advanced(str(file_path))
        else:
            result = document_processor.process_document(str(file_path), file_type)
        
        # Add to database
        doc_id = db_manager.add_document(
            file_name=file.filename,
            file_type=file_type,
            metadata=result['metadata'],
            file_size=file.size
        )
        
        # Chunk and vectorize
        chunks = rag_engine.chunk_text_adaptive(
            result['full_text'],
            metadata={'file_name': file.filename, 'file_type': file_type}
        )
        
        db_manager.add_chunks_to_vector_db(
            doc_id,
            [c['content'] for c in chunks],
            [c['metadata'] for c in chunks]
        )
        
        db_manager.mark_document_processed(doc_id)
        
        # Generate summary if requested
        summary = None
        if generate_summary:
            summary_result = rag_engine.summarize_advanced(
                result['full_text'][:5000],
                style="executive",
                language="English",
                target_length=300
            )
            summary = summary_result['summary']
            db_manager.save_summary(doc_id, summary, "en")
        
        # Extract keywords if requested
        keywords = None
        if extract_keywords:
            keywords = rag_engine.extract_keywords(
                result['full_text'][:3000],
                num_keywords=10
            )
        
        # Clean up
        os.remove(file_path)
        
        return {
            "id": doc_id,
            "file_name": file.filename,
            "file_type": file_type,
            "chunks": len(chunks),
            "summary": summary,
            "keywords": keywords,
            "status": "processed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents():
    """Get all documents"""
    try:
        docs = db_manager.get_all_documents()
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}")
async def get_document(document_id: int):
    """Get document details"""
    try:
        doc = db_manager.get_document_with_chunks(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document"""
    try:
        success = db_manager.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"status": "deleted", "document_id": document_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with documents"""
    try:
        # Search for relevant documents
        relevant_docs = db_manager.semantic_search(
            request.message,
            top_k=request.top_k
        )
        
        if not relevant_docs:
            return ChatResponse(
                answer="I couldn't find relevant information in your documents.",
                sources=[],
                confidence="low"
            )
        
        # Generate answer
        response = rag_engine.generate_answer_advanced(
            query=request.message,
            context_documents=relevant_docs,
            language=request.language
        )
        
        # Save to database
        db_manager.save_chat_message(
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=response['answer'],
            language=request.language,
            source_documents=[{
                'content': s['content'][:200],
                'metadata': s.get('metadata', {})
            } for s in relevant_docs]
        )
        
        return ChatResponse(
            answer=response['answer'],
            sources=relevant_docs,
            confidence=response.get('confidence', 'medium'),
            complexity=response.get('complexity', 'moderate')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """Get chat history"""
    try:
        history = db_manager.get_chat_history(session_id, limit=limit)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize_document(request: SummaryRequest):
    """Generate document summary"""
    try:
        doc = db_manager.get_document_with_chunks(request.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        full_text = ' '.join([chunk['content'] for chunk in doc['chunks']])
        
        result = rag_engine.summarize_advanced(
            text=full_text,
            style=request.style,
            language=request.language,
            target_length=request.target_length
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    """Get system analytics"""
    try:
        analytics = db_manager.get_analytics_dashboard()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_text(request: TranslateRequest):
    """Translate text to target language"""
    try:
        if not translator:
            raise HTTPException(
                status_code=501, 
                detail="Translation not available with local LLM. Please use OpenAI."
            )
        
        result = translator.translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)