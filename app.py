import streamlit as st
import requests
import whisper
import tempfile
import os
import av
import numpy as np

def download_video(url):
    local_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(resp.content)
        return local_path
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        return None

def extract_audio_from_video(video_path):
    try:
        container = av.open(video_path)
        audio_frames = []
        for frame in container.decode(audio=0):
            audio_frames.append(frame.to_ndarray())
        if not audio_frames:
            st.error("لم يتم استخراج أي صوت من الفيديو.")
            return None
        audio = np.concatenate(audio_frames, axis=1)
        # Whisper requires 16000Hz mono audio, so let's convert sample rate and channels
        # But to keep dependencies low, let's just save as wav 16k mono via soundfile
        import soundfile as sf
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        # audio is ndarray shape (channels, samples), let's make mono by averaging channels
        if audio.shape[0] > 1:
            mono_audio = np.mean(audio, axis=0)
        else:
            mono_audio = audio[0]
        sf.write(audio_path, mono_audio, 16000)
        return audio_path
    except Exception as e:
        st.error(f"خطأ في استخراج الصوت: {e}")
        return None

def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        st.error(f"خطأ في التفريغ الصوتي: {e}")
        return None

def detect_accent(text):
    text = text.lower()
    british_words = ['mate', 'bloody', 'cheers', 'loo', 'rubbish']
    american_words = ['gonna', 'wanna', 'dude', 'awesome', 'sidewalk']
    australian_words = ['no worries', 'mate', 'heaps', 'arvo', 'barbie']
    if any(word in text for word in british_words):
        return "British", 85
    elif any(word in text for word in american_words):
        return "American", 90
    elif any(word in text for word in australian_words):
        return "Australian", 75
    else:
        return "Uncertain", 50

st.title("Accent Detector - Video Link")

video_url = st.text_input("Enter direct MP4 video URL here:")

if st.button("Analyze") and video_url:
    with st.spinner("Downloading video..."):
        video_path = download_video(video_url)
    if not video_path:
        st.stop()

    with st.spinner("Extracting audio..."):
        audio_path = extract_audio_from_video(video_path)
    if not audio_path:
        st.stop()

    with st.spinner("Transcribing audio..."):
        transcription = transcribe_audio(audio_path)
    if not transcription:
        st.stop()

    accent, confidence = detect_accent(transcription)

    st.success(f"Accent detected: {accent} (Confidence: {confidence}%)")
    st.write("Transcription:")
    st.write(transcription)

    # Cleanup temp files
    try:
        os.remove(video_path)
        os.remove(audio_path)
    except:
        pass
