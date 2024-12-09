import time
import streamlit as st
import os
from record_audio import record_audio, stop_recording
import sounddevice as sd

# Page title and layout
st.set_page_config(page_title="Melodeez", layout="centered")
st.title("Melodeez")

# Load CSS
with open("style.css") as f:
    css = f.read()
    
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Get available audio devices
devices = sd.query_devices()
input_devices = {i: d['name'] for i, d in enumerate(devices) if d['max_input_channels'] > 0}

# Dropdown to select microphone
st.subheader("Provide a sample or hum your tune:")
selected_device = st.selectbox(
    "Choose your microphone:", options=list(input_devices.keys()), format_func=lambda x: input_devices[x]
)

# Initialize session state
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "recording_data" not in st.session_state:
    st.session_state.recording_data = None
if "displaying_file" not in st.session_state:
    st.session_state.displaying_file = None

if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Interactive microphone button
if st.button("🎤 Tap to Record"):
    if not st.session_state.is_recording:
        # Start recording
        st.session_state.is_recording = True
        st.session_state.start_time = time.time()  # Record the start time
        st.session_state.recording_data = record_audio(
            sample_rate=44100,
            duration=15,  # Original recording duration
            device=selected_device
        )# auto stop after 15 seconds
        st.warning("Recording started. Tap again to stop.")
    else:
        # Stop recording
        st.session_state.is_recording = False
        try:
            elapsed_time = time.time() - st.session_state.start_time
            output_file = "HumInput.wav"
            saved_file = stop_recording(
                data=st.session_state.recording_data,
                sample_rate=44100,
                output_file=output_file,
                max_duration=elapsed_time  # Save only the first 3 seconds
            )
            st.session_state.displaying_file = saved_file
            st.success(f"Recording saved as {saved_file}.")
        except Exception as e:
            st.error(f"Error: {e}")

# Automatically stop after 15 seconds

# File uploader
uploaded_file = st.file_uploader("Or upload an audio file:", type=["mp3", "wav"])

if uploaded_file and st.button("Upload"):
    # Save uploaded file
    uploaded_path = f"uploaded_file.{uploaded_file.name.split('.')[-1]}"
    with open(uploaded_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.displaying_file = uploaded_path
    st.success("File uploaded successfully!")

# Display the currently active file
if st.session_state.displaying_file:
    st.write(f"Current Input:")
    st.audio(
        st.session_state.displaying_file,
        format="audio/mp3" if st.session_state.displaying_file.endswith(".mp3") else "audio/wav"
    )

# Simulate search functionality
if st.button("Search a song"):
    st.subheader("Results from Search:")
    results = [
        {"title": "Song 1", "artist": "Artist A", "match": "90%"},
        {"title": "Song 2", "artist": "Artist B", "match": "75%"},
        {"title": "Song 3", "artist": "Artist C", "match": "60%"},
    ]
    for result in results:
        st.markdown(
            f"""
            <div class="result-item">
                <strong>{result['title']}</strong> by {result['artist']} <br>
                Match: {result['match']}
            </div>
            """,
            unsafe_allow_html=True,
        )