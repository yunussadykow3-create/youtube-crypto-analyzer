
from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id):
    languages = ["tr", "en", "ru"]

    try:
        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id,
            languages=languages
        )

        text = " ".join(
            item.text for item in transcript
        )

        if len(text.strip()) < 100:
            print("Altyazı çok kısa veya boş.")
            return None

        print("YouTube altyazısı başarıyla alındı.")
        return text

    except Exception as error:
        print("YouTube altyazısı alınamadı:", error)
        return None
