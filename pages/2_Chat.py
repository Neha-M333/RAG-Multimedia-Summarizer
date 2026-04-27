"""
Chat Interface Page - FIXED
Streamlit multipage component for document Q&A
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database_manager import EnhancedDatabaseManager
from backend.rag_engine import AdvancedRAGEngine  # FIXED: AdvancedRAGEngine
from backend.translator import Translator
from utils.config import Config
from backend.local_llm import LocalRAGEngine
from backend.chat_metrics_logger import ChatMetricsLogger


st.set_page_config(
    page_title="Chat with Documents",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if 'session_id' not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_language' not in st.session_state:
    st.session_state.current_language = 'English'

# Initialize components
@st.cache_resource
def init_components():
    db_manager = EnhancedDatabaseManager(
        str(Config.db_config.sqlite_path),
        str(Config.db_config.chromadb_path)
    )
    
    # Check if using local LLM or OpenAI
    if Config.USE_LOCAL_LLM:
        # Use local LLM - no API key needed
        from backend.local_llm import LocalRAGEngine
        rag_engine = LocalRAGEngine(model=Config.OLLAMA_MODEL)
        translator = None  # Translation not available with local LLM
        return db_manager, rag_engine, translator
    else:
        # Use OpenAI - need API key
        api_key = Config.OPENAI_API_KEY
        if not api_key or api_key.startswith('sk-your'):
            return None, None, None
        
        rag_engine = AdvancedRAGEngine(api_key, Config.model_config.model_name)
        translator = Translator(api_key)
        return db_manager, rag_engine, translator

db_manager, rag_engine, translator = init_components()
metrics_logger = ChatMetricsLogger("data/chat_metrics_log.xlsx")

# Page header
st.markdown("# 💬 Chat with Your Documents")
st.markdown("Ask questions and get AI-powered answers from your uploaded documents")

if not db_manager or not rag_engine:
    if Config.USE_LOCAL_LLM:
        st.error("❌ System not initialized. Please check if Ollama is running.")
        st.info("💡 Start Ollama: `ollama serve` in terminal")
    else:
        st.error("❌ System not initialized. Please check your API key in .env file.")
    st.stop()

# Check if documents exist
docs = db_manager.get_all_documents()
if not docs:
    st.warning("⚠️ No documents found in the system.")
    st.info("👈 Please go to the **Upload Documents** page to add documents first.")
    if st.button("Go to Upload Page"):
        st.switch_page("pages/1_Upload.py")
    st.stop()

# Sidebar - Chat settings
with st.sidebar:
    st.markdown("### ⚙️ Chat Settings")
    
    # Language selector
    st.session_state.current_language = st.selectbox(
        "🌍 Response Language",
        list(Config.LANGUAGES.keys()),
        index=list(Config.LANGUAGES.keys()).index(st.session_state.current_language)
    )
    
    # Search settings
    st.markdown("---")
    st.markdown("### 🔍 Search Settings")
    top_k = st.slider("Number of sources to retrieve", 1, 10, 5)
    show_sources = st.checkbox("Show source documents", value=True)
    
    # Document filter
    st.markdown("---")
    st.markdown("### 📚 Active Documents")
    st.write(f"Total: {len(docs)} documents")
    
    for doc in docs[:5]:  # Show first 5
        st.caption(f"📄 {doc['file_name']}")
    
    if len(docs) > 5:
        st.caption(f"... and {len(docs) - 5} more")
    
    # Clear chat
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Export chat
    if st.button("💾 Export Chat", use_container_width=True):
        if st.session_state.messages:
            import json
            chat_export = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="Download Chat History",
                data=chat_export,
                file_name=f"chat_history_{st.session_state.session_id[:8]}.json",
                mime="application/json"
            )

# Main chat interface
st.info(f"💬 Chatting in: **{st.session_state.current_language}**")

# Display chat messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if show_sources and "sources" in message and message["sources"]:
                with st.expander(f"📚 View {len(message['sources'])} Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}:** `{source.get('metadata', {}).get('file_name', 'Unknown')}`")
                        with st.container():
                            st.text(source['content'][:300] + "..." if len(source['content']) > 300 else source['content'])
                        st.markdown("---")

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # Start metrics tracking
        chat_session_id = f"{st.session_state.session_id}_chat_{len(st.session_state.messages)}"
        metrics_logger.start_session(chat_session_id)
        
        with st.spinner("🤔 Thinking..."):
            try:
                # Track search phase
                with metrics_logger.track_phase('file_load'):
                    relevant_docs = db_manager.semantic_search(prompt, top_k=top_k)
                
                if not relevant_docs:
                    response_text = "I couldn't find any relevant information in the uploaded documents to answer your question."
                    sources = []
                    metrics_logger.log_error("No relevant documents found")
                else:
                    # Track response generation
                    with metrics_logger.track_phase('response_generation'):
                        response = rag_engine.generate_answer_advanced(
                            query=prompt,
                            context_documents=relevant_docs,
                            language=st.session_state.current_language
                        )
                    
                    response_text = response['answer']
                    sources = relevant_docs
                    
                    # Log query info
                    metrics_logger.log_query_info(
                        query_text=prompt,
                        response_length=len(response_text),
                        sources_retrieved=len(sources),
                        confidence_level=response.get('confidence', 'medium')
                    )
                
                # Display response
                st.markdown(response_text)
                
                # Show sources
                if show_sources and sources:
                    with st.expander(f"📚 View {len(sources)} Sources"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**Source {i}:** `{source.get('metadata', {}).get('file_name', 'Unknown')}`")
                            with st.container():
                                st.text(source['content'][:300] + "..." if len(source['content']) > 300 else source['content'])
                            st.markdown("---")
                
                # Save messages
                assistant_message = {
                    "role": "assistant",
                    "content": response_text,
                    "sources": sources
                }
                st.session_state.messages.append(assistant_message)
                
                # Save to database
                db_manager.save_chat_message(
                    session_id=st.session_state.session_id,
                    user_message=prompt,
                    assistant_message=response_text,
                    language=st.session_state.current_language,
                    source_documents=[{
                        'content': s['content'][:200],
                        'metadata': s.get('metadata', {})
                    } for s in sources]
                )
                
                # End metrics session
                metrics_logger.end_session()
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                metrics_logger.log_error(str(e))
                metrics_logger.end_session()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


# Suggested questions
if not st.session_state.messages:
    st.markdown("---")
    st.markdown("### 💡 Suggested Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize all documents", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Please provide a summary of all the uploaded documents."
            })
            st.rerun()
        
        if st.button("🔍 What are the main topics?", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "What are the main topics discussed in the documents?"
            })
            st.rerun()
    
    with col2:
        if st.button("📊 Extract key findings", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "What are the key findings or conclusions from the documents?"
            })
            st.rerun()
        
        if st.button("❓ Generate questions", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Generate 5 important questions that these documents can answer."
            })
            st.rerun()