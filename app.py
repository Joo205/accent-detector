import streamlit as st
import requests
import whisper
import os
import uuid
import subprocess

def download_video(url, filename="input_video.mp4"):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def extract_audio(video_path, audio_path="audio.wav"):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    subprocess.run(command, check=True)

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def detect_accent(text):
    text = text.lower()
    if any(word in text for word in ['mate', 'bloody', 'cheers']):
        return "British", 85
    elif any(word in text for word in ['gonna', 'wanna', 'dude']):
        return "American", 90
    elif any(word in text for word in ['no worries', 'mate', 'heaps']):
        return "Australian", 75
    else:
        return "Uncertain", 50

st.title("English Accent Detector")

video_url = st.text_input("Enter a direct MP4 video URL:")

if st.button("Analyze") and video_url:
    st.info("Downloading video...")
    video_filename = f"{uuid.uuid4()}.mp4"
    download_video(video_url, video_filename)

    st.info("Extracting audio...")
    extract_audio(video_filename)

    st.info("Transcribing and analyzing...")
    transcription = transcribe_audio("audio.wav")
    accent, confidence = detect_accent(transcription)

    st.success(f"Accent: {accent}")
    st.write(f"Confidence: {confidence}%")
    st.write("Transcription:")
    st.text(transcription)
