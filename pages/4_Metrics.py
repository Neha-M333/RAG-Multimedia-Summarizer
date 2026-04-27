"""
Metrics & Analytics Page
View detailed performance metrics and statistics
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.chat_metrics_logger import ChatMetricsLogger
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Performance Metrics",
    page_icon="📊",
    layout="wide"
)

# Initialize metrics logger
try:
    metrics_logger = ChatMetricsLogger("data/chat_metrics_log.xlsx")
except Exception as e:
    st.error(f"Error initializing metrics: {e}")
    st.stop()

st.markdown("# 📊 Performance Metrics & Analytics")
st.markdown("Track and analyze system performance over time")

# Get statistics
stats = metrics_logger.get_statistics()

if 'error' in stats:
    st.error(f"Error loading metrics: {stats['error']}")
    st.stop()

if 'message' in stats:
    st.info(stats['message'])
    st.info("👆 Upload some documents and ask questions to see metrics here!")
    st.stop()

# === OVERVIEW METRICS ===
st.markdown("## 📈 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Sessions",
        stats['total_sessions'],
        help="Total number of processing sessions"
    )

with col2:
    st.metric(
        "Files Processed",
        stats['total_files'],
        help="Unique files processed"
    )

with col3:
    st.metric(
        "Avg Processing Time",
        f"{stats['avg_processing_time']:.2f}s",
        help="Average time to process files"
    )

with col4:
    st.metric(
        "Success Rate",
        f"{stats['success_rate']:.1f}%",
        help="Percentage of successful operations"
    )

st.markdown("---")

# === DETAILED STATISTICS ===
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Processing Statistics")
    st.metric("Total Words Processed", f"{stats['total_words_processed']:,}")
    st.metric("Total Chunks Created", f"{stats['total_chunks_created']:,}")
    st.metric("Avg Words per File", f"{stats['avg_words_per_file']:.0f}")
    st.metric("Avg Chunks per File", f"{stats['avg_chunks_per_file']:.0f}")

with col2:
    st.markdown("### ⏱️ Timing Breakdown")
    st.metric("Avg Response Time", f"{stats['avg_response_time']:.3f}s")
    st.metric("Avg Total Runtime", f"{stats['avg_total_runtime']:.3f}s")

st.markdown("---")

# === FILE TYPES CHART ===
st.markdown("### 📁 File Types Distribution")

if stats['file_types']:
    fig = px.pie(
        values=list(stats['file_types'].values()),
        names=list(stats['file_types'].keys()),
        title="Documents by Type",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# === RECENT SESSIONS ===
st.markdown("### 🕐 Recent Sessions")

if stats['recent_sessions']:
    df_recent = pd.DataFrame(stats['recent_sessions'])
    
    # Select relevant columns
    display_columns = ['Timestamp', 'File_Name', 'Words_Count', 
                      'Processing_Time_Sec', 'Success']
    
    available_columns = [col for col in display_columns if col in df_recent.columns]
    
    if available_columns:
        st.dataframe(
            df_recent[available_columns],
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")

# === EXPORT OPTIONS ===
st.markdown("### 💾 Export Options")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Print Statistics", use_container_width=True):
        metrics_logger.print_statistics()
        st.success("Statistics printed to console")

with col2:
    if st.button("📄 Export Summary Report", use_container_width=True):
        output_file = "data/metrics_summary_report.xlsx"
        metrics_logger.export_summary_report(output_file)
        
        with open(output_file, 'rb') as f:
            st.download_button(
                label="Download Report",
                data=f,
                file_name="metrics_summary_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 Metrics are automatically logged for all upload and chat operations</p>
    <p>Data is stored in: <code>data/chat_metrics_log.xlsx</code></p>
</div>
""", unsafe_allow_html=True)