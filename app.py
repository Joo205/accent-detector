import os
import requests
import streamlit as st
from moviepy.editor import VideoFileClip
import whisper

# ====== Streamlit App Title ======
st.title("Accent Analyzer")
st.markdown("Upload a public MP4 video URL. The tool will extract audio, transcribe it, and detect the English accent.")

# ====== Inputs ======
video_url = st.text_input("Paste a public MP4 video URL here:")

if st.button("Analyze") and video_url:
    VIDEO_PATH = "video.mp4"
    AUDIO_PATH = "audio.wav"

    # ====== Download video ======
    with st.spinner("Downloading video..."):
        response = requests.get(video_url)
        with open(VIDEO_PATH, "wb") as f:
            f.write(response.content)

    # ====== Extract audio ======
    with st.spinner("Extracting audio..."):
        video = VideoFileClip(VIDEO_PATH)
        video.audio.write_audiofile(AUDIO_PATH)

    # ====== Transcribe audio ======
    with st.spinner("Transcribing audio..."):
        model = whisper.load_model("base")
        result = model.transcribe(AUDIO_PATH)
        transcript = result["text"]

    # ====== Analyze Accent ======
    def classify_accent(text):
        american_words = {"gonna", "wanna", "gotten", "kinda", "y'all"}
        british_words = {"whilst", "flat", "lorry", "mate", "rubbish"}
        australian_words = {"arvo", "bikkie", "brekkie", "g'day", "bogan"}

        text_lower = text.lower()

        def count_hits(word_set):
            return sum(word in text_lower for word in word_set)

        scores = {
            "American": count_hits(american_words),
            "British": count_hits(british_words),
            "Australian": count_hits(australian_words)
        }

        detected = max(scores, key=scores.get)
        confidence = int((scores[detected] / max(1, sum(scores.values()))) * 100)

        return detected, confidence

    accent, confidence = classify_accent(transcript)

    # ====== Display results ======
    st.subheader("Results")
    st.write(f"**Detected Accent:** {accent}")
    st.write(f"**Confidence Score:** {confidence}%")
    st.write("**Transcript:**")
    st.text(transcript)

    # ====== Cleanup (Optional) ======
    os.remove(VIDEO_PATH)
    os.remove(AUDIO_PATH)
