import streamlit as st
import requests
import whisper
import os
import uuid
import subprocess

def download_video(url, filename="input_video.mp4"):
    response = requests.get(url)
    response.raise_for_status()  # تأكد من نجاح التحميل
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
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        st.write(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error(f"FFmpeg failed:\n{e.stderr}")
        raise

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
    video_filename = f"{uuid.uuid4()}.mp4"
    audio_filename = "audio.wav"

    st.info("Downloading video...")
    try:
        download_video(video_url, video_filename)
        st.success("Video downloaded successfully!")
    except Exception as e:
        st.error(f"Failed to download video: {e}")
        st.stop()

    st.info("Extracting audio...")
    try:
        extract_audio(video_filename, audio_filename)
        if not os.path.exists(audio_filename):
            st.error("Audio file was not created. Check ffmpeg or the video file.")
            st.stop()
        st.success("Audio extraction done!")
    except Exception:
        st.stop()

    st.info("Starting transcription...")
    try:
        transcription = transcribe_audio(audio_filename)
        st.success("Transcription done!")
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        st.stop()

    accent, confidence = detect_accent(transcription)
    st.write(f"Accent: **{accent}**")
    st.write(f"Confidence: **{confidence}%**")
    st.text_area("Transcription", transcription, height=200)

    # نظافة: حذف الملفات المؤقتة
    if os.path.exists(video_filename):
        os.remove(video_filename)
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
