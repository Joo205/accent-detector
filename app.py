import streamlit as st
import requests
import uuid
import os
import wave
import av
from faster_whisper import WhisperModel

def download_video(url, filename="input.mp4"):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filename
    except Exception as e:
        st.error(f"خطأ في تحميل الفيديو: {e}")
        return None

def extract_audio_with_av(input_path, output_path="output.wav"):
    container = av.open(input_path)
    audio_stream = container.streams.audio[0]
    output = wave.open(output_path, 'wb')
    output.setnchannels(1)
    output.setsampwidth(2)
    output.setframerate(16000)

    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono",
        rate=16000
    )

    for frame in container.decode(audio=0):
        frame = resampler.resample(frame)
        audio_bytes = frame.to_ndarray().tobytes()
        output.writeframes(audio_bytes)

    output.close()

def transcribe_audio(audio_path):
    model = WhisperModel("base", compute_type="cpu")
    segments, _ = model.transcribe(audio_path)
    return " ".join([segment.text for segment in segments])

def detect_accent(text):
    text = text.lower()
    if any(word in text for word in ['mate', 'bloody', 'cheers', 'innit', 'loo']):
        return "British", 90
    elif any(word in text for word in ['gonna', 'wanna', 'dude', 'awesome', 'bro']):
        return "American", 85
    elif any(word in text for word in ['no worries', 'heaps', 'arvo', 'crikey']):
        return "Australian", 80
    else:
        return "Uncertain", 50

# Streamlit UI
st.title("🎙️ English Accent Detector")

video_url = st.text_input("Enter direct .mp4 video URL:")

if st.button("Analyze") and video_url:
    st.info("📥 Downloading video...")
    video_file = f"{uuid.uuid4()}.mp4"
    if download_video(video_url, video_file):
        st.success("✅ Video downloaded successfully.")

        st.info("🎧 Extracting audio...")
        audio_file = f"{uuid.uuid4()}.wav"
        try:
            extract_audio_with_av(video_file, audio_file)
            st.success("✅ Audio extracted successfully.")
        except Exception as e:
            st.error(f"خطأ في استخراج الصوت: {e}")
            st.stop()

        st.info("🧠 Transcribing audio...")
        try:
            transcription = transcribe_audio(audio_file)
            st.success("✅ Transcription completed.")
        except Exception as e:
            st.error(f"خطأ في التفريغ الصوتي: {e}")
            st.stop()

        accent, confidence = detect_accent(transcription)

        st.markdown(f"### 🎯 Accent: `{accent}`")
        st.markdown(f"**Confidence**: {confidence}%")
        st.markdown("**Transcription:**")
        st.text(transcription)

        # Clean up
        os.remove(video_file)
        os.remove(audio_file)
