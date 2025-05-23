import streamlit as st
import requests
import uuid
import os
from vosk import Model, KaldiRecognizer
import wave
import subprocess

def download_video(url, filename="video.mp4"):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def convert_mp4_to_wav(mp4_path, wav_path):
    # محاولة استخدام ffmpeg فقط إذا كان مثبتاً في بيئة Streamlit
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", mp4_path, "-ac", "1", "-ar", "16000", wav_path
        ], check=True)
    except Exception as e:
        st.error(f"فشل تحويل الفيديو إلى WAV: {e}")
        raise

def transcribe_with_vosk(wav_path):
    model = Model(lang="en-us")
    wf = wave.open(wav_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    
    results = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results += rec.Result()
    results += rec.FinalResult()
    return results

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

# واجهة Streamlit
st.title("English Accent Detector (FFmpeg-free)")
video_url = st.text_input("Enter a direct MP4 video URL:")

if st.button("Analyze") and video_url:
    video_path = f"{uuid.uuid4()}.mp4"
    wav_path = "audio.wav"
    
    try:
        st.info("Downloading video...")
        download_video(video_url, video_path)

        st.info("Extracting audio...")
        convert_mp4_to_wav(video_path, wav_path)

        st.info("Transcribing...")
        transcript = transcribe_with_vosk(wav_path)

        st.success("Done!")
        accent, confidence = detect_accent(transcript)
        st.write(f"Accent Detected: **{accent}**")
        st.write(f"Confidence: **{confidence}%**")
        st.text(transcript)

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)
