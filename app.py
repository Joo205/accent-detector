import streamlit as st
import tempfile
import os
import vosk
import wave
import json
from faster_whisper import WhisperModel

def is_valid_video_file(file):
    return file.name.endswith(".mp4")

def extract_audio_with_av(input_path, output_path):
    import av
    container = av.open(input_path)
    audio_stream = container.streams.audio[0]
    output = wave.open(output_path, 'wb')
    output.setnchannels(1)
    output.setsampwidth(2)
    output.setframerate(16000)

    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono",
        rate=16000
    )

    for frame in container.decode(audio=0):
        frame = resampler.resample(frame)
        output.writeframes(frame.planes[0].to_bytes())

    output.close()

def transcribe_audio_with_faster_whisper(audio_path):
    model = WhisperModel("base.en", compute_type="int8")
    segments, _ = model.transcribe(audio_path)
    full_text = " ".join([segment.text for segment in segments])
    return full_text

def detect_accent(text):
    text = text.lower()
    if any(w in text for w in ['cheers', 'bloody', 'innit']):
        return "British", 80
    elif any(w in text for w in ['gonna', 'wanna', 'dude']):
        return "American", 85
    elif any(w in text for w in ['mate', 'no worries', 'heaps']):
        return "Australian", 75
    else:
        return "Uncertain", 50

# Streamlit UI
st.title("🎙️ English Accent Detector")

uploaded_file = st.file_uploader("Upload an MP4 video file", type=["mp4"])

if uploaded_file and is_valid_video_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_file.read())
        video_path = temp_video.name

    audio_path = video_path.replace(".mp4", ".wav")
    
    st.info("🔧 Extracting audio...")
    try:
        extract_audio_with_av(video_path, audio_path)
        st.success("✅ Audio extracted")
    except Exception as e:
        st.error(f"❌ Failed to extract audio: {e}")
        st.stop()

    st.info("🧠 Transcribing...")
    try:
        text = transcribe_audio_with_faster_whisper(audio_path)
        st.success("✅ Transcription complete")
    except Exception as e:
        st.error(f"❌ Failed to transcribe audio: {e}")
        st.stop()

    st.info("🕵️ Detecting accent...")
    accent, confidence = detect_accent(text)
    st.success(f"🎯 Accent: {accent}")
    st.write(f"Confidence: {confidence}%")
    st.write("Transcription:")
    st.text(text)

    os.remove(video_path)
    os.remove(audio_path)
else:
    st.warning("⚠️ Please upload a valid .mp4 file.")
