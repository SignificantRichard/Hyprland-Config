import queue
import sys
import threading
import time
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

TARGET_SAMPLE_RATE = 16000
BLOCK_SIZE = 2048

def get_native_sample_rate():
    try:
        default_device = sd.default.device[0]
        device_info = sd.query_devices(default_device, 'input')
        return int(device_info['default_samplerate'])
    except Exception:
        return 44100

NATIVE_SAMPLE_RATE = get_native_sample_rate()

def resample_audio(audio_data, original_sr, target_sr):
    if original_sr == target_sr:
        return audio_data
    target_length = int(len(audio_data) * target_sr / original_sr)
    return np.interp(
        np.linspace(0, len(audio_data) - 1, target_length),
        np.arange(len(audio_data)),
        audio_data
    ).astype(np.float32)

def listen_until_over(language="en") -> str:
    print(f"Using native sample rate: {NATIVE_SAMPLE_RATE} Hz")
    print("Initializing Faster-Whisper model...")
    
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            pass
        audio_queue.put(indata.copy().flatten())

    print("\nListening... Speak now. Say 'over' when you are done.\n")

    full_transcript = []
    stop_event = threading.Event()

    def worker_thread():
        buffer = np.array([], dtype=np.float32)
        chunk_duration = 3.0
        native_chunk_samples = int(NATIVE_SAMPLE_RATE * chunk_duration)

        while not stop_event.is_set():
            try:
                data = audio_queue.get(timeout=0.1)
                buffer = np.concatenate((buffer, data))
            except queue.Empty:
                pass

            if len(buffer) >= native_chunk_samples:
                audio_chunk = buffer[:native_chunk_samples]
                buffer = buffer[native_chunk_samples:]

                resampled_chunk = resample_audio(audio_chunk, NATIVE_SAMPLE_RATE, TARGET_SAMPLE_RATE)
                
                segments, info = model.transcribe(
                    resampled_chunk,
                    beam_size=5,
                    language=language,
                    vad_filter=True,
                )

                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        print(f"-> {text}")
                        full_transcript.append(text)
                        
                        # Check if "over" is spoken (case-insensitive)
                        cleaned_text = text.lower().strip(".,!?")
                        if "over" in cleaned_text.split():
                            stop_event.set()
                            break

    t = threading.Thread(target=worker_thread, daemon=True)
    t.start()

    with sd.InputStream(
        samplerate=NATIVE_SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=audio_callback,
        blocksize=BLOCK_SIZE
    ):
        while not stop_event.is_set():
            time.sleep(0.1)

    t.join(timeout=2.0)
    
    # Combine all captured segments into a single string
    return " ".join(full_transcript)

if __name__ == "__main__":
    result_text = listen_until_over()
    print(f"\nFinal Transcribed Text Returned:\n{result_text}")