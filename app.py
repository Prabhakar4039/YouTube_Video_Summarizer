import streamlit as st
import os
from dotenv import load_dotenv

# Import our utilities
from utils.transcript import extract_video_id, get_transcript
from utils.summarize import generate_summary
from utils.chat import chat_with_video

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="YouTube Video Summarizer", page_icon="📺", layout="wide")

st.markdown("# 📺 YouTube Video Summarizer")
st.markdown("---")

# URL Input section
url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# Sidebar for Transcript preview
st.sidebar.markdown("### 📝 Transcript Preview")

if url:
    video_id = extract_video_id(url)
    
    if video_id:
        if st.button("🚀 Process Video"):
            with st.spinner("🔍 Fetching transcript..."):
                try:
                    # Cache transcript extraction (pass URL for fallback)
                    @st.cache_data
                    def get_cached_transcript(vid, u):
                        return get_transcript(vid, u)
                    
                    # Notify user if API fails and fallback kicks in 
                    # Note: get_transcript handles the fallback internally
                    transcript = get_cached_transcript(video_id, url)
                    st.session_state['transcript'] = transcript
                    
                    with st.spinner("🤖 Generating summary..."):
                        # Cache summarization
                        @st.cache_data
                        def get_cached_summary(text):
                            return generate_summary(text)
                        
                        summary = get_cached_summary(transcript)
                        st.session_state['summary'] = summary
                
                except Exception as e:
                    st.error(f"Error processing video: {e}")
        
        # Display results from session state
        if 'transcript' in st.session_state:
            st.sidebar.text_area("Transcript Content", st.session_state['transcript'], height=400)
            
            # Summary Section
            st.markdown("### 📋 AI Summary")
            st.markdown(st.session_state['summary'])
            
            st.markdown("---")
            
            # Chat Section
            st.markdown("### 💬 Chat with Video")
            user_question = st.text_input("Ask a question about the video:")
            
            if user_question:
                with st.spinner("💭 Thinking..."):
                    answer = chat_with_video(user_question, st.session_state['transcript'])
                    st.info(f"**AI Response:**\n\n{answer}")
    else:
        st.warning("Invalid YouTube URL. Please check and try again.")
else:
    st.info("Paste a YouTube link above to get started.")

# Footer
st.markdown("---")
st.caption("Powered by Groq and llama-3.3-70b-versatile. ⚡ Faster than light.")
