"""
FastAPI Backend Server - FIXED: Summary display and subtitle control
Key Fixes:
1. ✅ Returns summary text in response immediately
2. ✅ Respects include_subtitles parameter
3. ✅ Properly saves summary to database
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import sys
from pathlib import Path
import uuid
from fastapi.responses import StreamingResponse
import mimetypes

sys.path.append(str(Path(__file__).parent))

from backend.document_processor import DocumentProcessor
from backend.database_manager import EnhancedDatabaseManager
from backend.rag_engine import AdvancedRAGEngine
from backend.local_llm import LocalRAGEngine
from backend.multimedia_processor import AdvancedMultimediaProcessor
from backend.video_integration import DocumentVideoGenerator
from utils.config import Config

app = FastAPI(
    title="AI Document Intelligence API",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

if Config.USE_LOCAL_LLM:
    rag_engine = LocalRAGEngine(model=Config.OLLAMA_MODEL)
    print("✅ Using Local LLM (Ollama)")
else:
    rag_engine = AdvancedRAGEngine(Config.OPENAI_API_KEY, Config.model_config.model_name)
    print("✅ Using OpenAI API")

video_generator = DocumentVideoGenerator()

@app.get("/api/health")
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "llm_provider": "local" if Config.USE_LOCAL_LLM else "openai",
        "model": Config.OLLAMA_MODEL if Config.USE_LOCAL_LLM else Config.model_config.model_name,
        "documents_count": len(db_manager.get_all_documents()),
    }

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    generate_summary: bool = Form(True),
    summary_style: str = Form("executive"),
    language: str = Form("english"),
    generate_video: bool = Form(False),
    include_subtitles: bool = Form(False),  # ADDED
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload and process a document
    FIXED: Better video generation tracking and error handling
    """
    try:
        print(f"\n{'='*70}")
        print(f"📤 UPLOAD REQUEST")
        print(f"{'='*70}")
        print(f"File: {file.filename}")
        print(f"Language: {language}")
        print(f"Generate Video: {generate_video}")
        print(f"Include Subtitles: {include_subtitles}")
        
        # Ensure upload directory exists
        Config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        file_path = Config.UPLOADS_DIR / file.filename
        
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Determine file type
        file_ext = Path(file.filename).suffix.lower()
        file_type_mapping = {
            '.pdf': 'pdf',
            '.docx': 'word', '.doc': 'word',
            '.pptx': 'powerpoint', '.ppt': 'powerpoint',
            '.xlsx': 'excel', '.xls': 'excel', '.csv': 'excel',
            '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio',
            '.mp4': 'video', '.avi': 'video', '.mov': 'video',
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image',
            '.txt': 'text', '.md': 'text'
        }
        
        file_type = file_type_mapping.get(file_ext)
        if not file_type:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        # Process document
        result = document_processor.process_document(str(file_path), file_type)
        
        # Add to database
        doc_id = db_manager.add_document(
            file_name=file.filename,
            file_type=file_type,
            metadata=result['metadata'],
            file_size=file_path.stat().st_size
        )
        
        print(f"✅ Document added: ID={doc_id}")
        
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
        
        # Generate summary if requested
        summary = None
        if generate_summary:
            language_map = {"english": "English", "hindi": "Hindi", "kannada": "Kannada"}
            summary_result = rag_engine.summarize_advanced(
                result['full_text'],
                style=summary_style,
                language=language_map.get(language, "English"),
                target_length=300
            )
            summary = summary_result['summary']
            db_manager.save_summary(doc_id, summary, language[:2])
            
            print(f"✅ Summary generated: {len(summary)} chars in {language}")
        
        # Generate video in background if requested
        video_info = None
        if generate_video and summary:
            print(f"\n🎬 Starting video generation in background...")
            video_info = {
                "status": "processing",
                "message": f"Video generation started in background for {language}",
                "language": language,
                "include_subtitles": include_subtitles
            }
            
            background_tasks.add_task(
                generate_video_background,
                summary, 
                language, 
                file.filename, 
                doc_id,
                include_subtitles,  # Pass subtitle setting
                db_manager
            )
        
        # Cleanup uploaded file
        if file_path.exists():
            file_path.unlink()
        
        return {
            "success": True,
            "document_id": doc_id,
            "file_name": file.filename,
            "file_type": file_type,
            "chunks_count": len(chunks),
            "summary": summary,
            "video_info": video_info,
            "message": "File uploaded and processed successfully"
        }
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



async def generate_video_background(
    summary: str, 
    language: str, 
    filename: str, 
    doc_id: int,
    include_subtitles: bool,
    db_manager
):
    """
    Background task for video generation with ROBUST error handling
    """
    try:
        print(f"\n🎬 Background video generation started")
        print(f"   Doc ID: {doc_id}")
        print(f"   Language: {language}")
        print(f"   Subtitles: {include_subtitles}")
        
        result = await video_generator.generate_video_from_summary(
            summary_text=summary,
            language=language,
            target_duration=60,
            document_name=Path(filename).stem,
            document_id=doc_id,
            include_subtitles=include_subtitles
        )
        
        if result["success"]:
            print(f"✅ Video generated for document {doc_id}")
            print(f"   Video name: {result['video_name']}")
            print(f"   Size: {result['file_size'] / (1024*1024):.2f} MB")
            
            # OPTIONAL: Save video info to database
            # This helps track which videos exist
            # db_manager.log_video_generation(doc_id, language, ...)
            
        else:
            print(f"❌ Video generation failed for document {doc_id}")
            print(f"   Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Background video generation exception: {e}")
        import traceback
        traceback.print_exc()


# ============== CHAT ENDPOINTS ==============
class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "English"
    top_k: int = 5

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with documents using RAG"""
    try:
        relevant_docs = db_manager.semantic_search(request.message, top_k=request.top_k)
        
        if not relevant_docs:
            return {
                "success": True,
                "answer": "I couldn't find relevant information in your documents.",
                "sources": [],
                "session_id": request.session_id,
                "metadata": {"confidence": "low"}
            }
        
        response = rag_engine.generate_answer_advanced(
            query=request.message,
            context_documents=relevant_docs,
            language=request.language
        )
        
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
        
        return {
            "success": True,
            "answer": response['answer'],
            "sources": relevant_docs,
            "session_id": request.session_id,
            "metadata": {
                "complexity": response.get('complexity', 'moderate'),
                "confidence": response.get('confidence', 'medium'),
                "tokens_used": response.get('tokens_used', 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== DOCUMENT ENDPOINTS ==============
@app.get("/api/documents")
async def get_documents():
    """Get all documents"""
    try:
        docs = db_manager.get_all_documents()
        return {"success": True, "documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document"""
    try:
        success = db_manager.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"success": True, "message": "Document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== SUMMARY ENDPOINTS ==============
@app.get("/api/summaries/all")
async def get_all_summaries():
    """
    Get all summaries with their associated documents and videos
    FIXED: Properly matches videos to documents by checking multiple patterns
    """
    try:
        docs = db_manager.get_all_documents()
        summaries = []
        
        # Get all video files
        video_files = list(Config.VIDEO_DIR.glob("*.mp4"))
        print(f"📁 Found {len(video_files)} video files in {Config.VIDEO_DIR}")
        
        for doc in docs:
            # Get summary
            summary_data = db_manager.get_summary(doc['id'])
            
            # FIXED: Better video matching logic
            video_name = None
            
            # Try multiple matching patterns
            patterns_to_try = [
                f"doc{doc['id']}_*.mp4",  # doc123_english_abc123.mp4
                f"*{doc['id']}_*.mp4",    # anything with doc ID
                f"{Path(doc['file_name']).stem}_*.mp4",  # filename_english_abc123.mp4
            ]
            
            for pattern in patterns_to_try:
                matches = list(Config.VIDEO_DIR.glob(pattern))
                if matches:
                    # Prefer language-specific videos
                    if summary_data and summary_data.get('language'):
                        lang = summary_data['language']
                        lang_matches = [m for m in matches if f"_{lang}_" in m.name or f"_{lang}." in m.name]
                        if lang_matches:
                            video_name = lang_matches[0].name
                            break
                    # Otherwise take any match
                    video_name = matches[0].name
                    break
            
            if video_name:
                print(f"✅ Video found for doc {doc['id']}: {video_name}")
            else:
                print(f"⚠️ No video for doc {doc['id']} ({doc['file_name']})")
            
            summaries.append({
                "document_id": doc['id'],
                "document_name": doc['file_name'],
                "file_type": doc['file_type'],
                "upload_date": doc['upload_date'],
                "summary": summary_data,
                "video_name": video_name,  # Filename only
                "video_url": f"/api/videos/{video_name}" if video_name else None,  # Full URL
                "has_video": video_name is not None
            })
        
        print(f"📊 Total summaries: {len(summaries)}")
        print(f"📊 With videos: {sum(1 for s in summaries if s['has_video'])}")
        
        return {
            "success": True,
            "summaries": summaries,
            "total": len(summaries),
            "with_videos": sum(1 for s in summaries if s["has_video"])
        }
        
    except Exception as e:
        print(f"❌ Error in get_all_summaries: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



# ============== VIDEO ENDPOINTS ==============
@app.get("/api/videos")
async def list_videos():
    """List all generated videos"""
    try:
        video_dir = Config.VIDEO_DIR
        videos = []
        if video_dir.exists():
            for video_file in video_dir.glob("*.mp4"):
                videos.append({
                    "name": video_file.name,
                    "size": video_file.stat().st_size,
                    "created": video_file.stat().st_ctime
                })
        return {"success": True, "videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos/{video_name}")
async def stream_video(video_name: str):
    """
    Stream video file with proper headers
    FIXED: Better error handling and logging
    """
    try:
        video_path = Config.VIDEO_DIR / video_name
        
        print(f"📹 Video request: {video_name}")
        print(f"   Path: {video_path}")
        print(f"   Exists: {video_path.exists()}")
        
        if not video_path.exists():
            print(f"❌ Video not found: {video_path}")
            raise HTTPException(status_code=404, detail=f"Video not found: {video_name}")
        
        # Get file size
        file_size = video_path.stat().st_size
        print(f"   Size: {file_size / (1024*1024):.2f} MB")
        
        # Open file and return streaming response
        def iterfile():
            with open(video_path, mode="rb") as file:
                yield from file
        
        return StreamingResponse(
            iterfile(),
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Disposition": f'inline; filename="{video_name}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error streaming video: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )