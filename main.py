
import os
import json
import urllib.request
import urllib.parse

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("YouTube API anahtarı bulunamadı.")

QUERIES = [
    ("crypto", "en"),
    ("Bitcoin cryptocurrency", "en"),
    ("криптовалюта", "ru"),
    ("Биткоин", "ru"),
    ("kripto para", "tr"),
    ("Bitcoin analiz", "tr")
]

videos = {}

def api_request(endpoint, params):
    params["key"] = API_KEY
    url = (
        "https://www.googleapis.com/youtube/v3/"
        + endpoint + "?"
        + urllib.parse.urlencode(params)
    )
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))

print("Kripto videolari araniyor...")

for query, language in QUERIES:
    page_token = None

    # Her arama için en fazla 3 sayfa
    for page in range(3):
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 50,
            "order": "viewCount",
            "relevanceLanguage": language
        }

        if page_token:
            params["pageToken"] = page_token

        result = api_request("search", params)

        ids = [
            item["id"]["videoId"]
            for item in result.get("items", [])
        ]

        for i in range(0, len(ids), 50):
            stats = api_request("videos", {
                "part": "snippet,statistics",
                "id": ",".join(ids[i:i+50])
            })

            for video in stats.get("items", []):
                video_id = video["id"]
                snippet = video["snippet"]
                statistics = video.get("statistics", {})

                videos[video_id] = {
                    "title": snippet["title"],
                    "channel": snippet["channelTitle"],
                    "views": int(statistics.get("viewCount", 0)),
                    "likes": int(statistics.get("likeCount", 0)),
                    "url": "https://www.youtube.com/watch?v=" + video_id
                }

        page_token = result.get("nextPageToken")
        if not page_token:
            break

print("\nEN COK IZLENEN 20 VIDEO\n")

top_views = sorted(
    videos.values(),
    key=lambda x: x["views"],
    reverse=True
)[:20]

for video in top_views:
    print(video["title"])
    print("Kanal:", video["channel"])
    print("Izlenme:", video["views"])
    print("Begeni:", video["likes"])
    print(video["url"])
    print("--------------------")

print("\nEN COK BEGENILEN 20 VIDEO\n")

top_likes = sorted(
    videos.values(),
    key=lambda x: x["likes"],
    reverse=True
)[:20]

for video in top_likes:
    print(video["title"])
    print("Kanal:", video["channel"])
    print("Izlenme:", video["views"])
    print("Begeni:", video["likes"])
    print(video["url"])
    print("--------------------")

print("\nToplam bulunan video:", len(videos))
