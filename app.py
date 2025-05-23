import streamlit as st
import requests
import whisper
import os
import uuid

def download_video(url, filename):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        raise

def transcribe_video(video_path):
    model = whisper.load_model("base")
    # في النسخ الجديدة للwhisper ممكن تمرر ملف فيديو mp4 مباشرة
    result = model.transcribe(video_path)
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
    video_filename = f"{uuid.uuid4()}.mp4"
    st.info("Downloading video...")
    try:
        download_video(video_url, video_filename)
    except:
        st.stop()

    st.info("Starting transcription...")
    try:
        transcription = transcribe_video(video_filename)
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
    except:
        pass
