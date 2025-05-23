import streamlit as st
import requests
import os
import uuid
from faster_whisper import WhisperModel
import av  # For audio decoding


def download_video(url, filename="input_video.mp4"):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        raise


def extract_audio_with_av(video_path, audio_path="audio.wav"):
    container = av.open(video_path)
    audio_stream = next((s for s in container.streams if s.type == 'audio'), None)

    if audio_stream is None:
        raise RuntimeError("No audio stream found")

    with open(audio_path, "wb") as f:
        for frame in container.decode(audio=0):
            f.write(frame.planes[0].to_bytes())


def transcribe_audio(audio_path):
    model = WhisperModel("base", compute_type="cpu", download_root=".")
    segments, _ = model.transcribe(audio_path)
    full_text = " ".join([segment.text for segment in segments])
    return full_text


def detect_accent(text):
    text = text.lower()
    if any(word in text for word in ['mate', 'bloody', 'cheers', 'innit']):
        return "British", 85
    elif any(word in text for word in ['gonna', 'wanna', 'dude', 'yo']):
        return "American", 90
    elif any(word in text for word in ['no worries', 'heaps', 'reckon']):
        return "Australian", 75
    else:
        return "Uncertain", 50


st.title("English Accent Detector")
video_url = st.text_input("Enter a direct MP4 video URL:")

if st.button("Analyze") and video_url:
    st.info("Downloading video...")
    video_filename = f"{uuid.uuid4()}.mp4"
    try:
        download_video(video_url, video_filename)
    except:
        st.stop()

    st.info("Extracting audio...")
    try:
        extract_audio_with_av(video_filename)
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        st.stop()
    st.success("Audio extraction done!")

    st.info("Starting transcription...")
    try:
        transcription = transcribe_audio("audio.wav")
    except Exception as e:
        st.error(f"خطأ في التفريغ الصوتي: {e}")
        st.stop()
    st.success("Transcription done!")

    accent, confidence = detect_accent(transcription)

    st.success(f"Accent: {accent}")
    st.write(f"Confidence: {confidence}%")
    st.write("Transcription:")
    st.text(transcription)

    try:
        os.remove(video_filename)
        os.remove("audio.wav")
    except:
        pass
