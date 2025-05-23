import streamlit as st
import requests
import uuid
import os
import torch
import torchaudio
from faster_whisper import WhisperModel

def download_video(url, filename="video.mp4"):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(response.content)

def extract_audio_with_torchaudio(video_path, output_path="audio.wav"):
    waveform, sample_rate = torchaudio.load(video_path, format="mp4", normalize=True)
    waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
    torchaudio.save(output_path, waveform, 16000)

def transcribe_audio(audio_path):
    model = WhisperModel("base.en", compute_type="int8")
    segments, _ = model.transcribe(audio_path)
    return " ".join([seg.text for seg in segments])

def detect_accent(text):
    text = text.lower()
    keywords = {
        "British": ['mate', 'bloody', 'cheers', 'rubbish', 'loo'],
        "American": ['gonna', 'wanna', 'dude', 'awesome', 'y’all'],
        "Australian": ['heaps', 'no worries', 'arvo', 'mate', 'crikey']
    }

    for accent, words in keywords.items():
        if any(word in text for word in words):
            return accent, 85
    return "Uncertain", 50

st.title("🎙️ English Accent Detector")

url = st.text_input("Paste a direct link to an .mp4 video")

if st.button("Analyze") and url:
    file_name = f"{uuid.uuid4()}.mp4"
    try:
        st.info("⬇️ Downloading video...")
        download_video(url, file_name)
        st.success("Download complete!")

        st.info("🔊 Extracting audio...")
        extract_audio_with_torchaudio(file_name)
        st.success("Audio extracted!")

        st.info("🧠 Transcribing...")
        text = transcribe_audio("audio.wav")
        st.success("Transcription complete!")

        accent, confidence = detect_accent(text)
        st.markdown(f"### Accent: **{accent}**")
        st.markdown(f"**Confidence:** {confidence}%")
        st.text_area("Transcription", text)

    except Exception as e:
        st.error(f"🔥 Error: {e}")
    finally:
        if os.path.exists(file_name): os.remove(file_name)
        if os.path.exists("audio.wav"): os.remove("audio.wav")
