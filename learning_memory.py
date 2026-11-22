import json
import os
from datetime import datetime, timezone

FILE = "learning_memory.json"


def save_learning(video, transcript):
    memory = []

    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
        except (json.JSONDecodeError, OSError):
            memory = []

    video_id = video["id"]

    # Aynı videoyu ikinci kez kaydetme
    if any(item["video_id"] == video_id for item in memory):
        return

    memory.append({
        "video_id": video_id,
        "title": video["title"],
        "channel": video["channel"],
        "transcript": transcript,
        "saved_at": datetime.now(timezone.utc).isoformat()
    })

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def load_learning():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
