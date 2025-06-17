import time
import whisper

model = whisper.load_model("turbo")

# timer
print("starting transcription")
start_time = time.time()
result = model.transcribe("test files\Abide with Me\Abide_With_Me_Guitar_and_Vox.mp3", fp16=False, language="en")

stop_time = time.time()

elapsed_time = stop_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")
print(result["text"])