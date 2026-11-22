
import os
from learning_memory import save_learning

FOLDER = "transcripts"


def learn_from_files():
    os.makedirs(FOLDER, exist_ok=True)

    files = [
        name for name in os.listdir(FOLDER)
        if name.endswith(".txt")
    ]

    learned = 0

    for filename in files:
        path = os.path.join(FOLDER, filename)

        with open(path, "r", encoding="utf-8") as file:
            transcript = file.read().strip()

        if len(transcript) < 100:
            continue

        video = {
            "id": "manual_" + filename,
            "title": os.path.splitext(filename)[0],
            "channel": "Kullanıcı tarafından sağlanan",
        }

        save_learning(video, transcript)
        learned += 1

    print(f"Öğrenilen altyazı dosyası: {learned}")


if __name__ == "__main__":
    learn_from_files()
