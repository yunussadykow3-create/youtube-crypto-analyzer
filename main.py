import os
import json
import html
import urllib.parse
import urllib.request

API_KEY = os.getenv("YOUTUBE_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
    raise RuntimeError("GitHub Secrets eksik!")

QUERIES = [
    ("crypto", "en"),
    ("Bitcoin cryptocurrency", "en"),
    ("криптовалюта", "ru"),
    ("Биткоин", "ru"),
    ("kripto para", "tr"),
    ("Bitcoin analiz", "tr"),
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
        for page in range(3):
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "order": "viewCount",
                "maxResults": 50,
                "relevanceLanguage": language,
                "key": API_KEY,
            }

            if page > 0:
                break

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
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})

            videos.append({
                "id": item["id"],
                "title": snippet.get("title", "Başlık yok"),
                "channel": snippet.get("channelTitle", "Bilinmiyor"),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
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

def make_message(title, videos):
    lines = [title, ""]

    for number, video in enumerate(videos, 1):
        safe_title = html.escape(video["title"])
        safe_channel = html.escape(video["channel"])
        link = f"https://www.youtube.com/watch?v={video['id']}"

        lines.append(
            f"{number}. {safe_title}\n"
            f"📺 Kanal: {safe_channel}\n"
            f"👁 Görüntülenme: {video['views']:,}\n"
            f"👍 Beğeni: {video['likes']:,}\n"
            f"🔗 {link}\n"
        )

    return "\n".join(lines)

def main():
    videos = search_videos()

    if not videos:
        send_telegram("YouTube Crypto Analyzer: Video bulunamadı.")
        return

    top_views = sorted(
        videos, key=lambda x: x["views"], reverse=True
    )[:20]

    top_likes = sorted(
        videos, key=lambda x: x["likes"], reverse=True
    )[:20]

    send_telegram(
        make_message("🔥 EN ÇOK İZLENEN KRİPTO VİDEOLARI", top_views)
    )

    send_telegram(
        make_message("👍 EN ÇOK BEĞENİLEN KRİPTO VİDEOLARI", top_likes)
    )

    print(f"Analiz tamamlandı. Bulunan video sayısı: {len(videos)}")

if __name__ == "__main__":
    main()
