from faster_whisper import WhisperModel

AUDIO_FILE = "video_ilk_10_dakika.mp3"

print("Whisper modeli yükleniyor...")

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)

print("Ses yazıya çevriliyor...")

segments, info = model.transcribe(
    AUDIO_FILE,
    beam_size=1
)

text = " ".join(segment.text for segment in segments)

with open("video_transcript.txt", "w", encoding="utf-8") as file:
    file.write(text)

print("Transkripsiyon tamamlandı!")
print(text)
