import os
import yt_dlp
from faster_whisper import WhisperModel

VIDEO_URL = os.getenv("YOUTUBE_URL")

if not VIDEO_URL:
    raise ValueError("YouTube video adresi girilmedi.")

print("Video sesi alınıyor...")

options = {
    "format": "bestaudio/best",
    "outtmpl": "audio.%(ext)s",
    "quiet": True
}

with yt_dlp.YoutubeDL(options) as ydl:
    ydl.download([VIDEO_URL])

audio_file = next(
    f for f in os.listdir(".")
    if f.startswith("audio.")
)

print("Konuşma yazıya çevriliyor...")

model = WhisperModel("small", device="cpu", compute_type="int8")

segments, info = model.transcribe(
    audio_file,
    beam_size=5,
    language=None
)

with open("transcript.txt", "w", encoding="utf-8") as file:
    file.write(f"Algılanan dil: {info.language}\n\n")

    for segment in segments:
        file.write(segment.text + "\n")

print("Altyazı oluşturuldu: transcript.txt")
