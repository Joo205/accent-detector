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
    # مش ممكن نغير channels مباشر، فلازم نمشي كده

    for packet in container.demux(audio_stream):
        for frame in packet.decode():
            frame.pts = None
            frame.sample_rate = 16000
            frame.layout = 'mono'  # يحول للصوت مونو لو مش كده أصلاً
            new_packet = output_stream.encode(frame)
            if new_packet:
                output.mux(new_packet)

    # Flush
    new_packet = output_stream.encode(None)
    if new_packet:
        output.mux(new_packet)
    out
