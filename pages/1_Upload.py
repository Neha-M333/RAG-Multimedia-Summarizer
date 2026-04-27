"""
FIXED Upload Page with Proper Multi-language Support
Summary and video now respect the selected language
"""
import streamlit as st
import os
import sys
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).parent.parent))

from backend.document_processor import DocumentProcessor
from backend.database_manager import EnhancedDatabaseManager
from backend.rag_engine import AdvancedRAGEngine
from utils.config import Config
from backend.local_llm import LocalRAGEngine

# Import video generator
from backend.video_integration import DocumentVideoGenerator, StreamlitVideoHelper

st.set_page_config(
    page_title="Upload & Generate Videos",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []
if 'generated_videos' not in st.session_state:
    st.session_state.generated_videos = []

# Initialize components
@st.cache_resource
def init_components():
    processor = DocumentProcessor()
    db_manager = EnhancedDatabaseManager(
        str(Config.db_config.sqlite_path),
        str(Config.db_config.chromadb_path)
    )
    
    if Config.USE_LOCAL_LLM:
        from backend.local_llm import LocalRAGEngine
        rag_engine = LocalRAGEngine(model=Config.OLLAMA_MODEL)
        st.sidebar.success("🖥️ Using Local LLM")
    else:
        api_key = Config.OPENAI_API_KEY
        if not api_key or api_key.startswith('sk-your'):
            return None, None, None, None
        rag_engine = AdvancedRAGEngine(api_key, Config.model_config.model_name)
        st.sidebar.success("☁️ Using OpenAI")
    
    # Initialize video generator
    video_gen = DocumentVideoGenerator()
    
    return processor, db_manager, rag_engine, video_gen

processor, db_manager, rag_engine, video_gen = init_components()

# Page header
st.markdown("# 🎬 Upload & Generate AI Videos")
st.markdown("Upload documents and generate animated video summaries with AI narration")

if not all([processor, db_manager, rag_engine, video_gen]):
    if Config.USE_LOCAL_LLM:
        st.error("❌ System not initialized. Check if Ollama is running.")
    else:
        st.error("❌ System not initialized. Check API key in .env file.")
    st.stop()

# File uploader
st.markdown("---")
st.markdown("### 📁 Select Files to Upload")

uploaded_files = st.file_uploader(
    "Choose files to process",
    type=['pdf', 'docx', 'pptx', 'xlsx', 'xls', 'csv', 'mp3', 'mp4', 
          'jpg', 'jpeg', 'png', 'txt', 'md'],
    accept_multiple_files=True,
    help="Upload documents to generate summaries and videos"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) selected")
    
    # Display file info
    st.markdown("### 📋 Selected Files")
    for idx, file in enumerate(uploaded_files, 1):
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        with col1:
            st.write(f"**{idx}.**")
        with col2:
            st.write(f"📄 {file.name}")
        with col3:
            st.write(f"{file.size / 1024:.2f} KB")
        with col4:
            ext = Path(file.name).suffix.lower()[1:].upper()
            st.write(f"`{ext}`")
    
    st.markdown("---")
    
    # Processing options
    st.markdown("### ⚙️ Processing Options")
    
    tab1, tab2 = st.tabs(["📝 Summary Options", "🎬 Video Options"])
    
    # FIXED: Store video language in session state to use for summary
    if 'selected_video_language' not in st.session_state:
        st.session_state.selected_video_language = "english"
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            generate_summary = st.checkbox("Generate Text Summary", value=True)
            summary_style = st.selectbox(
                "Summary Style",
                ["executive", "technical", "academic", "bullet", "narrative"]
            ) if generate_summary else None
        
        with col2:
            extract_keywords = st.checkbox("Extract Keywords", value=True)
            generate_questions = st.checkbox("Generate Questions", value=False)
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            generate_video = st.checkbox("🎬 Generate Video", value=True, 
                                        help="Create animated video from summary")
            
            if generate_video:
                # FIXED: Store in session state
                st.session_state.selected_video_language = st.selectbox(
                    "Video Language",
                    ["english", "hindi", "kannada"],
                    help="Language for narration AND summary"
                )
        
        with col2:
            if generate_video:
                target_duration = st.slider(
                    "Target Duration (seconds)",
                    min_value=30,
                    max_value=180,
                    value=60,
                    step=15,
                    help="Desired video length"
                )
        
        with col3:
            if generate_video:
                include_subtitles = st.checkbox(
                    "Include Subtitles",
                    value=True,
                    help="Show text on video"
                )
    
    st.markdown("---")
    
    # IMPORTANT: Show language info
    if generate_video:
        # Map language codes to full names for display
        lang_display = {
            "english": "English",
            "hindi": "Hindi (हिंदी)",
            "kannada": "Kannada (ಕನ್ನಡ)"
        }
        
        st.info(f"📢 **Selected Language:** {lang_display[st.session_state.selected_video_language]}")
        st.caption("Both summary text and video narration will be in this language")
    
    # Process button
    if st.button("🚀 Process Documents & Generate Videos", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_container = st.container()
        
        with status_container:
            for idx, file in enumerate(uploaded_files):
                with st.status(f"Processing {file.name}...", expanded=True) as status:
                    try:
                        # Save file
                        # Save file
                        st.write("💾 Saving file...")
                        temp_path = Config.UPLOADS_DIR / file.name
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())

                        # Determine file type - COMPLETE FIXED VERSION
                        st.write("🔍 Detecting file type...")
                        file_ext = Path(file.name).suffix.lower()

                        # Map extension to processor type
                        file_type_mapping = {
                            '.pdf': 'pdf',
                            '.docx': 'word',
                            '.doc': 'word',
                            '.pptx': 'powerpoint',
                            '.ppt': 'powerpoint',
                            '.xlsx': 'excel',
                            '.xls': 'excel',
                            '.csv': 'excel',
                            '.mp3': 'audio',
                            '.wav': 'audio',
                            '.m4a': 'audio',
                            '.ogg': 'audio',
                            '.flac': 'audio',
                            '.mp4': 'video',
                            '.avi': 'video',
                            '.mov': 'video',
                            '.mkv': 'video',
                            '.jpg': 'image',
                            '.jpeg': 'image',
                            '.png': 'image',
                            '.gif': 'image',
                            '.bmp': 'image',
                            '.txt': 'text',
                            '.md': 'text',
                            '.log': 'text'
                        }

                        file_type = file_type_mapping.get(file_ext)

                        if not file_type:
                            st.error(f"❌ Unsupported file type: {file_ext}")
                            st.info("Supported: PDF, Word (.docx/.doc), PowerPoint, Excel, Audio, Video, Images, Text")
                            if temp_path.exists():
                                os.remove(temp_path)
                            continue  # Skip to next file

                        st.write(f"📎 Detected type: {file_type.upper()}")
                        # Process document
                        try:
                            result = processor.process_document(str(temp_path), file_type)
                        except Exception as proc_error:
                            error_msg = str(proc_error)
                            
                            # Check if it's a password error
                            if "PASSWORD-PROTECTED" in error_msg or "encrypted" in error_msg.lower():
                                status.update(
                                    label=f"🔒 {file.name} - Password Protected", 
                                    state="error", 
                                    expanded=True
                                )
                                st.error("**This PDF is password-protected!**")
                                st.warning(f"📄 File: `{file.name}`")
                                st.info("""
                                **Solutions:**
                                1. **Remove password protection:**
                                - Open PDF in Adobe Acrobat
                                - Go to File → Properties → Security
                                - Set Security to "No Security"
                                - Save and re-upload
                                
                                2. **Or unlock online:**
                                - Visit: https://www.ilovepdf.com/unlock_pdf
                                - Upload your PDF
                                - Download unlocked version
                                - Re-upload here
                                
                                3. **Or use a different PDF** without password protection
                                """)
                                continue  # Skip to next file
                            else:
                                # Other errors
                                status.update(
                                    label=f"❌ Error processing {file.name}", 
                                    state="error", 
                                    expanded=True
                                )
                                st.error(f"Error: {error_msg}")
                                continue
                        
                        # Add to database
                        st.write("💾 Saving to database...")
                        doc_id = db_manager.add_document(
                            file.name,
                            file_type,
                            result['metadata'],
                            file_size=file.size
                        )
                        
                        # Chunk text
                        st.write("🔪 Chunking text...")
                        chunks = rag_engine.chunk_text_adaptive(
                            result['full_text'],
                            metadata={'file_name': file.name, 'file_type': file_type}
                        )
                        
                        # Add to vector DB
                        st.write("🔗 Adding to vector database...")
                        db_manager.add_chunks_to_vector_db(
                            doc_id,
                            [c['content'] for c in chunks],
                            [c['metadata'] for c in chunks]
                        )
                        
                        # ✅ FIXED: Generate summary in SELECTED LANGUAGE
                        summary = None
                        summary_language_code = st.session_state.selected_video_language
                        
                        # Map to full language names that RAG engine expects
                        language_map = {
                            "english": "English",
                            "hindi": "Hindi",
                            "kannada": "Kannada"
                        }
                        summary_language_name = language_map[summary_language_code]
                        
                        if generate_summary or generate_video:
                            st.write(f"📊 Generating {summary_language_name} summary...")
                            
                            try:
                                summary_result = rag_engine.summarize_advanced(
                                    result['full_text'],
                                    style=summary_style if summary_style else "executive",
                                    language=summary_language_name,  # ✅ FIXED: Use selected language!
                                    target_length=300
                                )
                                summary = summary_result['summary']
                                
                                # Show preview of summary
                                st.write(f"   ✅ Summary preview: {summary[:100]}...")
                                
                                # Verify language (for Hindi/Kannada)
                                if summary_language_code == "hindi":
                                    has_hindi = any('\u0900' <= char <= '\u097F' for char in summary)
                                    if has_hindi:
                                        st.write(f"   ✅ Hindi text verified!")
                                    else:
                                        st.warning("   ⚠️ Summary appears to be in English (translation may have failed)")
                                
                                elif summary_language_code == "kannada":
                                    has_kannada = any('\u0C80' <= char <= '\u0CFF' for char in summary)
                                    if has_kannada:
                                        st.write(f"   ✅ Kannada text verified!")
                                    else:
                                        st.warning("   ⚠️ Summary appears to be in English (translation may have failed)")
                                
                                db_manager.save_summary(doc_id, summary, summary_language_code[:2])
                                
                            except Exception as sum_error:
                                st.error(f"   ❌ Summary generation failed: {sum_error}")
                                # Use English as fallback
                                summary_result = rag_engine.summarize_advanced(
                                    result['full_text'],
                                    style=summary_style if summary_style else "executive",
                                    language="English",
                                    target_length=300
                                )
                                summary = summary_result['summary']
                                st.warning("   ⚠️ Falling back to English summary")
                        
                        # Extract keywords
                        keywords = None
                        if extract_keywords:
                            st.write("🔑 Extracting keywords...")
                            keywords = rag_engine.extract_keywords(
                                result['full_text'][:3000],
                                num_keywords=10
                            )
                        
                        # Generate questions
                        questions = None
                        if generate_questions:
                            st.write("❓ Generating questions...")
                            questions = rag_engine.generate_questions(
                                result['full_text'][:3000],
                                num_questions=5
                            )
                        
                        # ✅ Generate video with CORRECT language
                        video_result = None
                        if generate_video and summary:
                            st.write(f"🎬 Generating {summary_language_name} animated video...")
                            st.write("   This may take 1-2 minutes...")
                            
                            # Run async video generation
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            video_result = loop.run_until_complete(
                                video_gen.generate_video_from_summary(
                                    summary_text=summary,  # ✅ Summary is now in correct language
                                    language=summary_language_code,  # ✅ Pass correct language
                                    target_duration=target_duration,
                                    include_subtitles=include_subtitles,
                                    document_name=Path(file.name).stem
                                )
                            )
                            loop.close()
                            
                            if video_result["success"]:
                                st.write(f"   ✅ Video created: {video_result['duration']:.1f}s")
                                st.write(f"   Language: {summary_language_name}")
                                st.session_state.generated_videos.append(video_result)
                            else:
                                st.write(f"   ⚠️ Video generation failed: {video_result.get('error', 'Unknown')}")
                        
                        # Cleanup
                        if temp_path.exists():
                            os.remove(temp_path)
                        
                        # Store result
                        st.session_state.processed_docs.append({
                            'id': doc_id,
                            'name': file.name,
                            'type': file_type,
                            'summary': summary,
                            'summary_language': summary_language_name,  # ✅ Store language used
                            'keywords': keywords,
                            'questions': questions,
                            'chunks': len(chunks),
                            'video': video_result
                        })
                        
                        status.update(
                            label=f"✅ {file.name} - Complete!",
                            state="complete",
                            expanded=False
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
        
        st.success(f"🎉 Successfully processed {len(uploaded_files)} document(s)!")
        
        # Display results
        if st.session_state.processed_docs:
            st.markdown("---")
            st.markdown("### 📊 Processing Results")
            
            for doc in st.session_state.processed_docs:
                with st.expander(f"📄 {doc['name']}", expanded=True):
                    
                    # Document info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Document ID", doc['id'])
                        st.metric("Type", doc['type'].upper())
                    with col2:
                        st.metric("Chunks", doc['chunks'])
                        if doc.get('summary_language'):
                            st.metric("Language", doc['summary_language'])
                    with col3:
                        if doc.get('video') and doc['video'].get('success'):
                            st.metric("Video Duration", f"{doc['video']['duration']:.1f}s")
                    
                    # Summary
                    if doc['summary']:
                        st.markdown(f"**📝 Summary ({doc.get('summary_language', 'Unknown')}):**")
                        st.info(doc['summary'])
                    
                    # Keywords
                    if doc['keywords']:
                        st.markdown("**🔑 Keywords:**")
                        st.write(", ".join(doc['keywords']))
                    
                    # Questions
                    if doc['questions']:
                        st.markdown("**❓ Generated Questions:**")
                        for i, q in enumerate(doc['questions'], 1):
                            st.write(f"{i}. {q}")
                    
                    # Video player
                    if doc.get('video') and doc['video'].get('success'):
                        st.markdown("---")
                        st.markdown("**🎬 Generated Video:**")
                        
                        video_col1, video_col2 = st.columns([2, 1])
                        
                        with video_col1:
                            st.video(doc['video']['video_path'])
                        
                        with video_col2:
                            st.markdown("#### Video Info")
                            st.write(f"**Duration:** {doc['video']['duration']:.1f}s")
                            st.write(f"**Size:** {doc['video']['file_size'] / (1024*1024):.2f} MB")
                            st.write(f"**Language:** {doc['video']['language'].capitalize()}")
                            
                            # Download button
                            with open(doc['video']['video_path'], 'rb') as f:
                                st.download_button(
                                    label="⬇️ Download Video",
                                    data=f,
                                    file_name=Path(doc['video']['video_path']).name,
                                    mime="video/mp4",
                                    key=f"download_{doc['id']}"
                                )

# Show existing documents
st.markdown("---")
st.markdown("### 📚 Document Library")

if db_manager:
    docs = db_manager.get_all_documents()
    
    if docs:
        import pandas as pd
        
        docs_df = pd.DataFrame([
            {
                'ID': doc['id'],
                'File Name': doc['file_name'],
                'Type': doc['file_type'].upper(),
                'Upload Date': doc['upload_date'][:10],
                'Processed': '✅' if doc.get('processed') else '⏳'
            }
            for doc in docs
        ])
        
        st.dataframe(docs_df, use_container_width=True, hide_index=True)
    else:
        st.info("🔭 No documents yet. Upload files to get started!")

# Display generated videos
if st.session_state.generated_videos:
    st.markdown("---")
    st.markdown("### 🎬 Generated Videos")
    
    for video in st.session_state.generated_videos:
        with st.expander(f"🎥 {Path(video['video_path']).stem}", expanded=False):
            StreamlitVideoHelper.display_video_result(video, st)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>💡 Tip: Select Hindi or Kannada for multilingual summaries and videos</p>
    <p>🎬 Videos include: AI narration, animated character, and multilingual subtitles</p>
</div>
""", unsafe_allow_html=True)