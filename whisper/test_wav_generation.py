import time
import numpy as np

#!/usr/bin/env python3
"""
Audio Device Selector GUI
A Tkinter GUI for selecting audio devices and managing callback-based audio streams.
"""

import os
from faster_whisper import WhisperModel
import numpy as np

model_size = "small"

os.add_dll_directory(
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.9\\bin"
)
os.add_dll_directory("C:\\Program Files\\NVIDIA\\CUDNN\\v9.10\\bin\\11.8")

def test_wav_file_sounds_correct():
    whisper_model = WhisperModel(
                    model_size, device="cuda", compute_type="float32"
                )

    segments, info = whisper_model.transcribe(
                            "test files\Abide with Me\Abide_With_Me_Guitar_and_Vox.mp3",
                            beam_size=1,  # Faster processing
                            best_of=1,
                            temperature=0.0,
                            vad_filter=True,  # Voice activity detection
                            vad_parameters=dict(min_silence_duration_ms=1000),
                        )
    

    transcription_text = ""

    start_time = time.time()
    for segment in segments:
        transcription_text += segment.text.strip()
    stop_time = time.time()

    elapsed_time = stop_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    print(transcription_text)
    assert "I need thy presence" in transcription_text