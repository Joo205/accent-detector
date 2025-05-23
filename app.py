import streamlit as st
import requests
import whisper
import os
import uuid
import av  # PyAV library

def download_video(url, filename="input_video.mp4"):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def extract_audio_with_pyav(video_path, audio_path="audio.wav"):
    container = av.open(video_path)
    audio_stream = None
    for stream in container.streams:
        if stream.type == 'audio':
            audio_stream = stream
            break
    if audio_stream is None:
        raise ValueError("الفيديو لا يحتوي على مسار صوتي")

    output = av.open(audio_path, mode='w')
    output_stream = output.add_stream('pcm_s16le', rate=16000)
    output_stream.channels = 1

    for packet in container.demux(audio_stream):
        for frame in packet.decode():
            frame.pts = None
            frame.sample_rate = 16000
            frame.layout = 'mono'
            new_packet = output_stream.encode(frame)
            if new_packet:
                output.mux(new_packet)

    # Flush stream
    new_packet = output_stream.encode(None)
    if new_packet:
        output.mux(new_packet)
    output.close()

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

    try:
        st.info("Extracting audio...")
        extract_audio_with_pyav(video_filename)
        st.success("Audio extraction done!")

        st.info("Starting transcription...")
        transcription = transcribe_audio("audio.wav")
        st.success("Transcription done!")

        accent, confidence = detect_accent(transcription)

        st.success(f"Accent: {accent}")
        st.write(f"Confidence: {confidence}%")
        st.write("Transcription:")
        st.text(transcription)

    except Exception as e:
        st.error(f"Error: {e}")
