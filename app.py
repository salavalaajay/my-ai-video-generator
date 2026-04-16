import streamlit as st
import os
import shutil
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
from planner import Planner
from script_generator import ScriptGenerator
from video_fetcher import VideoFetcher
from voice_generator import VoiceGenerator
from assembler import VideoAssembler

# Load environment variables
load_dotenv()

# State management initialization
if 'video_ready' not in st.session_state:
    st.session_state.video_ready = False
if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = ""
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None

# Setup paths
TEMP_DIR = "temp_assets"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Page config
st.set_page_config(page_title="Script to Screen AI", page_icon="🎬", layout="wide")

# Custom CSS for the Orange/Gold Theme
st.markdown("""
    <style>
    /* Main Background and Text */
    .main {
        background-color: #0e1117;
    }
    
    /* Headers and Labels */
    h1, h2, h3, label, p, .stMarkdown {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input, .stSelectbox > div > div > select, .stSlider > div > div > div {
        background-color: #1a1c24 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #333 !important;
    }
    
    /* Orange Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #ff8c00 0%, #ff4500 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-size: 1.1rem !important;
        transition: transform 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0px 4px 15px rgba(255, 140, 0, 0.4) !important;
    }
    
    /* Radio Buttons */
    .stRadio > div {
        flex-direction: row !important;
        gap: 20px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111318 !important;
        border-right: 1px solid #222 !important;
    }
    
    /* Video Placeholder */
    .video-placeholder {
        background-color: #111318;
        border: 2px dashed #333;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        color: #666;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Script to Screen")
st.markdown("### Agentic AI Video Generator")

# Sidebar - Configuration (Hidden by default for a cleaner look)
with st.sidebar:
    st.header("⚙️ Configuration")
    ai_provider = st.selectbox("AI Provider", ["Groq (Free)", "OpenAI (Paid)"], index=0)
    
    if ai_provider == "OpenAI (Paid)":
        openai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
        groq_key = None
    else:
        groq_key = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password")
        openai_key = None

    pexels_key = st.text_input("Pexels API Key", value=os.getenv("PEXELS_API_KEY", ""), type="password")
    voice_service = st.selectbox("Voice Service", ["Edge-TTS (Free & Natural)", "gTTS (Free & Robotic)", "ElevenLabs (Paid)"], index=0)
    eleven_key = st.text_input("ElevenLabs API Key", value=os.getenv("ELEVENLABS_API_KEY", ""), type="password") if "ElevenLabs" in voice_service else None

# Main Layout
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Topic")
    topic = st.text_input("Topic", placeholder="e.g. How black holes are formed", label_visibility="collapsed")
    
    st.subheader("Video Type")
    video_type = st.radio("Video Type", ["Educational", "Marketing", "Story"], label_visibility="collapsed")
    
    st.subheader("Duration")
    duration_min = st.slider("Duration (minutes)", 0.5, 5.0, 1.0, step=0.5, label_visibility="collapsed")
    duration = int(duration_min * 60) # Convert to seconds
    st.markdown(f"<span style='color: #ff8c00; font-weight: bold;'>{duration} seconds</span>", unsafe_allow_html=True)
    
    st.subheader("Language")
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Spanish", "French", "German"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✨ Generate Video")

with col_right:
    if 'video_ready' not in st.session_state or not st.session_state.video_ready:
        st.markdown(f"""
            <div class="video-placeholder">
                <div style="font-size: 50px;">▶️</div>
                <div style="margin-top: 20px; font-weight: bold; color: #888;">Your video will appear here</div>
                <div style="font-size: 0.9rem; color: #555;">Fill the form and click Generate</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.video(st.session_state.final_video_path)
        with open(st.session_state.final_video_path, "rb") as file:
            st.download_button(
                label="📥 Download MP4",
                data=file,
                file_name=f"{topic.replace(' ', '_')}_{language}.mp4",
                mime="video/mp4"
            )

# State management (Removing redundant block)

if generate_btn:
    # Check for keys
    ai_key = openai_key if ai_provider == "OpenAI (Paid)" else groq_key
    if not ai_key or not pexels_key:
        st.error(f"Please provide both {ai_provider.split(' ')[0]} and Pexels API keys in the sidebar.")
    else:
        try:
            # Initialize clients
            if ai_provider == "OpenAI (Paid)":
                ai_client = OpenAI(api_key=ai_key)
                provider_name = "openai"
            else:
                ai_client = Groq(api_key=ai_key)
                provider_name = "groq"

            planner = Planner(ai_client, provider=provider_name)
            script_gen = ScriptGenerator(ai_client, provider=provider_name)
            video_fetcher = VideoFetcher(pexels_key)
            
            # Determine voice service
            if "ElevenLabs" in voice_service:
                v_service = "elevenlabs"
            elif "Edge-TTS" in voice_service:
                v_service = "edge-tts"
            else:
                v_service = "gtts"
                
            voice_gen = VoiceGenerator(api_key=eleven_key, service=v_service)
            assembler = VideoAssembler(TEMP_DIR)

            with st.status("🎬 Processing...", expanded=True) as status:
                # 1. Planning
                st.write("🧠 Planning the video structure...")
                plan = planner.plan_video(topic, video_type, duration, language)
                st.session_state.current_plan = plan
                st.write(f"Created {len(plan.scenes)} scenes.")

                # 2. Scripting (Planner already did most, but we can refine here)
                st.write("📝 Refining scripts and keywords...")
                # Script refinement could be added here if needed

                # 3. Asset Generation (Videos and Voices)
                video_paths = []
                audio_paths = []
                
                for i, scene in enumerate(plan.scenes):
                    st.write(f"📺 Scene {i+1}/{len(plan.scenes)}: Generating assets...")
                    
                    # 3a. Video Fetching
                    video_url = video_fetcher.fetch_video(scene.keywords, scene.duration)
                    if video_url:
                        video_path = os.path.join(TEMP_DIR, f"video_{i}.mp4")
                        if video_fetcher.download_video(video_url, video_path):
                            video_paths.append(video_path)
                            st.write(f"  ✅ Video found for keywords: {', '.join(scene.keywords[:2])}")
                        else:
                            video_paths.append(None)
                            st.warning(f"  ⚠️ Video download failed for Scene {i+1}.")
                    else:
                        video_paths.append(None)
                        st.warning(f"  ⚠️ No video found for Scene {i+1}. (Using fallback)")

                    # 3b. Voiceover Generation
                    audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
                    if voice_gen.generate_voiceover(scene.narration, language, audio_path):
                        audio_paths.append(audio_path)
                        st.write(f"  ✅ Voiceover generated ({language})")
                    else:
                        audio_paths.append(None)
                        st.error(f"  ❌ Voiceover failed for Scene {i+1}.")

                # 4. Assembly
                st.write("🎞️ Assembling final video...")
                final_output = os.path.join(TEMP_DIR, "final_video.mp4")
                success = assembler.assemble_video(plan, video_paths, audio_paths, final_output)

                if success:
                    st.session_state.video_ready = True
                    st.session_state.final_video_path = final_output
                    status.update(label="✅ Video Generated Successfully!", state="complete")
                    st.rerun()
                else:
                    st.error("Failed to assemble the video.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Output Section (Script Breakdown below the main layout)
if st.session_state.video_ready:
    st.divider()
    st.subheader("📄 Script Breakdown")
    if st.session_state.current_plan:
        # Show scenes in a grid or expanding list
        for i in range(0, len(st.session_state.current_plan.scenes), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(st.session_state.current_plan.scenes):
                    scene = st.session_state.current_plan.scenes[i + j]
                    with cols[j].expander(f"🎬 Scene {scene.scene_number} ({scene.duration}s)"):
                        st.write(f"**Narration ({language}):**")
                        st.write(scene.narration)
                        st.write(f"**Visuals:** {scene.visual_description}")
                        st.write(f"**Keywords:** {', '.join(scene.keywords)}")

# Clean up button (optional)
st.sidebar.divider()
if st.sidebar.button("🧹 Clear Temporary Files"):
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR)
        st.session_state.video_ready = False
        st.session_state.current_plan = None
        st.sidebar.success("Cleaned up temporary assets.")
