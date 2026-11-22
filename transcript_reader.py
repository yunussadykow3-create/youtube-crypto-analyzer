from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id,
            languages=["tr", "en", "ru"]
        )

        return " ".join(
            item.text for item in transcript
        )

    except Exception as error:
        print("Altyazı alınamadı:", error)
        return None
