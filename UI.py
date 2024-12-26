import time
import streamlit as st
import os
from record_audio import record_audio, stop_recording
import sounddevice as sd
from pydub import AudioSegment
import tempfile
from search import run_search_pipeline

# Page configuration
st.set_page_config(
    page_title="Melodeez",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load CSS
with open("style.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Title with custom styling
st.markdown("<h1 class='main-title'>🎵 Melodeez</h1>", unsafe_allow_html=True)

# Initialize session state
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "recording_data" not in st.session_state:
    st.session_state.recording_data = None
if "displaying_file" not in st.session_state:
    st.session_state.displaying_file = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Get available audio devices
devices = sd.query_devices()
input_devices = {i: d['name'] for i, d in enumerate(devices) if d['max_input_channels'] > 0}

st.subheader("Choose how to input your tune:")
selected_device = st.selectbox(
    "Select your microphone:",
    options=list(input_devices.keys()),
    format_func=lambda x: input_devices[x]
)

# Record button with improved logic
record_button = st.button(
    "🎤 " + ("Stop Recording" if st.session_state.is_recording else "Start Recording"),
    key="record_button",
    help="Click to start/stop recording. Minimum 5 seconds, maximum 60 seconds."
)

if record_button:
    if not st.session_state.is_recording:
        # Start recording
        st.session_state.is_recording = True
        st.session_state.start_time = time.time()
        st.session_state.recording_data = record_audio(
            sample_rate=44100,
            duration=60,
            device=selected_device
        )
        st.experimental_rerun()
    else:
        # Stop recording
        st.session_state.is_recording = False
        elapsed_time = time.time() - st.session_state.start_time

        if elapsed_time < 5:
            st.error("Recording must be at least 5 seconds long. Please try again.")
        else:
            try:
                saved_file = stop_recording(
                    data=st.session_state.recording_data,
                    sample_rate=44100,
                    max_duration=min(60, elapsed_time)
                )
                st.session_state.displaying_file = saved_file
                st.success("Recording saved successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# Show recording status
if st.session_state.is_recording:
    elapsed = time.time() - st.session_state.start_time
    st.markdown(f"""
        <div style='text-align: center; color: #ff3b30;'>
            Recording in progress... ({elapsed:.1f}s)
        </div>
    """, unsafe_allow_html=True)

    # Auto-stop recording after 60 seconds
    if elapsed >= 60:
        st.session_state.is_recording = False
        try:
            saved_file = stop_recording(
                data=st.session_state.recording_data,
                sample_rate=44100,
                max_duration=60
            )
            st.session_state.displaying_file = saved_file
            st.success("Recording saved successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# File upload section
st.markdown("### Or upload an audio file:")
uploaded_file = st.file_uploader(
    "Upload audio (5-60 seconds)",
    type=["mp3", "wav", "m4a"],
    help="Supports MP3, WAV, and M4A formats"
)

def check_audio_duration(file_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
        tmp_file.write(file_content)
        tmp_path = tmp_file.name

    try:
        audio = AudioSegment.from_file(tmp_path)
        duration = len(audio) / 1000
        os.unlink(tmp_path)
        return duration
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise e

if uploaded_file and st.button("Process Upload"):
    try:
        file_content = uploaded_file.read()
        duration = check_audio_duration(file_content)

        if duration < 5:
            st.error("Audio file must be at least 5 seconds long.")
        elif duration > 60:
            st.error("Audio file must not exceed 60 seconds.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
                tmp_file.write(file_content)
                tmp_path = tmp_file.name

            audio = AudioSegment.from_file(tmp_path)
            audio.export("uploaded_file.wav", format="wav")
            st.session_state.displaying_file = "uploaded_file.wav"
            st.success("File uploaded successfully!")

            os.unlink(tmp_path)

    except Exception as e:
        st.error(f"Error processing file: {e}")

# Display current audio and search functionality
if st.session_state.displaying_file:
    st.markdown("### Current Input:")
    st.audio(st.session_state.displaying_file, format="audio/wav")

    if st.button("🔍 Search for Matches"):
        try:
            with st.spinner("Searching for matches..."):
                results = run_search_pipeline(st.session_state.displaying_file)

            if results:
                st.markdown("### Found Matches:")
                for result in results:
                    st.markdown(f"""
                        <div class="result-item">
                            <strong>{result['title']}</strong>
                            <div>Artist: {result['artist']}</div>
                            <div>Match: {result['match']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No matches found. Try recording a longer sample.")

        except Exception as e:
            st.error(f"Error during search: {str(e)}")
