"""Audio recorder module for capturing audio from iPhone microphone."""

import queue
import threading
from typing import Generator, Optional

import sounddevice as sd
import numpy as np
from loguru import logger


class AudioRecorder:
    """Records audio from the iPhone microphone in chunks."""

    def __init__(
        self,
        device_index: int = 0,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: type = np.int16,
        chunk_size: int = 1024,
    ):
        """
        Initialize the audio recorder.

        Args:
            device_index: Index of the iPhone microphone (default: 0)
            sample_rate: Sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            dtype: Data type for audio samples (default: np.int16)
            chunk_size: Size of audio chunks in samples (default: 1024)
        """
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.stream: Optional[sd.InputStream] = None

    def _audio_callback(self, indata, frames, time, status):
        """Callback function for the audio stream."""
        if status:
            logger.warning(f"Audio status: {status}")
        self.audio_queue.put(indata.copy())

    def start(self):
        """Start recording audio."""
        logger.info(f"Starting audio recording from device {self.device_index}")
        self.stop_event.clear()
        self.stream = sd.InputStream(
            device=self.device_index,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._audio_callback,
            blocksize=self.chunk_size,
        )
        self.stream.start()

    def stop(self):
        """Stop recording audio."""
        logger.info("Stopping audio recording")
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.stop_event.set()

    def get_audio_chunks(self) -> Generator[np.ndarray, None, None]:
        """
        Generator that yields audio chunks.

        Yields:
            Audio chunks as numpy arrays
        """
        while not self.stop_event.is_set() or not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                yield chunk
            except queue.Empty:
                continue
