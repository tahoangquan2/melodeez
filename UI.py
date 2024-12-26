import time
import streamlit as st
import os
from record_audio import record_audio, stop_recording
import sounddevice as sd
from pydub import AudioSegment
import tempfile
from search import run_search_pipeline

# Page title and layout
st.set_page_config(page_title="Melodeez", layout="wide")

container = st.container()
with container:
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='font-size: 3rem;'>🎵 Melodeez</h1>
            <p style='font-size: 1.2rem; opacity: 0.8;'>Find your tune by humming or uploading</p>
        </div>
    """, unsafe_allow_html=True)

    with open("style.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Create two columns for input methods
    col1, col2 = st.columns(2, gap="large")

    # First column for recording
    with col1:
        st.markdown("""
            <div style='background: rgba(157, 125, 255, 0.1); padding: 20px; border-radius: 10px;'>
                <h3 style='margin-bottom: 1rem; text-align: center;'>Record Your Voice 🎤</h3>
            </div>
        """, unsafe_allow_html=True)

        devices = sd.query_devices()
        input_devices = {i: d['name'] for i, d in enumerate(devices) if d['max_input_channels'] > 0}

        selected_device = st.selectbox(
            "Choose your microphone:",
            options=list(input_devices.keys()),
            format_func=lambda x: input_devices[x]
        )

        # Session state initialization
        if "is_recording" not in st.session_state:
            st.session_state.is_recording = False
        if "recording_data" not in st.session_state:
            st.session_state.recording_data = None
        if "displaying_file" not in st.session_state:
            st.session_state.displaying_file = None
        if "start_time" not in st.session_state:
            st.session_state.start_time = None

        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("🎤 Tap to Record"):
            if not st.session_state.is_recording:
                # Start recording
                st.session_state.is_recording = True
                st.session_state.start_time = time.time()
                st.session_state.recording_data = record_audio(
                    sample_rate=44100,
                    duration=60,
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
                            max_duration=min(60, elapsed_time)
                        )
                        st.session_state.displaying_file = saved_file
                        st.success("Recording saved successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.is_recording:
            st.warning(f"Recording in progress... Press button again to stop.")

        # Auto-stop recording after 60 seconds
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

    # Second column for file upload
    with col2:
        st.markdown("""
            <div style='background: rgba(157, 125, 255, 0.1); padding: 20px; border-radius: 10px;'>
                <h3 style='margin-bottom: 1rem; text-align: center;'>Upload Audio File 📁</h3>
            </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Or upload an audio file (5-60 seconds):",
            type=["mp3", "wav", "m4a"]
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

        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if uploaded_file and st.button("Upload"):
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
        st.markdown('</div>', unsafe_allow_html=True)

    # Audio preview and search section
    if st.session_state.displaying_file:
        st.markdown("""
            <div style='background: rgba(157, 125, 255, 0.1); padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h3 style='text-align: center;'>Current Input</h3>
            </div>
        """, unsafe_allow_html=True)

        st.audio("uploaded_file.wav", format="audio/wav")

        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("🔍 Searching"):
            try:
                st.subheader("Results from Search:")
                results = run_search_pipeline("uploaded_file.wav")

                if results:
                    for result in results:
                        st.markdown(f"""
                            <div class="result-item">
                                {result['title']} by {result['artist']} <br>
                                Match: {result['match']}
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No matches found.")

            except Exception as e:
                st.error(f"Error during search: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
