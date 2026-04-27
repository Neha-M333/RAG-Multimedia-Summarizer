"""
FastAPI Backend to Bridge React Frontend with Streamlit Backend
Provides REST API endpoints for all backend functionality
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys
import asyncio
import uuid
import logging

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from backend.rag_engine import AdvancedRAGEngine
from backend.database_manager import EnhancedDatabaseManager
from backend.document_processor import DocumentProcessor
from backend.multimedia_processor import AdvancedMultimediaProcessor
from backend.video_integration import DocumentVideoGenerator
from utils.config import Config

# Initialize FastAPI
app = FastAPI(
    title="AI Document Intelligence API",
    description="REST API for document processing, RAG, and video generation",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Backend Components
logger = logging.getLogger(__name__)

class BackendServices:
    """Singleton for backend services"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize all backend components"""
        try:
            self.document_processor = DocumentProcessor()
            self.multimedia_processor = AdvancedMultimediaProcessor()
            
            self.db_manager = EnhancedDatabaseManager(
                str(Config.db_config.sqlite_path),
                str(Config.db_config.chromadb_path)
            )
            
            if Config.USE_LOCAL_LLM:
                from backend.local_llm import LocalRAGEngine
                self.rag_engine = LocalRAGEngine(model=Config.OLLAMA_MODEL)
                logger.info("Using Local LLM (Ollama)")
            else:
                api_key = Config.OPENAI_API_KEY
                if not api_key or api_key.startswith('sk-your'):
                    raise ValueError("OpenAI API key not configured")
                self.rag_engine = AdvancedRAGEngine(api_key, Config.model_config.model_name)
                logger.info("Using OpenAI API")
            
            self.video_generator = DocumentVideoGenerator()
            
            logger.info("✅ Backend services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Backend initialization failed: {e}")
            raise

# Initialize services
try:
    services = BackendServices()
except Exception as e:
    logger.error(f"Failed to initialize backend: {e}")
    services = None

# ============= Pydantic Models =============

class ChatMessage(BaseModel):
    query: str
    language: str = "English"
    top_k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: str
    complexity: str
    tokens_used: int
    cost: float

class SummaryRequest(BaseModel):
    text: str
    style: str = "executive"
    language: str = "English"
    target_length: int = 300

class VideoGenerationRequest(BaseModel):
    document_id: int
    language: str = "english"
    target_duration: int = 60
    include_subtitles: bool = True

class DocumentUploadResponse(BaseModel):
    document_id: int
    file_name: str
    file_type: str
    chunks_created: int
    processing_time: float
    summary: Optional[str] = None

# ============= Health Check =============

@app.get("/api/health")
async def health_check():
    """Check if backend services are running"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend services not initialized")
    
    return {
        "status": "healthy",
        "backend": "operational",
        "llm_provider": "local" if Config.USE_LOCAL_LLM else "openai",
        "model": Config.model_config.model_name,
        "database": "connected"
    }

# ============= Document Upload & Processing =============

@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    generate_summary: bool = True,
    summary_style: str = "executive",
    language: str = "English"
):
    """Upload and process a document"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        # Save uploaded file
        temp_path = Config.UPLOADS_DIR / file.filename
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Detect file type
        file_ext = Path(file.filename).suffix.lower()
        file_type_mapping = {
            '.pdf': 'pdf', '.docx': 'word', '.doc': 'word',
            '.pptx': 'powerpoint', '.ppt': 'powerpoint',
            '.xlsx': 'excel', '.xls': 'excel', '.csv': 'excel',
            '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio',
            '.mp4': 'video', '.avi': 'video', '.mov': 'video',
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image'
        }
        
        file_type = file_type_mapping.get(file_ext)
        if not file_type:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        # Process document
        import time
        start_time = time.time()
        
        result = services.document_processor.process_document(str(temp_path), file_type)
        
        # Add to database
        doc_id = services.db_manager.add_document(
            file.filename,
            file_type,
            result['metadata'],
            file_size=len(content)
        )
        
        # Chunk text
        chunks = services.rag_engine.chunk_text_adaptive(
            result['full_text'],
            metadata={'file_name': file.filename, 'file_type': file_type}
        )
        
        # Add to vector DB
        services.db_manager.add_chunks_to_vector_db(
            doc_id,
            [c['content'] for c in chunks],
            [c['metadata'] for c in chunks]
        )
        
        # Generate summary if requested
        summary = None
        if generate_summary:
            summary_result = services.rag_engine.summarize_advanced(
                result['full_text'],
                style=summary_style,
                language=language,
                target_length=300
            )
            summary = summary_result['summary']
            services.db_manager.save_summary(doc_id, summary, language[:2])
        
        processing_time = time.time() - start_time
        
        # Cleanup
        temp_path.unlink()
        
        return DocumentUploadResponse(
            document_id=doc_id,
            file_name=file.filename,
            file_type=file_type,
            chunks_created=len(chunks),
            processing_time=processing_time,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Chat/Query =============

@app.post("/api/chat/query", response_model=ChatResponse)
async def chat_query(message: ChatMessage):
    """Query documents via chat interface"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        # Semantic search
        relevant_docs = services.db_manager.semantic_search(
            message.query, 
            top_k=message.top_k
        )
        
        if not relevant_docs:
            return ChatResponse(
                answer="I couldn't find relevant information in the documents.",
                sources=[],
                confidence="low",
                complexity="simple",
                tokens_used=0,
                cost=0.0
            )
        
        # Generate answer
        response = services.rag_engine.generate_answer_advanced(
            query=message.query,
            context_documents=relevant_docs,
            language=message.language
        )
        
        # Save to database
        services.db_manager.save_chat_message(
            session_id=str(uuid.uuid4()),
            user_message=message.query,
            assistant_message=response['answer'],
            language=message.language,
            source_documents=[{
                'content': s['content'][:200],
                'metadata': s.get('metadata', {})
            } for s in relevant_docs]
        )
        
        return ChatResponse(
            answer=response['answer'],
            sources=relevant_docs,
            confidence=response.get('confidence', 'medium'),
            complexity=response.get('complexity', 'moderate'),
            tokens_used=response.get('tokens_used', 0),
            cost=response.get('cost', 0.0)
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Video Generation =============

@app.post("/api/video/generate")
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate animated video from document summary"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        # Get document summary
        doc = services.db_manager.get_document_with_chunks(request.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        summary_data = services.db_manager.get_summary(request.document_id)
        if not summary_data:
            # Generate summary if not exists
            full_text = ' '.join([c['content'] for c in doc['chunks'][:10]])
            summary_result = services.rag_engine.summarize_advanced(
                full_text,
                style="executive",
                language=request.language.capitalize(),
                target_length=300
            )
            summary_text = summary_result['summary']
        else:
            summary_text = summary_data['summary']
        
        # Generate video asynchronously
        job_id = str(uuid.uuid4())[:8]
        
        async def generate_video_task():
            result = await services.video_generator.generate_video_from_summary(
                summary_text=summary_text,
                language=request.language,
                target_duration=request.target_duration,
                include_subtitles=request.include_subtitles,
                document_name=doc['file_name']
            )
            return result
        
        # Start generation in background
        loop = asyncio.get_event_loop()
        video_result = await loop.create_task(generate_video_task())
        
        if not video_result["success"]:
            raise HTTPException(status_code=500, detail=video_result.get("error"))
        
        return {
            "success": True,
            "job_id": job_id,
            "video_path": video_result["video_path"],
            "duration": video_result["duration"],
            "file_size": video_result["file_size"],
            "language": video_result["language"]
        }
        
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Document Management =============

@app.get("/api/documents")
async def list_documents():
    """Get all uploaded documents"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        docs = services.db_manager.get_all_documents()
        return {"documents": docs, "count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{document_id}")
async def get_document(document_id: int):
    """Get document details with chunks"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        doc = services.db_manager.get_document_with_chunks(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        success = services.db_manager.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"success": True, "message": "Document deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= Chat History =============

@app.get("/api/chat/history")
async def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 50
):
    """Get chat history"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        if not session_id:
            session_id = "default"
        
        history = services.db_manager.get_chat_history(session_id, limit=limit)
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= Analytics =============

@app.get("/api/analytics")
async def get_analytics():
    """Get system analytics"""
    if services is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    try:
        analytics = services.db_manager.get_analytics_dashboard()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= Serve React Frontend =============

# Mount React build directory (after building frontend)
app.mount("/", StaticFiles(directory="dist", html=True), name="frontend")

# ============= Run Server =============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )