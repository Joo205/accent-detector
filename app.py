import streamlit as st
import av
import whisper
import os
import uuid

def extract_audio_from_video(video_path, audio_path="audio.wav"):
    try:
        container = av.open(video_path)
        stream = next(s for s in container.streams if s.type == 'audio')
        with open(audio_path, "wb") as f:
            for frame in container.decode(stream):
                f.write(frame.to_ndarray().tobytes())
        return audio_path
    except Exception as e:
        st.error(f"خطأ في استخراج الصوت من الفيديو: {e}")
        return None

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def detect_accent(text):
    text = text.lower()
    if any(word in text for word in ["mate", "bloody", "cheers"]):
        return "British", 85
    elif any(word in text for word in ["gonna", "wanna", "dude"]):
        return "American", 90
    elif any(word in text for word in ["no worries", "mate", "heaps"]):
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
        import requests
        r = requests.get(video_url, timeout=15)
        r.raise_for_status()
        with open(video_filename, "wb") as f:
            f.write(r.content)
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        st.stop()

    st.info("Extracting audio...")
    audio_file = extract_audio_from_video(video_filename, audio_filename)
    if audio_file is None:
        st.stop()
    st.success("Audio extraction done!")

    st.info("Starting transcription...")
    try:
        transcription = transcribe_audio(audio_filename)
    except Exception as e:
        st.error(f"خطأ في التفريغ الصوتي: {e}")
        st.stop()
    st.success("Transcription done!")

    accent, confidence = detect_accent(transcription)
    st.success(f"Accent: {accent}")
    st.write(f"Confidence: {confidence}%")
    st.write("Transcription:")
    st.text(transcription)

    # Clean up temp files
    try:
        os.remove(video_filename)
        os.remove(audio_filename)
    except:
        pass
