import sounddevice as sd
import soundfile as sf

def record_audio(sample_rate, duration, device):
    try:
        return sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            device=device,
            dtype="int16"
        )
    except Exception as e:
        raise RuntimeError(f"Error during recording: {e}")

def stop_recording(data, sample_rate, max_duration=15):
    try:
        sd.stop()

        max_samples = int(max_duration * sample_rate)
        trimmed_data = data[:max_samples]

        output_file = "uploaded_file.wav"
        sf.write(output_file, trimmed_data, sample_rate)
        return output_file
    except Exception as e:
        raise RuntimeError(f"Error saving audio: {e}")
