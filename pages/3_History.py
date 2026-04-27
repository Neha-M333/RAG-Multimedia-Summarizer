"""
History & Analytics Page - FIXED
Streamlit multipage component for viewing chat history and analytics
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database_manager import EnhancedDatabaseManager
from utils.config import Config
from utils.helpers import export_to_json, export_to_csv

st.set_page_config(
    page_title="History & Analytics",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'session_id' not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Initialize components
@st.cache_resource
def init_components():
    db_manager = EnhancedDatabaseManager(
        str(Config.db_config.sqlite_path),  # FIXED
        str(Config.db_config.chromadb_path)  # FIXED
    )
    return db_manager

db_manager = init_components()

# Page header
st.markdown("# 📊 History & Analytics")
st.markdown("View your chat history, document library, and system analytics")

if not db_manager:
    st.error("❌ Database not initialized.")
    st.stop()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat History", 
    "📄 Documents", 
    "📈 Analytics",
    "⚙️ System Info"
])

# ============== TAB 1: CHAT HISTORY ==============
with tab1:
    st.markdown("### 💬 Conversation History")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        limit = st.selectbox("Show last", [10, 25, 50, 100, "All"], index=2)
        limit_value = 1000 if limit == "All" else limit
    
    with col2:
        language_filter = st.selectbox(
            "Filter by language",
            ["All", "English", "Hindi", "Kannada"]
        )
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Get chat history
    history = db_manager.get_chat_history(st.session_state.session_id, limit=limit_value)
    
    if history:
        # Filter by language if needed
        if language_filter != "All":
            history = [h for h in history if h['language'] == language_filter.lower()[:2]]
        
        st.success(f"📖 Found {len(history)} conversation(s)")
        
        # Export options
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("💾 Export JSON"):
                export_data = {
                    'session_id': st.session_state.session_id,
                    'export_date': datetime.now().isoformat(),
                    'total_messages': len(history),
                    'conversations': history
                }
                import json
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export CSV"):
                df = pd.DataFrame([
                    {
                        'Timestamp': h['timestamp'],
                        'User Question': h['user_message'],
                        'Assistant Answer': h['assistant_message'][:100] + '...',
                        'Language': h['language']
                    }
                    for h in history
                ])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        st.markdown("---")
        
        # Display conversations
        for idx, item in enumerate(history, 1):
            with st.expander(
                f"🕐 {item['timestamp']} - {item['user_message'][:60]}...", 
                expanded=(idx == 1)
            ):
                col1, col2 = st.columns([1, 5])
                
                with col1:
                    st.metric("Language", item['language'].upper())
                    if item.get('source_documents'):
                        st.metric("Sources", len(item['source_documents']))
                
                with col2:
                    st.markdown("**👤 You:**")
                    st.info(item['user_message'])
                    
                    st.markdown("**🤖 Assistant:**")
                    st.success(item['assistant_message'])
                    
            # Show sources if available
            if item.get('source_documents'):
                                with st.expander("📚 View Sources"):
                                    for i, source in enumerate(item['source_documents'], 1):
                                        st.caption(f"**Source {i}:** {source.get('metadata', {}).get('file_name', 'Unknown')}")
                                        st.text(source.get('content', '')[:200] + "...")
            else:
                st.info("🔭 No conversation history yet. Start chatting to see your history here!")
                if st.button("Go to Chat"):
                    st.switch_page("pages/2_Chat.py")

# ============== TAB 2: DOCUMENTS ==============
with tab2:
    st.markdown("### 📄 Document Library")
    
    docs = db_manager.get_all_documents()
    
    if docs:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", len(docs))
        
        with col2:
            pdf_count = len([d for d in docs if d['file_type'] == 'pdf'])
            st.metric("PDFs", pdf_count)
        
        with col3:
            excel_count = len([d for d in docs if d['file_type'] == 'excel'])
            st.metric("Excel/CSV", excel_count)
        
        with col4:
            audio_video = len([d for d in docs if d['file_type'] in ['audio', 'video']])
            st.metric("Audio/Video", audio_video)
        
        st.markdown("---")
        
        # Documents table
        st.markdown("#### 📋 All Documents")
        
        docs_data = []
        for doc in docs:
            docs_data.append({
                'ID': doc['id'],
                'File Name': doc['file_name'],
                'Type': doc['file_type'].upper(),
                'Upload Date': doc['upload_date'][:10],
                'Processed': '✅' if doc.get('processed') else '⏳'
            })
        
        df = pd.DataFrame(docs_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Detailed document view
        st.markdown("#### 🔍 Document Details")
        
        selected_doc = st.selectbox(
            "Select a document to view details",
            options=[f"{doc['id']} - {doc['file_name']}" for doc in docs]
        )
        
        if selected_doc:
            doc_id = int(selected_doc.split(' - ')[0])
            doc = next(d for d in docs if d['id'] == doc_id)
            
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**Basic Information:**")
                    st.write(f"**ID:** {doc['id']}")
                    st.write(f"**Name:** {doc['file_name']}")
                    st.write(f"**Type:** {doc['file_type'].upper()}")
                    st.write(f"**Uploaded:** {doc['upload_date']}")
                    
                 # Delete button with popover confirmation
                    st.markdown("---")

                    with st.popover("🗑️ Delete Document"):
                        st.warning(f"Delete '{doc['file_name']}'?")
                        st.caption("This action cannot be undone.")
                        
                        if st.button("✅ Confirm Delete", key=f"confirm_delete_{doc['id']}", type="primary"):
                            success = db_manager.delete_document(doc['id'])
                            if success:
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete")