
import os
import json
import urllib.parse
import urllib.request

from transcript_reader import get_transcript
from learning_memory import save_learning
from manual_learning import learn_from_files

API_KEY = os.getenv("YOUTUBE_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
    raise RuntimeError("GitHub Secrets eksik!")

QUERIES = [
    ("crypto Bitcoin analysis", "en"),
    ("Bitcoin technical analysis", "en"),
    ("криптовалюта анализ Bitcoin", "ru"),
    ("Биткоин технический анализ", "ru"),
    ("kripto para Bitcoin analizi", "tr"),
    ("Bitcoin grafik analizi", "tr"),
]

def api_get(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "YouTubeCryptoAnalyzer"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def search_videos():
    video_ids = set()

    for query, language in QUERIES:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "maxResults": 20,
            "relevanceLanguage": language,
            "key": API_KEY,
        }

        url = (
            "https://www.googleapis.com/youtube/v3/search?"
            + urllib.parse.urlencode(params)
        )
        data = api_get(url)

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if video_id:
                video_ids.add(video_id)

    videos = []
    ids = list(video_ids)

    for start in range(0, len(ids), 50):
        batch = ids[start:start + 50]
        params = {
            "part": "snippet,statistics",
            "id": ",".join(batch),
            "key": API_KEY,
        }
        url = (
            "https://www.googleapis.com/youtube/v3/videos?"
            + urllib.parse.urlencode(params)
        )
        data = api_get(url)

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})

            videos.append({
                "id": item["id"],
                "title": snippet.get("title", "Başlık yok"),
                "channel": snippet.get("channelTitle", "Bilinmiyor"),
                "views": int(stats.get("viewCount", 0)),
            })

    return videos

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
    }

    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError("Telegram mesajı gönderilemedi!")

def main():
    learn_from_files()
    videos = search_videos()

    if not videos:
        send_telegram("Video bulunamadı.")
        return

    # İzlenme sayısına göre ilk 10 videoyu incele
    selected = sorted(
        videos,
        key=lambda video: video["views"],
        reverse=True
    )[:10]

    learned = 0
    failed = 0

    for video in selected:
        print("Video inceleniyor:", video["title"])

        transcript = get_transcript(video["id"])

        if transcript and len(transcript.strip()) > 100:
            save_learning(video, transcript)
            learned += 1
            print("Altyazı kaydedildi.")
        else:
            failed += 1
            print("Altyazı bulunamadı veya çok kısa.")

    send_telegram(
        "🧠 YouTube öğrenme çalışması tamamlandı.\n\n"
        f"🔎 İncelenen video: {len(selected)}\n"
        f"📚 Altyazısı kaydedilen: {learned}\n"
        f"⚠️ Altyazısı alınamayan: {failed}\n\n"
        "Not: Bu aşamada bot henüz alım-satım yapmaz."
    )

    print("Öğrenme çalışması tamamlandı.")

if __name__ == "__main__":
    main()
