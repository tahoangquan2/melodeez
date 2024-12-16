import time
import streamlit as st
import os
from record_audio import record_audio, stop_recording
import sounddevice as sd
from pydub import AudioSegment

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
        st.session_state.start_time = time.time()
        st.session_state.recording_data = record_audio(
            sample_rate=44100,
            duration=60,  # Automatically stops after 60 seconds
            device=selected_device
        )
    else:
        # Stop recording manually
        st.session_state.is_recording = False
        elapsed_time = time.time() - st.session_state.start_time

        if elapsed_time < 5:
            st.error("Recording must be at least 5 seconds long. Please try again.")
        else:
            try:
                saved_file = stop_recording(
                    data=st.session_state.recording_data,
                    sample_rate=44100,
                    max_duration=min(60, elapsed_time)  # Ensure not exceeding 60 seconds
                )
                st.session_state.displaying_file = saved_file
                st.success("Recording saved successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.is_recording and time.time() - st.session_state.start_time >= 60:
    print("Auto-stopping recording...")
    st.session_state.is_recording = False
    try:
        saved_file = stop_recording(
            data=st.session_state.recording_data,
            sample_rate=44100,
            max_duration=60
        )
        st.session_state.displaying_file = saved_file
        st.success("Recording saved successfully!")
    except Exception as e:
        st.error(f"Error: {e}")

if st.session_state.is_recording:
    elapsed = time.time() - st.session_state.start_time
    st.warning(f"Recording in progress ({elapsed:.1f} seconds)... Press button again to stop.")

# File uploader
uploaded_file = st.file_uploader("Or upload an audio file (5-60 seconds):", type=["mp3", "wav", "m4a"])

if uploaded_file and st.button("Upload"):
    try:
        # First save the uploaded file with its original extension
        temp_filename = f"temp_upload.{uploaded_file.name.split('.')[-1].lower()}"
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert to WAV using pydub
        audio = AudioSegment.from_file(temp_filename)
        duration_in_seconds = len(audio) / 1000  # Convert ms to seconds

        if duration_in_seconds < 5:
            st.error("Audio file must be at least 5 seconds long.")
        elif duration_in_seconds > 60:
            st.error("Audio file must not exceed 60 seconds.")
        else:
            # Export as WAV
            audio.export("uploaded_file.wav", format="wav")
            st.session_state.displaying_file = "uploaded_file.wav"
            st.success("File uploaded successfully!")

        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    except Exception as e:
        st.error(f"Error processing file: {e}")
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# Display the currently active file
if st.session_state.displaying_file:
    st.write(f"Current Input:")
    st.audio("uploaded_file.wav", format="audio/wav")

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
