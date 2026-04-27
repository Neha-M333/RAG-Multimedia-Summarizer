"""
Enhanced AI Document Intelligence System - Main Application
Professional-grade UI with advanced features
Version: 2.0.0
"""
import streamlit as st
import os
import sys
from pathlib import Path
import uuid
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import logging
import hashlib

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Import backend components with correct names
from backend.rag_engine import AdvancedRAGEngine, QueryComplexity, ProcessingStrategy
from backend.database_manager import EnhancedDatabaseManager
from backend.multimedia_processor import AdvancedMultimediaProcessor
from backend.document_processor import DocumentProcessor
from utils.config import EnhancedConfig as Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Document Intelligence Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.example.com',
        'Report a bug': 'https://github.com/example/issues',
        'About': '# AI Document Intelligence System v2.0'
    }
)

# Modern CSS styling
st.markdown("""
<style>
    /* Main theme */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1E88E5, #42A5F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 0.5rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 10px;
        padding: 1.5rem;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Progress and stats */
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'current_language' not in st.session_state:
        st.session_state.current_language = 'English'
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'processed_docs' not in st.session_state:
        st.session_state.processed_docs = []
    if 'chat_analytics' not in st.session_state:
        st.session_state.chat_analytics = {
            'total_queries': 0,
            'avg_confidence': 0,
            'total_tokens': 0,
            'total_cost': 0
        }

init_session_state()

# Initialize components with error handling
@st.cache_resource
def init_components():
    """Initialize all system components"""
    try:
        # Initialize processors
        document_processor = DocumentProcessor()
        multimedia_processor = AdvancedMultimediaProcessor()
        
        # Initialize database
        db_manager = EnhancedDatabaseManager(
            str(Config.BASE_DIR / "data" / "databases" / "structured.db"),
            str(Config.BASE_DIR / "data" / "databases" / "chromadb")
        )
        
        # Initialize RAG Engine
        if Config.USE_LOCAL_LLM:
            from backend.local_llm import LocalRAGEngine
            rag_engine = LocalRAGEngine()
            st.sidebar.success("🖥️ Using Local LLM (Ollama)")
        else:
            api_key = Config.OPENAI_API_KEY
            if not api_key or api_key.startswith('sk-your'):
                st.error("❌ OpenAI API key not configured. Please check .env file.")
                return None, None, None, None
            
            rag_engine = AdvancedRAGEngine(api_key, Config.model_config.model_name)
            st.sidebar.success("☁️ Using OpenAI API")
        
        return document_processor, multimedia_processor, db_manager, rag_engine
        
    except Exception as e:
        st.error(f"❌ System initialization failed: {str(e)}")
        logger.error(f"Initialization error: {str(e)}", exc_info=True)
        return None, None, None, None

document_processor, multimedia_processor, db_manager, rag_engine = init_components()

# Sidebar
with st.sidebar:
    st.markdown("## 🧠 AI Document Intelligence")
    st.markdown("---")
    
    # Language selector
    st.session_state.current_language = st.selectbox(
        "🌐 Interface Language",
        list(Config.LANGUAGES.keys()),
        index=list(Config.LANGUAGES.keys()).index(st.session_state.current_language)
    )
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📋 Navigation")
    page = st.radio(
        "Navigation Menu    ",
        [
            "🏠 Home Dashboard",
            "📤 Upload & Process",
            "💬 Intelligent Chat",
            "📊 Analytics & Insights",
            "🎯 Advanced Features"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats
    if db_manager:
        st.markdown("### 📈 Quick Stats")
        
        try:
            docs = db_manager.get_all_documents()
            history = db_manager.get_chat_history(st.session_state.session_id)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📄 Documents", len(docs))
            with col2:
                st.metric("💬 Chats", len(history))
            
            # System status
            st.markdown("### ⚡ System Status")
            stats = db_manager.get_statistics()
            
            cache_hit_rate = stats['cache_stats']['hit_rate'] * 100 if stats['cache_stats']['hit_rate'] else 0
            st.progress(min(cache_hit_rate / 100, 1.0))
            st.caption(f"Cache Hit Rate: {cache_hit_rate:.1f}%")
        except Exception as e:
            st.warning(f"⚠️ Stats unavailable: {str(e)}")
    
    st.markdown("---")
    
    # Support formats
    st.markdown("### 📁 Supported Formats")
    st.markdown("""
                #### Documents
            - 📄 **PDF** (.pdf)
            - 📝 **Word** (.docx, .doc)
            - 📊 **PowerPoint** (.pptx, .ppt)
            - 📋 **Excel/CSV** (.xlsx, .xls, .csv)
            - 📑 **Rich Text** (.rtf)

            #### Code & Data
            - 💻 **Source Code** (.py, .js, .java, .cpp, .c, .cs, .php, .rb, .go, .rs, .swift)
            - 📊 **JSON** (.json) 
            - 🔖 **XML** (.xml) 
            - 📘 **Markdown** (.md, .markdown) 

            #### Media
            - 🎵 **Audio** (.mp3, .wav, .m4a, .flac, .ogg, .aac) 
            - 🎬 **Video** (.mp4, .avi, .mov, .mkv, .flv, .wmv) 
            - 🖼️ **Images** (.jpg, .png, .gif, .bmp, .tiff, .webp)

            #### Web & E-books
            - 🌐 **HTML** (.html, .htm) 
            - 📚 **EPUB** (.epub) 
            - 📄 **Text** (.txt, .log) 
    """)

# Main content area
if page == "🏠 Home Dashboard":
    st.markdown('<div class="main-header">🧠 AI Document Intelligence System</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Professional-grade AI platform for document processing and intelligent analysis</div>', 
                unsafe_allow_html=True)
    
    # Hero section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🚀 Advanced Processing</h3>
            <p>Multi-format document processing with OCR, audio transcription, and video analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 Smart AI</h3>
            <p>Context-aware responses with chain-of-thought reasoning and confidence scoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🌍 Multilingual</h3>
            <p>Full support for multiple languages with real-time translation capabilities</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System capabilities
    st.markdown("## 🎯 System Capabilities")
    
    tab1, tab2, tab3 = st.tabs(["📄 Document Processing", "💡 AI Features", "📊 Analytics"])
    
    with tab1:
        st.markdown("""
        ### Multi-Format Processing
        
        **PDF Documents**
        - Text extraction with automatic OCR fallback
        - Table and image detection
        - Multi-page handling with page-level metadata
        
        **Spreadsheets & Data**
        - Excel, CSV parsing with structure preservation
        - Automatic data type detection
        - Statistical summaries generation
        
        **Audio & Video**
        - High-accuracy speech transcription
        - Scene detection and key frame extraction
        - Visual text recognition (OCR from video)
        
        **Images**
        - Advanced OCR with multiple languages
        - Layout analysis and structure preservation
        """)
    
    with tab2:
        st.markdown("""
        ### Advanced AI Capabilities
        
        **Query Processing**
        - Automatic complexity detection
        - Adaptive response strategies
        - Chain-of-thought reasoning for complex queries
        - Confidence scoring and validation
        
        **Summarization**
        - Multiple styles: Executive, Technical, Academic, Bullet Points
        - Hierarchical summarization for long documents
        - Multi-document synthesis
        - Audio/Video content summaries
        
        **Context Understanding**
        - Semantic search with relevance scoring
        - Cross-document reasoning
        - Source attribution and citation
        - Follow-up question generation
        """)
    
    with tab3:
        if db_manager:
            try:
                analytics = db_manager.get_analytics_dashboard()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Documents",
                        analytics['documents']['total'],
                        f"{analytics['documents']['total_size_mb']:.1f} MB"
                    )
                
                with col2:
                    st.metric(
                        "Total Chats",
                        analytics['chat']['total_messages'],
                        f"${analytics['chat']['total_cost']:.2f} cost"
                    )
                
                with col3:
                    st.metric(
                        "Avg Response Time",
                        f"{analytics['chat']['avg_response_time']:.2f}s"
                    )
                
                with col4:
                    cache_rate = analytics['performance']['cache_hit_rate'] * 100
                    st.metric(
                        "Cache Hit Rate",
                        f"{cache_rate:.1f}%"
                    )
            except Exception as e:
                st.warning(f"Analytics temporarily unavailable: {str(e)}")
    
    # Quick start guide
    with st.expander("🚀 Quick Start Guide", expanded=False):
        st.markdown("""
        ### Getting Started in 3 Steps
        
        **Step 1: Upload Documents** 📤
        - Navigate to "Upload & Process"
        - Select your files (PDF, Excel, Audio, Video)
        - Click "Process Documents" and wait for analysis
        
        **Step 2: Ask Questions** 💬
        - Go to "Intelligent Chat"
        - Ask questions about your documents
        - Get AI-powered answers with source citations
        
        **Step 3: Explore Insights** 📊
        - Check "Analytics & Insights" for usage stats
        - View document summaries and key topics
        - Export data and chat history
        """)

elif page == "📤 Upload & Process":
    st.markdown('<div class="main-header">📤 Upload & Process Documents</div>', 
                unsafe_allow_html=True)
    
    if not all([document_processor, multimedia_processor, db_manager, rag_engine]):
        st.error("❌ System components not initialized. Please check configuration.")
        st.stop()
    
    # File uploader
    st.markdown("### 📁 Select Files")
    uploaded_files = st.file_uploader(
    "Drag and drop files here or click to browse",
    type=[
        # Documents
        'pdf', 'docx', 'doc', 'pptx', 'ppt', 'rtf',
        # Spreadsheets & Data
        'xlsx', 'xls', 'csv', #'json', 'xml',
        # Web & Text
        'html', 'htm', 'md', 'txt', 'log',
        # Audio
        'mp3',
        # Video
        'mp4', #'avi', 'mov', 'mkv', 'flv', 'wmv',
        # Images
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp',
        # Code
        'py', 'js', #'java', 'cpp', 'c', 'cs', 'php', 'rb', 'go', 'rs', 'swift',
        # E-books
        #'epub'
    ],
    accept_multiple_files=True,
    help="Upload any document, spreadsheet, media file, code, or e-book for AI-powered processing and analysis"
)
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) selected")
        
        # Display file preview
        st.markdown("### 📋 File Preview")
        for idx, file in enumerate(uploaded_files, 1):
            col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
            
            with col1:
                st.write(f"**{idx}**")
            with col2:
                ext = Path(file.name).suffix.lower()
                icon = {"pdf": "📄", "xlsx": "📊", "xls": "📊", "csv": "📊",
                       "mp3": "🎵", "wav": "🎵", "m4a": "🎵",
                       "mp4": "🎬", "avi": "🎬", "mov": "🎬",
                       "png": "🖼️", "jpg": "🖼️", "jpeg": "🖼️"}.get(ext[1:], "📁")
                st.write(f"{icon} {file.name}")
            with col3:
                st.write(f"{file.size / 1024:.1f} KB")
            with col4:
                st.write(f"`{ext[1:].upper()}`")
        
        st.markdown("---")
        
        # Processing options
        st.markdown("### ⚙️ Processing Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            generate_summary = st.checkbox("📝 Generate Summary", value=True)
            summary_style = st.selectbox(
                "Summary Style",
                ["executive", "technical", "academic", "bullet", "narrative"]
            ) if generate_summary else None
        
        with col2:
            extract_keywords = st.checkbox("🔑 Extract Keywords", value=True)
            enable_ocr = st.checkbox("👁️ Enable OCR", value=True)
        
        with col3:
            generate_questions = st.checkbox("❓ Generate Questions", value=False)
            advanced_analysis = st.checkbox("🔬 Advanced Analysis", value=False)
        
        st.markdown("---")
        
        # Process button
        if st.button("🚀 Process All Documents", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processing_results = []
            
            for idx, file in enumerate(uploaded_files):
                try:
                    status_text.markdown(f"### Processing: {file.name}")
                    
                    with st.status(f"📄 {file.name}", expanded=True) as status:
                        # Save file
                        st.write("💾 Saving file...")
                        temp_path = Config.UPLOADS_DIR / file.name
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        
                        # Calculate file hash for deduplication
                        file_hash = hashlib.md5(file.getvalue()).hexdigest()
                        
                        # Determine file type
                        file_ext = Path(file.name).suffix.lower()
                        if file_ext == '.pdf':
                            file_type = 'pdf'
                        elif file_ext in ['.xlsx', '.xls', '.csv']:
                            file_type = 'excel'
                        elif file_ext in ['.mp3', '.wav', '.m4a', '.ogg']:
                            file_type = 'audio'
                        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                            file_type = 'video'
                        elif file_ext in ['.png', '.jpg', '.jpeg']:
                            file_type = 'image'
                        else:
                            st.warning(f"⚠️ Unsupported file type: {file.name}")
                            continue
                        
                        # Process document
                        st.write("🔍 Extracting content...")
                        start_time = time.time()
                        
                        if file_type in ['audio', 'video']:
                            if file_type == 'audio':
                                result = multimedia_processor.process_audio_advanced(str(temp_path))
                            else:
                                result = multimedia_processor.process_video_advanced(str(temp_path))
                        else:
                            result = document_processor.process_document(str(temp_path), file_type)
                        
                        processing_time = time.time() - start_time
                        
                        # Add to database
                        st.write("💾 Saving to database...")
                        doc_id = db_manager.add_document(
                            file_name=file.name,
                            file_type=file_type,
                            metadata=result['metadata'],
                            file_size=file.size,
                            file_hash=file_hash,
                            tags=[file_type, summary_style] if summary_style else [file_type]
                        )
                        
                        # Chunk and vectorize
                        st.write("🔪 Chunking text...")
                        chunks = rag_engine.chunk_text_adaptive(
                            result['full_text'],
                            metadata={'file_name': file.name, 'file_type': file_type}
                        )
                        
                        st.write("🔗 Adding to vector database...")
                        db_manager.add_chunks_to_vector_db(
                            doc_id,
                            [c['content'] for c in chunks],
                            [c['metadata'] for c in chunks]
                        )
                        
                        # Generate summary if requested
                        summary = None
                        if generate_summary:
                            st.write("📝 Generating summary...")
                            summary_result = rag_engine.summarize_advanced(
                                result['full_text'],
                                style=summary_style,
                                language=st.session_state.current_language,
                                target_length=300
                            )
                            summary = summary_result['summary']
                            db_manager.save_summary(doc_id, summary, st.session_state.current_language)

                            # Generate video summary
                            try:
                                from backend.video_integration import DocumentVideoGenerator, StreamlitVideoHelper
                                video_gen = DocumentVideoGenerator()

                                # generate video from summary
                                video_result = video_gen.generate_video_from_summary(
                                    summary_text=summary,
                                    language="hindi",
                                    target_duration=90
                                )
                                StreamlitVideoHelper.display_video_result(video_result, st)
                            except Exception as e:
                                st.error(f"Video generation failed: {str(e)}")
                        
                        # Extract keywords if requested
                        keywords = None
                        if extract_keywords:
                            st.write("🔑 Extracting keywords...")
                            keywords = rag_engine.extract_keywords(
                                result['full_text'][:3000],
                                num_keywords=10
                            )
                        
                        # Generate questions if requested
                        questions = None
                        if generate_questions:
                            st.write("❓ Generating questions...")
                            questions = rag_engine.generate_questions(
                                result['full_text'][:3000],
                                num_questions=5
                            )
                        
                        # Clean up
                        if temp_path.exists():
                            os.remove(temp_path)
                        
                        processing_results.append({
                            'id': doc_id,
                            'name': file.name,
                            'type': file_type,
                            'summary': summary,
                            'keywords': keywords,
                            'questions': questions,
                            'chunks': len(chunks),
                            'processing_time': processing_time
                        })
                        
                        status.update(
                            label=f"✅ {file.name} - Complete!",
                            state="complete",
                            expanded=False
                        )
                        
                except Exception as e:
                    st.error(f"❌ Error processing {file.name}: {str(e)}")
                    logger.error(f"Processing error for {file.name}: {str(e)}", exc_info=True)
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.empty()
            st.success(f"🎉 Successfully processed {len(processing_results)} document(s)!")
            
            # Display results
            if processing_results:
                st.markdown("---")
                st.markdown("### 📊 Processing Results")
                
                for result in processing_results:
                    with st.expander(f"📄 {result['name']}", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Document ID", result['id'])
                            st.metric("Type", result['type'].upper())
                        with col2:
                            st.metric("Chunks", result['chunks'])
                            st.metric("Processing Time", f"{result['processing_time']:.1f}s")
                        with col3:
                            if result['keywords']:
                                st.metric("Keywords", len(result['keywords']))
                        
                        if result['summary']:
                            st.markdown("**📝 Summary:**")
                            st.info(result['summary'])
                        
                        if result['keywords']:
                            st.markdown("**🔑 Keywords:**")
                            st.write(", ".join(result['keywords']))
                        
                        if result['questions']:
                            st.markdown("**❓ Generated Questions:**")
                            for i, q in enumerate(result['questions'], 1):
                                st.write(f"{i}. {q}")

elif page == "💬 Intelligent Chat":
    st.markdown('<div class="main-header">💬 Intelligent Chat</div>', 
                unsafe_allow_html=True)
    
    if not db_manager or not rag_engine:
        st.error("❌ System not initialized.")
        st.stop()
    
    # Check for documents
    try:
        docs = db_manager.get_all_documents()
        if not docs:
            st.warning("⚠️ No documents found. Please upload documents first!")
            if st.button("📤 Go to Upload"):
                st.rerun()
            st.stop()
    except Exception as e:
        st.error(f"Error accessing documents: {str(e)}")
        st.stop()
    
    # Chat configuration
    with st.expander("⚙️ Chat Configuration", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            response_language = st.selectbox(
                "🌐 Response Language",
                list(Config.LANGUAGES.keys()),
                index=list(Config.LANGUAGES.keys()).index(st.session_state.current_language)
            )
        
        with col2:
            top_k = st.slider("📊 Sources to retrieve", 1, 10, 5)
            show_reasoning = st.checkbox("🧠 Show reasoning", value=True)
        
        with col3:
            show_sources = st.checkbox("📚 Show sources", value=True)
            enable_followup = st.checkbox("❓ Generate follow-ups", value=True)
    
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show metadata
            if message["role"] == "assistant" and "metadata" in message:
                col1, col2, col3 = st.columns(3)
                with col1:
                    confidence = message["metadata"].get("confidence", "medium")
                    emoji = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🔴"
                    st.caption(f"{emoji} Confidence: {confidence.upper()}")
                with col2:
                    complexity = message["metadata"].get("complexity", "moderate")
                    st.caption(f"🎯 Complexity: {complexity}")
                with col3:
                    tokens = message["metadata"].get("tokens_used", 0)
                    st.caption(f"🔢 Tokens: {tokens}")
            
            # Show sources
            if show_sources and "sources" in message and message["sources"]:
                with st.expander(f"📚 View {len(message['sources'])} Sources"):
                    for i, source in enumerate(message['sources'], 1):
                        score = source.get('relevance_score', 0)
                        st.markdown(f"**Source {i}** - Relevance: {score:.1f}%")
                        st.caption(f"📄 {source.get('metadata', {}).get('file_name', 'Unknown')}")
                        st.text(source['content'][:300] + "...")
                        st.markdown("---")
            
            # Show follow-up questions
            if enable_followup and "follow_ups" in message and message["follow_ups"]:
                st.markdown("**💡 Related Questions:**")
                for q in message["follow_ups"]:
                    if st.button(q, key=f"followup_{hash(q)}_{message.get('id', '')}"):
                        st.session_state.messages.append({"role": "user", "content": q})
                        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask anything about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your question..."):
                start_time = time.time()
                
                try:
                    # Semantic search
                    relevant_docs = db_manager.semantic_search(prompt, top_k=top_k)
                    
                    if not relevant_docs:
                        response_text = "I couldn't find relevant information in your documents to answer this question."
                        metadata = {}
                    else:
                        # Generate answer
                        response = rag_engine.generate_answer_advanced(
                            query=prompt,
                            context_documents=relevant_docs,
                            language=response_language,
                            use_chain_of_thought=show_reasoning
                        )
                        
                        response_text = response['answer']
                        metadata = {
                            'confidence': response.get('confidence', 'medium'),
                            'complexity': response.get('complexity', 'moderate'),
                            'tokens_used': response.get('tokens_used', 0),
                            'cost': response.get('cost', 0)
                        }
                        
                        # Generate follow-up questions
                        follow_ups = []
                        if enable_followup:
                            follow_ups = rag_engine.generate_follow_up_questions(
                                prompt, response_text, num_questions=3
                            )
                    
                    response_time = time.time() - start_time
                    
                    # Display response
                    st.markdown(response_text)
                    
                    # Show metadata
                    if metadata:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            confidence = metadata.get("confidence", "medium")
                            emoji = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🔴"
                            st.caption(f"{emoji} Confidence: {confidence.upper()}")
                        with col2:
                            st.caption(f"🎯 Complexity: {metadata.get('complexity', 'moderate')}")
                        with col3:
                            st.caption(f"⏱️ Time: {response_time:.2f}s")
                    
                    # Save message
                    assistant_message = {
                        "role": "assistant",
                        "content": response_text,
                        "sources": relevant_docs if relevant_docs else [],
                        "metadata": metadata,
                        "follow_ups": follow_ups if enable_followup else [],
                        "id": str(uuid.uuid4())
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    # Save to database
                    db_manager.save_chat_message(
                        session_id=st.session_state.session_id,
                        user_message=prompt,
                        assistant_message=response_text,
                        language=response_language,
                        source_documents=[{
                            'content': s['content'][:200],
                            'metadata': s.get('metadata', {})
                        } for s in relevant_docs] if relevant_docs else None,
                        query_complexity=metadata.get('complexity'),
                        response_time=response_time,
                        tokens_used=metadata.get('tokens_used', 0),
                        cost=metadata.get('cost', 0),
                        confidence_level=metadata.get('confidence')
                    )
                    
                    # Update analytics
                    st.session_state.chat_analytics['total_queries'] += 1
                    st.session_state.chat_analytics['total_tokens'] += metadata.get('tokens_used', 0)
                    st.session_state.chat_analytics['total_cost'] += metadata.get('cost', 0)
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    logger.error(f"Chat error: {str(e)}", exc_info=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Suggested questions
    if not st.session_state.messages:
        st.markdown("---")
        st.markdown("### 💡 Try asking:")
        
        suggestions = [
            "📝 Summarize all documents",
            "🔍 What are the main topics?",
            "📊 Extract key statistics",
            "🎯 What are the conclusions?",
            "❓ Generate important questions"
        ]
        
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": suggestion})
                    st.rerun()

elif page == "📊 Analytics & Insights":
    st.markdown('<div class="main-header">📊 Analytics & Insights</div>', 
                unsafe_allow_html=True)
    
    if not db_manager:
        st.error("❌ Database not initialized.")
        st.stop()
    
    # Get analytics
    try:
        analytics = db_manager.get_analytics_dashboard()
        
        # Overview metrics
        st.markdown("### 📈 Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📄 Total Documents",
                analytics['documents']['total'],
                f"{analytics['documents']['total_size_mb']:.1f} MB"
            )
        
        with col2:
            st.metric(
                "💬 Chat Messages",
                analytics['chat']['total_messages'],
                f"Avg {analytics['chat']['avg_response_time']:.2f}s"
            )
        
        with col3:
            st.metric(
                "🔢 Total Tokens",
                f"{analytics['chat']['total_tokens']:,}",
                f"${analytics['chat']['total_cost']:.4f}"
            )
        
        with col4:
            cache_rate = analytics['performance']['cache_hit_rate'] * 100
            st.metric(
                "⚡ Cache Hit Rate",
                f"{cache_rate:.1f}%",
                "Performance"
            )
        
        st.markdown("---")
        
        # Charts and visualizations
        tab1, tab2, tab3 = st.tabs(["📊 Documents", "💬 Chat Analytics", "🔬 Performance"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Document types pie chart
                doc_types = analytics['documents']['by_type']
                if doc_types:
                    fig = px.pie(
                        values=list(doc_types.values()),
                        names=list(doc_types.keys()),
                        title="Documents by Type",
                        color_discrete_sequence=px.colors.sequential.Blues
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No document data available")
            
            with col2:
                # Processing times
                docs = db_manager.get_all_documents()
                if docs:
                    processing_times = [d.get('processing_time', 0) for d in docs if d.get('processing_time')]
                    if processing_times:
                        fig = px.histogram(
                            x=processing_times,
                            nbins=20,
                            title="Document Processing Times",
                            labels={'x': 'Time (seconds)', 'y': 'Count'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No processing time data available")
        
        with tab2:
            # Complexity distribution
            complexity_dist = analytics['chat'].get('complexity_distribution', {})
            if complexity_dist:
                fig = px.bar(
                    x=list(complexity_dist.keys()),
                    y=list(complexity_dist.values()),
                    title="Query Complexity Distribution",
                    labels={'x': 'Complexity Level', 'y': 'Count'},
                    color=list(complexity_dist.values()),
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No complexity data available yet")
            
            # Confidence distribution
            confidence_dist = analytics['chat'].get('confidence_distribution', {})
            if confidence_dist:
                fig = px.pie(
                    values=list(confidence_dist.values()),
                    names=list(confidence_dist.keys()),
                    title="Answer Confidence Levels",
                    color_discrete_sequence=px.colors.sequential.RdYlGn
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Usage trends
            usage_trends = analytics.get('usage_trends', {}).get('daily_messages', [])
            if usage_trends:
                dates = [t['date'] for t in usage_trends]
                counts = [t['count'] for t in usage_trends]
                
                fig = px.line(
                    x=dates,
                    y=counts,
                    title="Daily Chat Activity (Last 7 Days)",
                    labels={'x': 'Date', 'y': 'Messages'},
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Performance metrics
            perf = analytics['performance']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ⚡ Query Performance")
                st.metric("Queries Executed", perf['queries_executed'])
                st.metric("Avg Query Time", f"{perf['avg_query_time']:.3f}s")
                st.metric("Cache Size", perf['cache_size'])
            
            with col2:
                st.markdown("#### 💾 Cache Efficiency")
                cache_rate = perf['cache_hit_rate'] * 100
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=cache_rate,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Cache Hit Rate (%)"},
                    delta={'reference': 70},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        logger.error(f"Analytics error: {str(e)}", exc_info=True)

elif page == "🎯 Advanced Features":
    st.markdown('<div class="main-header">🎯 Advanced Features</div>', 
                unsafe_allow_html=True)
    
    if not db_manager or not rag_engine:
        st.error("❌ System not initialized.")
        st.stop()
    
    feature_tabs = st.tabs([
        "📝 Advanced Summarization",
        "🔄 Multi-Document Analysis",
        "🎨 Custom Processing",
        "🔍 Semantic Explorer"
    ])
    
    with feature_tabs[0]:
        st.markdown("### 📝 Advanced Document Summarization")
        
        # Select document
        try:
            docs = db_manager.get_all_documents()
            if not docs:
                st.warning("No documents available. Upload documents first.")
            else:
                selected_doc = st.selectbox(
                    "Select Document",
                    options=[f"{d['id']} - {d['file_name']}" for d in docs]
                )
                
                if selected_doc:
                    doc_id = int(selected_doc.split(' - ')[0])
                    doc_data = db_manager.get_document_with_chunks(doc_id)
                    
                    if doc_data:
                        # Get full text
                        full_text = ' '.join([chunk['content'] for chunk in doc_data['chunks']])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            summary_style = st.selectbox(
                                "Summary Style",
                                ["executive", "technical", "academic", "bullet", "narrative"]
                            )
                            target_length = st.slider("Target Length (words)", 100, 1000, 300)
                        
                        with col2:
                            language = st.selectbox("Language", list(Config.LANGUAGES.keys()))
                            include_metadata = st.checkbox("Include Metadata Analysis", value=True)
                        
                        if st.button("🚀 Generate Advanced Summary", type="primary", use_container_width=True):
                            with st.spinner("Generating summary..."):
                                result = rag_engine.summarize_advanced(
                                    text=full_text,
                                    style=summary_style,
                                    language=language,
                                    target_length=target_length,
                                    include_metadata=include_metadata
                                )
                                
                                st.markdown("#### 📄 Generated Summary")
                                st.info(result['summary'])
                                
                                # Show stats
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Word Count", result['word_count'])
                                with col2:
                                    st.metric("Compression", f"{result['compression_ratio']*100:.1f}%")
                                with col3:
                                    st.metric("Tokens Used", result['tokens_used'])
                                with col4:
                                    st.metric("Cost", f"${result['cost']:.4f}")
                                
                                # Show metadata if available
                                if include_metadata and 'metadata' in result:
                                    with st.expander("📊 Summary Analysis"):
                                        st.json(result['metadata'])
                                
                                # Export options
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        "💾 Download Summary (TXT)",
                                        result['summary'],
                                        file_name=f"summary_{doc_id}.txt",
                                        mime="text/plain"
                                    )
                                with col2:
                                    import json
                                    st.download_button(
                                        "💾 Download Full Report (JSON)",
                                        json.dumps(result, indent=2),
                                        file_name=f"summary_report_{doc_id}.json",
                                        mime="application/json"
                                    )
        except Exception as e:
            st.error(f"Error: {str(e)}")
            logger.error(f"Summarization error: {str(e)}", exc_info=True)
    
    with feature_tabs[1]:
        st.markdown("### 🔄 Multi-Document Synthesis")
        
        try:
            docs = db_manager.get_all_documents()
            if len(docs) < 2:
                st.warning("Need at least 2 documents for comparison.")
            else:
                selected_docs = st.multiselect(
                    "Select Documents to Analyze",
                    options=[f"{d['id']} - {d['file_name']}" for d in docs]
                )
                
                if len(selected_docs) >= 2:
                    synthesis_query = st.text_area(
                        "Synthesis Query",
                        "Compare and synthesize the main themes across these documents",
                        height=100
                    )
                    
                    if st.button("🔬 Synthesize Documents", type="primary", use_container_width=True):
                        with st.spinner("Performing multi-document analysis..."):
                            # Get document contents
                            doc_contents = []
                            for sel_doc in selected_docs:
                                doc_id = int(sel_doc.split(' - ')[0])
                                doc_data = db_manager.get_document_with_chunks(doc_id)
                                if doc_data:
                                    content = ' '.join([c['content'] for c in doc_data['chunks'][:5]])
                                    doc_contents.append({
                                        'content': content,
                                        'metadata': {'file_name': doc_data['file_name']}
                                    })
                            
                            # Perform synthesis
                            result = rag_engine.multi_document_synthesis(
                                documents=doc_contents,
                                query=synthesis_query,
                                language=st.session_state.current_language
                            )
                            
                            st.markdown("#### 🔬 Synthesis Results")
                            st.success(result['synthesis'])
                            
                            st.metric("Documents Analyzed", result['documents_analyzed'])
        except Exception as e:
            st.error(f"Error: {str(e)}")
            logger.error(f"Multi-doc synthesis error: {str(e)}", exc_info=True)
    
    with feature_tabs[2]:
        st.markdown("### 🎨 Custom Processing Pipeline")
        
        st.info("Build custom processing workflows for your documents")
        
        # Pipeline builder
        st.markdown("#### 🔧 Build Pipeline")
        
        col1, col2 = st.columns(2)
        
        with col1:
            operations = st.multiselect(
                "Select Operations",
                [
                    "Extract Keywords",
                    "Generate Summary",
                    "Answer Questions",
                    "Sentiment Analysis",
                    "Generate Follow-ups"
                ]
            )
        
        with col2:
            output_format = st.selectbox("Output Format", ["JSON", "Markdown", "Text"])
        
        if operations:
            st.markdown("#### 📋 Pipeline Configuration")
            st.info("Custom pipeline feature - Configure your operations here")
    
    with feature_tabs[3]:
        st.markdown("### 🔍 Semantic Search Explorer")
        
        st.markdown("Explore document relationships through semantic similarity")
        
        query = st.text_input("🔎 Search Query", placeholder="Enter search terms...")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            num_results = st.slider("Results", 1, 20, 10)
        with col2:
            similarity_threshold = st.slider("Similarity %", 0, 100, 50)
        with col3:
            file_type_filter = st.selectbox("File Type", ["All", "pdf", "excel", "audio", "video"])
        
        if query and st.button("🔍 Search", type="primary"):
            with st.spinner("Searching..."):
                try:
                    # Perform search
                    filter_meta = None if file_type_filter == "All" else {"file_type": file_type_filter}
                    results = db_manager.semantic_search(
                        query=query,
                        top_k=num_results,
                        filter_metadata=filter_meta
                    )
                    
                    # Filter by threshold
                    filtered_results = [r for r in results if r['relevance_score'] >= similarity_threshold]
                    
                    if filtered_results:
                        st.success(f"Found {len(filtered_results)} relevant results")
                        
                        # Visualize results
                        scores = [r['relevance_score'] for r in filtered_results]
                        labels = [f"{r['metadata'].get('file_name', 'Unknown')[:20]}..." for r in filtered_results]
                        
                        fig = px.bar(
                            x=labels,
                            y=scores,
                            title="Search Results - Relevance Scores",
                            labels={'x': 'Document', 'y': 'Relevance Score (%)'},
                            color=scores,
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show results
                        for i, result in enumerate(filtered_results, 1):
                            with st.expander(f"Result {i}: {result['metadata'].get('file_name', 'Unknown')} - {result['relevance_score']:.1f}%"):
                                st.markdown(f"**Relevance:** {result['relevance_score']:.1f}%")
                                st.markdown(f"**Source:** {result['metadata'].get('file_name', 'Unknown')}")
                                st.text_area("Content", result['content'], height=150, key=f"result_{i}")
                    else:
                        st.warning("No results found matching your criteria.")
                except Exception as e:
                    st.error(f"Search error: {str(e)}")
                    logger.error(f"Search error: {str(e)}", exc_info=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
    <h3>🧠 AI Document Intelligence System v2.0</h3>
    <p style='margin: 1rem 0;'>
        Advanced AI-powered platform for document processing, intelligent analysis, and multilingual support
    </p>
    <p style='font-size: 0.9rem; opacity: 0.9;'>
        Built with Streamlit | Powered by {Config.model_config.model_name} | Vector Search with ChromaDB
    </p>
    <p style='font-size: 0.8rem; margin-top: 1rem; opacity: 0.8;'>
        Session ID: {st.session_state.session_id[:8]} | Active
    </p>
</div>
""", unsafe_allow_html=True)    