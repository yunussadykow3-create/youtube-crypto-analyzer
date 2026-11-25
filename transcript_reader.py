import os
import tempfile

from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel


def get_transcript(video_id):
    # 1. Önce YouTube altyazısını dene
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(
            video_id,
            languages=["tr", "en", "ru"]
        )

        text = " ".join(item.text for item in transcript)

        if len(text.strip()) >= 100:
            print("YouTube altyazısı başarıyla alındı.")
            return text

    except Exception as error:
        print("YouTube altyazısı alınamadı:", error)

    # 2. Altyazı yoksa videonun sesini indir
    try:
        with tempfile.TemporaryDirectory() as folder:
            options = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(folder, "audio.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }

            url = f"https://www.youtube.com/watch?v={video_id}"

            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_path = ydl.prepare_filename(info)

            if not os.path.exists(audio_path):
                raise RuntimeError("Ses dosyası bulunamadı.")

            # 3. Whisper ile sesi metne çevir
            model = WhisperModel(
                "tiny",
                device="cpu",
                compute_type="int8"
            )

            segments, info = model.transcribe(
                audio_path,
                beam_size=1
            )

            text = " ".join(
                segment.text for segment in segments
            ).strip()

            if len(text) < 100:
                print("Whisper metni çok kısa.")
                return None

            print("Whisper ile metin başarıyla oluşturuldu.")
            return text

    except Exception as error:
        print("Whisper ile dönüştürme başarısız:", error)
        return None
