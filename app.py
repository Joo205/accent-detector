import streamlit as st
import requests
import whisper
import os
import uuid
from moviepy.editor import VideoFileClip

def download_video(url, filename="input_video.mp4"):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        raise

def extract_audio_from_video(video_path, audio_path="audio.wav"):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path, fps=16000, nbytes=2, codec='pcm_s16le')

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def detect_accent(text):
    text = text.lower()
    british_words = ['mate', 'bloody', 'cheers', 'lorry', 'queue', 'biscuit']
    american_words = ['gonna', 'wanna', 'dude', 'cookie', 'truck', 'sidewalk']
    australian_words = ['no worries', 'mate', 'heaps', 'barbie', 'arvo', 'servo']

    if any(word in text for word in british_words):
        return "British", 85
    elif any(word in text for word in american_words):
        return "American", 90
    elif any(word in text for word in australian_words):
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
        extract_audio_from_video(video_filename)
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
