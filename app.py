import streamlit as st
import requests
import whisper
import os
import uuid
import av

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
    try:
        container = av.open(video_path)
        audio_stream = next(s for s in container.streams if s.type == 'audio')

        resampler = av.audio.resampler.AudioResampler(format='s16', layout='mono', rate=16000)

        with open(audio_path, 'wb') as f:
            for frame in container.decode(audio_stream):
                frame = resampler.resample(frame)
                f.write(frame.planes[0].to_bytes())
    except Exception as e:
        st.error(f"حدث خطأ أثناء استخراج الصوت: {e}")
        raise

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def detect_accent(text):
    text = text.lower()
    # زيادة الكلمات عشان التعرف يكون أدق
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
    except:
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

    # تنظيف الملفات المؤقتة
    try:
        os.remove(video_filename)
        os.remove("audio.wav")
    except:
        pass
