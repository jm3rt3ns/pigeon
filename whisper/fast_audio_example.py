import io
from faster_whisper import WhisperModel
import time

model_size = "large-v3"
import os
import wave
import sys

import pyaudio

SKIP_MODEL = False
DEBUG = False
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == "darwin" else 2
RATE = 44100
RECORD_SECONDS = 5

os.add_dll_directory(
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.9\\bin"
)
os.add_dll_directory("C:\\Program Files\\NVIDIA\\CUDNN\\v9.10\\bin\\11.8")
# C:\Program Files\NVIDIA\CUDNN\v9.10\bin\12.9
# Run on GPU with FP16
if not SKIP_MODEL:
    model = WhisperModel(model_size, device="cuda", compute_type="float32")
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

temp_chunk = io.BytesIO()
start_time = time.time()
current_time = start_time
five_seconds = 5


def process_audio_chunk(input_bytes):
    input_bytes.seek(0)
    start_time = time.time()
    # convert incoming data to whisper-friendly format:
    with io.BytesIO() as wav_file:
        wav_writer = wave.open(wav_file, "wb")
        try:
            wav_writer.setframerate(RATE)
            wav_writer.setsampwidth(2) # this is a magic number
            wav_writer.setnchannels(CHANNELS)
            wav_writer.writeframes(input_bytes.read())
            wav_file.flush()
        finally:
            wav_writer.close()

        wav_file.seek(0)

        if DEBUG:
            with open("temp.wav", "wb") as f:
                f.write(wav_file.read())
            wav_file.seek(0)

        if not SKIP_MODEL:
            result = model.transcribe(
                wav_file,
                language="en",
            )
            segments = result[0]

            for segment in segments:
                print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            stop_time = time.time()
            elapsed_time = stop_time - start_time
            print(f"Elapsed time: {elapsed_time:.2f} seconds")


previous_time = time.time()
current_time = time.time()


def callback(in_data, frame_count, time_info, status):
    # save off the new chunk of temp audio
    global previous_time
    global current_time
    global temp_chunk

    current_time = time.time()

    temp_chunk.write(in_data)
    # check whether 5 seconds has passed
    delta = abs(current_time - previous_time)
    if delta > five_seconds:
        print("processing")
        process_audio_chunk(temp_chunk)
        temp_chunk.truncate()
        # update the "previous time" so that we wait another interval
        previous_time = current_time
    return (None, pyaudio.paContinue)


p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    stream_callback=callback,
)

# Wait for stream to finish (4)
while stream.is_active():
    time.sleep(5)

# Close the stream (5)
stream.close()

# Release PortAudio system resources (6)
p.terminate()
