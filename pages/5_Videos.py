import streamlit as st
from pathlib import Path

st.title("🎬 Video Gallery")

video_dir = Path("data/videos")
videos = list(video_dir.glob("*.mp4"))

for video in videos:
    with st.expander(f"📹 {video.stem}"):
        st.video(str(video))
        
        with open(video, "rb") as f:
            st.download_button(
                "⬇️ Download",
                f,
                file_name=video.name,
                mime="video/mp4"
            )