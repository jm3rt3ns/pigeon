#!/usr/bin/env python3
"""
Audio Device Selector GUI
A Tkinter GUI for selecting audio devices and managing callback-based audio streams.
"""

import io
import os
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import wave
from faster_whisper import WhisperModel
import pyaudio
import numpy as np
import threading
import time
from queue import Queue, Empty


def save_as_wav(wav_file, audio_chunk, sample_rate, channels, logger=print):
    logger("opening wave file")
    wav_writer = wave.open(wav_file, "wb")
    try:
        wav_writer.setframerate(sample_rate)
        wav_writer.setsampwidth(1)  # this is a magic number
        wav_writer.setnchannels(channels)
        wav_writer.writeframes(audio_chunk)
        wav_file.flush()
    finally:
        wav_writer.close()

    logger("saving the wav file")
    wav_file.seek(0)

    with open("temp.wav", "wb") as f:
        f.write(wav_file.read())
    wav_file.seek(0)


model_size = "small"

os.add_dll_directory(
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.9\\bin"
)
os.add_dll_directory("C:\\Program Files\\NVIDIA\\CUDNN\\v9.10\\bin\\11.8")


class AudioDeviceGUI:
    """Audio Device Selection and Streaming GUI Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Audio Device Selector")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Audio setup
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.devices = []
        self.audio_data = []
        self.stream_thread = None
        self.stop_streaming = False

        # Transcription setup
        self.whisper_model = None
        self.transcription_queue = queue.Queue()
        self.transcription_thread = None
        self.audio_buffer = []
        self.buffer_duration = 50.0  # seconds of audio to buffer before transcription
        self.sample_rate = 16000  # Whisper prefers 16kHz
        self.channels = 1
        self.transcription_active = False
        self.selected_device_index = -1
        self.is_streaming = False
        self.stop_streaming = False
        self.audio_data = []
        self.stream_thread = None
        self.volume_level = 0.0
        self.transcribed_text = []

        # Queue for thread-safe GUI updates
        self.update_queue = Queue()

        # Setup GUI
        self.setup_gui()
        self.refresh_devices()

        # Start the GUI update loop
        self.update_gui()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.initialize_whisper()

    def initialize_whisper(self) -> None:
        """Initialize the Whisper model in a separate thread"""

        def load_model():
            try:
                self.log_message("Loading Whisper model (this may take a moment)...")
                # self.query_one("#transcription_status", Static).update("Loading Whisper model...")

                # Use base model for faster processing, change to "small" or "medium" for better accuracy
                self.whisper_model = WhisperModel(
                    model_size, device="cuda", compute_type="float32"
                )

                self.log_message("Whisper model loaded successfully")
                # self.query_one("#transcription_status", Static).update("Transcription: Ready (Disabled)")

            except Exception as e:
                self.log_message(f"Error loading Whisper model: {e}")
                # self.query_one("#transcription_status", Static).update("Transcription: Error loading model")

        # Load model in background thread
        model_thread = threading.Thread(target=load_model, daemon=True)
        model_thread.start()

    def setup_gui(self):
        """Create the GUI layout"""
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Device selection tab
        device_frame = ttk.Frame(notebook)
        notebook.add(device_frame, text="Device Selection")

        # Device list
        ttk.Label(
            device_frame, text="Available Audio Devices:", font=("Arial", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))

        # Treeview for device list
        columns = ("ID", "Name", "Input Ch", "Output Ch", "Sample Rate", "Type")
        self.device_tree = ttk.Treeview(
            device_frame, columns=columns, show="headings", height=12
        )

        # Configure columns
        self.device_tree.heading("ID", text="ID")
        self.device_tree.heading("Name", text="Device Name")
        self.device_tree.heading("Input Ch", text="Input Ch")
        self.device_tree.heading("Output Ch", text="Output Ch")
        self.device_tree.heading("Sample Rate", text="Sample Rate")
        self.device_tree.heading("Type", text="Type")

        self.device_tree.column("ID", width=40)
        self.device_tree.column("Name", width=300)
        self.device_tree.column("Input Ch", width=80)
        self.device_tree.column("Output Ch", width=80)
        self.device_tree.column("Sample Rate", width=100)
        self.device_tree.column("Type", width=80)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(
            device_frame, orient=tk.VERTICAL, command=self.device_tree.yview
        )
        self.device_tree.configure(yscrollcommand=scrollbar.set)

        tree_frame = ttk.Frame(device_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.device_tree.bind("<<TreeviewSelect>>", self.on_device_select)

        # Refresh button
        ttk.Button(
            device_frame, text="Refresh Devices", command=self.refresh_devices
        ).pack(pady=5)

        # Selected device info
        info_frame = ttk.LabelFrame(
            device_frame, text="Selected Device Information", padding=10
        )
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.device_info = scrolledtext.ScrolledText(info_frame, height=8, wrap=tk.WORD)
        self.device_info.pack(fill=tk.BOTH, expand=True)
        self.device_info.insert(tk.END, "No device selected")
        self.device_info.config(state=tk.DISABLED)

        # Control tab
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Stream Control")

        # Stream controls
        control_group = ttk.LabelFrame(
            control_frame, text="Stream Controls", padding=10
        )
        control_group.pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(control_group)
        button_frame.pack(fill=tk.X)

        self.stream_button = ttk.Button(
            button_frame, text="Start Stream", command=self.toggle_stream
        )
        self.stream_button.pack(side=tk.LEFT, padx=(0, 10))

        self.monitor_var = tk.BooleanVar()
        ttk.Checkbutton(
            button_frame, text="Enable Audio Monitoring", variable=self.monitor_var
        ).pack(side=tk.LEFT)

        # Status
        status_frame = ttk.Frame(control_group)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))

        # Volume level
        volume_group = ttk.LabelFrame(control_frame, text="Audio Level", padding=10)
        volume_group.pack(fill=tk.X, pady=(0, 10))

        volume_frame = ttk.Frame(volume_group)
        volume_frame.pack(fill=tk.X)

        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT)

        self.volume_var = tk.DoubleVar()
        self.volume_progress = ttk.Progressbar(
            volume_frame, variable=self.volume_var, maximum=100, length=300
        )
        self.volume_progress.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)

        self.volume_label = ttk.Label(volume_frame, text="0%")
        self.volume_label.pack(side=tk.LEFT)

        # Stream settings
        settings_group = ttk.LabelFrame(
            control_frame, text="Stream Settings", padding=10
        )
        settings_group.pack(fill=tk.X, pady=(0, 10))

        # Chunk size
        chunk_frame = ttk.Frame(settings_group)
        chunk_frame.pack(fill=tk.X, pady=2)
        ttk.Label(chunk_frame, text="Chunk Size:").pack(side=tk.LEFT)
        self.chunk_var = tk.StringVar(value="1024")
        chunk_combo = ttk.Combobox(
            chunk_frame,
            textvariable=self.chunk_var,
            values=["256", "512", "1024", "2048", "4096"],
            width=10,
        )
        chunk_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Sample rate override
        rate_frame = ttk.Frame(settings_group)
        rate_frame.pack(fill=tk.X, pady=2)
        ttk.Label(rate_frame, text="Sample Rate:").pack(side=tk.LEFT)
        self.rate_var = tk.StringVar(value="Auto")
        rate_combo = ttk.Combobox(
            rate_frame,
            textvariable=self.rate_var,
            values=["Auto", "8000", "16000", "22050", "44100", "48000", "96000"],
            width=10,
        )
        rate_combo.pack(side=tk.LEFT, padx=(10, 0))

        # transcription
        transcription_group = ttk.LabelFrame(
            control_frame, text="Live Transcription", padding=10
        )
        transcription_group.pack(fill=tk.X, pady=(0, 10))

        text_frame = ttk.Frame(transcription_group)
        text_frame.pack(fill=tk.X, pady=2)
        ttk.Label(text_frame, text="Text").pack(side=tk.LEFT)
        self.status_label = ttk.Label(text_frame, text="Ready", foreground="green")

        # Log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Log")

        # Log area
        ttk.Label(log_frame, text="Application Log:", font=("Arial", 12, "bold")).pack(
            anchor=tk.W, pady=(0, 5)
        )

        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Log controls
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(log_control_frame, text="Clear Log", command=self.clear_log).pack(
            side=tk.LEFT
        )
        ttk.Button(log_control_frame, text="Save Log", command=self.save_log).pack(
            side=tk.LEFT, padx=(10, 0)
        )

    def refresh_devices(self):
        """Refresh the list of available audio devices"""
        try:
            # Clear existing items
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)

            self.devices = []
            device_count = self.pa.get_device_count()

            for i in range(device_count):
                try:
                    info = self.pa.get_device_info_by_index(i)
                    device_type = []
                    if info["maxInputChannels"] > 0:
                        device_type.append("Input")
                    if info["maxOutputChannels"] > 0:
                        device_type.append("Output")

                    self.devices.append(info)

                    # Add to treeview
                    self.device_tree.insert(
                        "",
                        tk.END,
                        values=(
                            str(i),
                            info["name"][:50],  # Truncate long names
                            str(info["maxInputChannels"]),
                            str(info["maxOutputChannels"]),
                            f"{int(info['defaultSampleRate'])} Hz",
                            "/".join(device_type),
                        ),
                    )

                except Exception as e:
                    self.log_message(f"Error getting device {i}: {e}")

            self.log_message(f"Found {len(self.devices)} audio devices")

        except Exception as e:
            self.log_message(f"Error refreshing devices: {e}")
            messagebox.showerror("Error", f"Failed to refresh devices: {e}")

    def on_device_select(self, event):
        """Handle device selection"""
        selection = self.device_tree.selection()
        if selection:
            item = self.device_tree.item(selection[0])
            device_id = int(item["values"][0])

            if device_id < len(self.devices):
                self.selected_device_index = device_id
                self.update_device_info()
                self.log_message(
                    f"Selected device {device_id}: {self.devices[device_id]['name']}"
                )

    def update_device_info(self):
        """Update the selected device information display"""
        self.device_info.config(state=tk.NORMAL)
        self.device_info.delete(1.0, tk.END)

        if self.selected_device_index >= 0 and self.selected_device_index < len(
            self.devices
        ):
            device_info = self.devices[self.selected_device_index]
            info_text = f"""Device Name: {device_info['name']}
Device Index: {device_info['index']}
Host API Index: {device_info['hostApi']}
Max Input Channels: {device_info['maxInputChannels']}
Max Output Channels: {device_info['maxOutputChannels']}
Default Sample Rate: {int(device_info['defaultSampleRate'])} Hz
Default Low Input Latency: {device_info.get('defaultLowInputLatency', 'N/A'):.4f} s
Default Low Output Latency: {device_info.get('defaultLowOutputLatency', 'N/A'):.4f} s
Default High Input Latency: {device_info.get('defaultHighInputLatency', 'N/A'):.4f} s
Default High Output Latency: {device_info.get('defaultHighOutputLatency', 'N/A'):.4f} s

Capabilities:
- Input Capable: {'Yes' if device_info['maxInputChannels'] > 0 else 'No'}
- Output Capable: {'Yes' if device_info['maxOutputChannels'] > 0 else 'No'}
- Suitable for Streaming: {'Yes' if device_info['maxInputChannels'] > 0 else 'No (No input channels)'}"""

            self.device_info.insert(tk.END, info_text)
        else:
            self.device_info.insert(tk.END, "No device selected")

        self.device_info.config(state=tk.DISABLED)

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback function"""
        if status:
            self.log_message(f"Audio callback status: {status}")

        # Convert audio data to numpy array for processing
        if in_data:
            # For volume monitoring (original format)
            audio_array = np.frombuffer(in_data, dtype=np.float32)

            # Calculate volume level (RMS)
            if len(audio_array) > 0:
                rms = np.sqrt(np.mean(audio_array**2))
                self.volume_level = min(rms * 1000, 100)  # Scale and cap at 100

            # Store recent audio data for monitoring
            self.audio_data.append(audio_array)
            if len(self.audio_data) > 10:  # Keep only recent data
                self.audio_data.pop(0)

            # Calculate volume level (RMS)
            if len(audio_array) > 0:
                rms = np.sqrt(np.mean(audio_array**2))
                volume_percent = min(rms * 1000, 100)  # Scale and cap at 100
                self.update_queue.put(("volume", volume_percent))

            # For transcription - resample to 16kHz mono if transcription is enabled
            if self.transcription_active:
                # Convert to mono if stereo
                if len(audio_array.shape) > 1 or self.channels > 1:
                    audio_mono = np.mean(audio_array.reshape(-1, self.channels), axis=1)
                else:
                    audio_mono = audio_array

                # Add to transcription buffer
                self.audio_buffer.extend(audio_mono)

                # Check if we have enough audio for transcription
                buffer_samples = int(self.buffer_duration * self.sample_rate)
                if len(self.audio_buffer) >= buffer_samples:
                    # Send audio chunk for transcription
                    audio_chunk = np.array(
                        self.audio_buffer[:buffer_samples], dtype=np.float32
                    )
                    self.log_message("about to put audio chunk in queue")
                    try:
                        self.transcription_queue.put_nowait(audio_chunk)
                    except queue.Full:
                        self.log_message("Queue is full")
                        pass  # Skip if queue is full

                    # Keep some overlap for context
                    overlap_samples = buffer_samples // 4
                    self.audio_buffer = self.audio_buffer[
                        buffer_samples - overlap_samples :
                    ]

        return (in_data, pyaudio.paContinue)

    def start_transcription(self) -> None:
        """Start the transcription processing thread"""
        if not self.whisper_model:
            self.log_message("Whisper model not loaded!")
            return

        self.transcription_active = True

        def transcription_worker():
            """Process audio chunks for transcription"""
            while self.transcription_active:
                try:
                    # Get audio chunk from queue (with timeout)
                    audio_chunk = self.transcription_queue.get(timeout=2.0)
                    self.log_message("Getting from queue!")

                    if audio_chunk is not None and len(audio_chunk) > 0:
                        self.log_message("Transcribing...")
                        # Normalize audio
                        # audio_chunk = audio_chunk / np.max(np.abs(audio_chunk) + 1e-10)

                        # with io.BytesIO() as wav_file:
                        #     save_as_wav(
                        #         wav_file,
                        #         audio_chunk,
                        #         self.sample_rate,
                        #         self.channels,
                        #         self.logger,
                        #     )

                        self.log_message("about to start transciption")

                        # Transcribe audio
                        segments, info = self.whisper_model.transcribe(
                            audio_chunk,
                            beam_size=1,  # Faster processing
                            best_of=1,
                            temperature=0.0,
                            vad_filter=True,  # Voice activity detection
                            # vad_parameters=dict(min_silence_duration_ms=1000),
                        )

                        # Collect transcription text
                        transcription_text = ""
                        for segment in segments:
                            transcription_text += segment.text.strip()

                        self.log_message(f"Transcribed Text: {transcription_text}")

                        if transcription_text.strip():
                            # Update transcription display
                            # self.update_transcription_display(transcription_text.strip())
                            self.transcribed_text.append(transcription_text.strip())
                            self.log_message(
                                f"Transcribed: {transcription_text.strip()}"
                            )

                except queue.Empty:
                    self.log_message("...")
                    continue  # Timeout, check if still active
                except Exception as e:
                    self.log_message(f"Transcription error: {e}")
                    continue

        self.transcription_thread = threading.Thread(
            target=transcription_worker, daemon=True
        )
        self.transcription_thread.start()

        # TODO: show when transcription starts self.query_one("#transcription_status", Static).update("Transcription: Active")
        self.log_message("Transcription started")

    def toggle_stream(self):
        """Toggle the audio stream on/off"""
        if self.is_streaming:
            self.stop_stream()
        else:
            self.start_stream()
            self.start_transcription()

    def start_stream(self):
        """Start the audio stream"""
        if self.selected_device_index < 0:
            messagebox.showwarning("No Device", "Please select an audio device first!")
            return False

        if self.is_streaming:
            self.log_message("Stream already running!")
            return False

        try:
            device_info = self.devices[self.selected_device_index]

            # Check if device supports input
            if device_info["maxInputChannels"] == 0:
                messagebox.showerror(
                    "Invalid Device", "Selected device doesn't support audio input!"
                )
                return False

            # Stream parameters
            try:
                chunk_size = int(self.chunk_var.get())
            except ValueError:
                chunk_size = 1024

            if self.rate_var.get() == "Auto":
                sample_rate = int(device_info["defaultSampleRate"])
            else:
                try:
                    sample_rate = int(self.rate_var.get())
                except ValueError:
                    sample_rate = int(device_info["defaultSampleRate"])

            channels = min(device_info["maxInputChannels"], 2)  # Use max 2 channels

            self.stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=sample_rate,
                input=True,
                input_device_index=self.selected_device_index,
                frames_per_buffer=chunk_size,
                stream_callback=self.audio_callback,
            )

            self.stream.start_stream()
            self.is_streaming = True
            self.stop_streaming = False

            # Update UI
            self.stream_button.config(text="Stop Stream")
            self.status_label.config(text="Streaming...", foreground="red")

            self.log_message(
                f"Started stream: {sample_rate}Hz, {channels}ch, {chunk_size} frames"
            )
            return True

        except Exception as e:
            self.log_message(f"Error starting stream: {e}")
            messagebox.showerror("Stream Error", f"Failed to start stream:\n{e}")
            return False

    def stop_stream(self):
        """Stop the audio stream"""
        try:
            self.stop_streaming = True

            if self.stream and self.stream.is_active():
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

            self.is_streaming = False

            # Update UI
            self.stream_button.config(text="Start Stream")
            self.status_label.config(text="Ready", foreground="green")
            self.volume_var.set(0)
            self.volume_label.config(text="0%")

            self.log_message("Stream stopped")

        except Exception as e:
            self.log_message(f"Error stopping stream: {e}")

    def update_gui(self):
        """Update GUI elements from the queue (thread-safe)"""
        try:
            while True:
                update_type, data = self.update_queue.get_nowait()

                if update_type == "volume":
                    self.volume_var.set(data)
                    self.volume_label.config(text=f"{data:.1f}%")
                elif update_type == "log":
                    self.log_message(data)

        except Empty:
            pass

        # Schedule next update
        self.root.after(50, self.update_gui)  # Update every 50ms

    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)

    def save_log(self):
        """Save log to file"""
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if filename:
            try:
                with open(filename, "w") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")

    def on_closing(self):
        """Handle application closing"""
        if self.is_streaming:
            self.stop_stream()

        try:
            if self.pa:
                self.pa.terminate()
        except:
            pass

        self.root.destroy()


def main():
    """Run the application"""
    try:
        root = tk.Tk()
        app = AudioDeviceGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Error running application: {e}")
        messagebox.showerror("Fatal Error", f"Application error: {e}")


if __name__ == "__main__":
    main()
