import streamlit as st
import tempfile
import os
import requests
import vosk
import wave
import json
from faster_whisper import WhisperModel

def download_video_from_url(url):
    if not url.endswith(".mp4"):
        raise ValueError("Only .mp4 links are supported.")
    
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Failed to download the video from the provided URL.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(response.content)
        return temp_video.name

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
st.title("🌍 English Accent Detector from Video URL")

video_url = st.text_input("Paste a direct link to an .mp4 video")

if video_url:
    try:
        st.info("⬇️ Downloading video...")
        video_path = download_video_from_url(video_url)
        st.success("✅ Video downloaded")

        audio_path = video_path.replace(".mp4", ".wav")

        st.info("🔧 Extracting audio...")
        extract_audio_with_av(video_path, audio_path)
        st.success("✅ Audio extracted")

        st.info("🧠 Transcribing...")
        text = transcribe_audio_with_faster_whisper(audio_path)
        st.success("✅ Transcription complete")

        st.info("🕵️ Detecting accent...")
        accent, confidence = detect_accent(text)
        st.success(f"🎯 Accent: {accent}")
        st.write(f"Confidence: {confidence}%")
        st.write("Transcription:")
        st.text(text)

        os.remove(video_path)
        os.remove(audio_path)

    except Exception as e:
        st.error(f"❌ Error: {e}")
