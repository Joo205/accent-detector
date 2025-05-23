import streamlit as st
import requests
import numpy as np
import uuid
import os
from scipy.io import wavfile
from faster_whisper import WhisperModel

def download_video(url, filename="video.mp4"):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        raise

def extract_audio_from_video(filename):
    import av
    container = av.open(filename)
    audio_stream = next((s for s in container.streams if s.type == "audio"), None)
    if audio_stream is None:
        raise RuntimeError("لم يتم العثور على مسار صوتي")

    audio_frames = []
    for frame in container.decode(audio=0):
        audio_frames.append(frame.to_ndarray())

    audio_data = np.concatenate(audio_frames)
    wavfile.write("audio.wav", 16000, audio_data.astype(np.int16))

def transcribe_audio(audio_path):
    model = WhisperModel("base.en", compute_type="int8")
    segments, _ = model.transcribe(audio_path)
    text = " ".join([seg.text for seg in segments])
    return text

def detect_accent(text):
    text = text.lower()
    british = ['mate', 'bloody', 'cheers', 'rubbish', 'loo']
    american = ['gonna', 'wanna', 'dude', 'awesome', 'y’all']
    australian = ['heaps', 'no worries', 'arvo', 'mate', 'crikey']

    if any(word in text for word in british):
        return "British", 85
    elif any(word in text for word in american):
        return "American", 90
    elif any(word in text for word in australian):
        return "Australian", 75
    else:
        return "Uncertain", 50

st.title("🎙️ English Accent Detector")

url = st.text_input("Paste a direct link to an .mp4 video file")

if st.button("Analyze") and url:
    st.info("Downloading video...")
    file_name = f"{uuid.uuid4()}.mp4"
    try:
        download_video(url, file_name)
        st.success("Download done!")
    except:
        st.stop()

    st.info("Extracting audio...")
    try:
        extract_audio_from_video(file_name)
        st.success("Audio extraction done!")
    except Exception as e:
        st.error(f"خطأ في استخراج الصوت: {e}")
        st.stop()

    st.info("Transcribing...")
    try:
        text = transcribe_audio("audio.wav")
        st.success("Done!")
    except Exception as e:
        st.error(f"خطأ في التفريغ الصوتي: {e}")
        st.stop()

    accent, confidence = detect_accent(text)
    st.write(f"**Accent Detected:** {accent}")
    st.write(f"**Confidence:** {confidence}%")
    st.text_area("Transcription", text)

    # تنظيف الملفات
    os.remove(file_name)
    os.remove("audio.wav")
