import streamlit as st
import whisper
import requests
import av
import numpy as np
import tempfile

def download_video(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        st.error(f"فشل تحميل الفيديو: {e}")
        return None

def extract_audio_from_video(video_path):
    container = av.open(video_path)
    audio_stream = next((s for s in container.streams if s.type == 'audio'), None)
    if audio_stream is None:
        raise RuntimeError("لم يتم العثور على مسار صوتي في الفيديو")
    
    audio_frames = []
    for frame in container.decode(audio_stream):
        # تحويل الإطار الصوتي لمصفوفة numpy
        frame_array = frame.to_ndarray()
        audio_frames.append(frame_array)
    
    if not audio_frames:
        raise RuntimeError("لا توجد إطارات صوتية")
    
    # دمج كل إطارات الصوت في مصفوفة واحدة
    audio = np.concatenate(audio_frames, axis=1)  # axis=1 لأن الصوت في شكل (channels, samples)
    
    # لو الصوت ستيريو، نحول لمونو بأخذ متوسط القناتين
    if audio.shape[0] > 1:
        audio_mono = np.mean(audio, axis=0)
    else:
        audio_mono = audio[0]
    
    # whisper يتوقع float32 مع مدى -1.0 إلى 1.0
    audio_float32 = audio_mono.astype(np.float32) / 32768.0  # تحويل من int16 لو الصوت بصيغة 16bit
    
    return audio_float32

def transcribe_audio_array(audio_np, model):
    # whisper يقدر ياخد مصفوفة صوتية جاهزة، لكن لازم تتأكد إنها 16kHz
    # هنا نفترض ان الصوت من الفيديو أصلاً 16kHz أو نقوم بتحويله لو لازم
    result = model.transcribe(audio_np, fp16=False)
    return result['text']

st.title("English Accent Detector بدون FFmpeg")

video_url = st.text_input("أدخل رابط مباشر لفيديو MP4:")

if st.button("تحليل") and video_url:
    st.info("جار تحميل الفيديو...")
    video_file = download_video(video_url)
    if not video_file:
        st.stop()
    
    st.info("جار استخراج الصوت من الفيديو...")
    try:
        audio_np = extract_audio_from_video(video_file)
    except Exception as e:
        st.error(f"خطأ في استخراج الصوت: {e}")
        st.stop()
    st.success("تم استخراج الصوت!")

    st.info("جار التفريغ الصوتي...")
    try:
        model = whisper.load_model("base")
        transcription = model.transcribe(audio_np, fp16=False)
        text = transcription['text']
    except Exception as e:
        st.error(f"خطأ في التفريغ الصوتي: {e}")
        st.stop()
    st.success("تم التفريغ الصوتي!")

    # مثال بسيط لتحديد اللكنة (تقدر توسع القاعدة)
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

    accent, confidence = detect_accent(text)

    st.success(f"اللكنة: {accent}")
    st.write(f"الثقة: {confidence}%")
    st.write("النص المستخرج:")
    st.text(text)
