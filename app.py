import streamlit as st
import whisper
import av
import numpy as np
import soundfile as sf
import os
import uuid
import requests

def download_video(url, filename="input_video.mp4"):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        raise

def extract_audio_av(video_path, audio_path="audio.wav"):
    container = av.open(video_path)
    audio_frames = []

    for frame in container.decode(audio=0):
        audio_frames.append(frame.to_ndarray())

    if not audio_frames:
        raise RuntimeError("لم يتم العثور على أي صوت في الفيديو.")

    audio_data = np.concatenate(audio_frames)
    sf.write(audio_path, audio_data, 16000)  # حفظ الصوت بصيغة WAV

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def detect_accent(text):
    text = text.lower()
    british_words = ['mate', 'bloody', 'cheers', 'rubbish', 'loo']
    american_words = ['gonna', 'wanna', 'dude', 'awesome', 'bathroom']
    australian_words = ['no worries', 'heaps', 'arvo', 'bush', 'thongs']

    if any(word in text for word in british_words):
        return "British", 85
    elif any(word in text for word in american_words):
        return "American", 90
    elif any(word in text for word in australian_words):
        return "Australian", 75
    else:
        return "Uncertain", 50

st.title("English Accent Detector (No FFmpeg!)")

video_url = st.text_input("Enter a direct MP4 video URL:")

if st.button("Analyze") and video_url:
    st.info("Downloading video...")
    video_filename = f"{uuid.uuid4()}.mp4"
    try:
        download_video(video_url, video_filename)
    except:
        st.stop()

    st.info("Extracting audio using PyAV...")
    try:
        extract_audio_av(video_filename)
    except Exception as e:
        st.error(f"خطأ في استخراج الصوت: {e}")
        st.stop()
    st.success("Audio extraction done!")

    st.info("Transcribing audio...")
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

    # تنظيف الملفات المؤقتة
    try:
        os.remove(video_filename)
        os.remove("audio.wav")
    except:
        pass
