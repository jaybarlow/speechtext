"""Speech to text transcription using Google Cloud Speech-to-Text API."""

import threading
import time
from typing import Callable, Iterator, Optional, Dict, Any
import numpy as np
from google.cloud import speech
from loguru import logger

# Type aliases
AudioChunks = Iterator[np.ndarray]
AudioBytes = Iterator[bytes]

# Speech-to-Text pfricing (as of 2023)
# Standard model: $0.006 per 15 seconds
# Enhanced model: $0.009 per 15 seconds
PRICING_PER_15_SECONDS = 0.006


class SpeechTranscriber:
    """Transcribes audio to text using Google Cloud Speech-to-Text API."""

    def __init__(
        self,
        language_code: str = "en-US",
        sample_rate: int = 16000,
        encoding: speech.RecognitionConfig.AudioEncoding = (
            speech.RecognitionConfig.AudioEncoding.LINEAR16
        ),
        enable_automatic_punctuation: bool = True,
        single_utterance: bool = False,
    ):
        """
        Initialize the speech transcriber.

        Args:
            language_code: Language code (default: "en-US")
            sample_rate: Audio sample rate in Hz (default: 16000)
            encoding: Audio encoding format
            enable_automatic_punctuation: Enable automatic punctuation
            single_utterance: End recognition after the first complete sentence
        """
        self.language_code = language_code
        self.sample_rate = sample_rate
        self.encoding = encoding
        self.enable_automatic_punctuation = enable_automatic_punctuation
        self.single_utterance = single_utterance
        self.client = speech.SpeechClient()
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=self.encoding,
                sample_rate_hertz=self.sample_rate,
                language_code=self.language_code,
                enable_automatic_punctuation=self.enable_automatic_punctuation,
            ),
            interim_results=True,
            single_utterance=self.single_utterance,
        )
        self.stop_event = threading.Event()

        # Usage tracking
        self.reset_usage_stats()

    def reset_usage_stats(self):
        """Reset the usage statistics."""
        self.usage_stats = {
            "total_audio_seconds": 0,
            "chunks_processed": 0,
            "total_characters": 0,
            "start_time": time.time(),
            "transcription_count": 0,
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get the current usage statistics.

        Returns:
            Dictionary with usage statistics and estimated cost
        """
        elapsed_seconds = time.time() - self.usage_stats["start_time"]

        # Calculate cost - round up to nearest 15 seconds
        billable_chunks = (self.usage_stats["total_audio_seconds"] + 14) // 15
        estimated_cost = billable_chunks * PRICING_PER_15_SECONDS

        return {
            **self.usage_stats,
            "elapsed_seconds": elapsed_seconds,
            "estimated_cost_usd": estimated_cost,
            "billable_chunks": billable_chunks,
        }

    def _audio_generator(self, audio_chunks: AudioChunks) -> AudioBytes:
        """
        Generate audio content for the Speech API.

        Args:
            audio_chunks: Iterator of audio chunks as numpy arrays

        Yields:
            Audio bytes for the Speech API
        """
        for chunk in audio_chunks:
            if self.stop_event.is_set():
                break

            # Track audio seconds (assuming 1 chunk = 64ms at 16kHz)
            chunk_duration = len(chunk) / self.sample_rate
            self.usage_stats["total_audio_seconds"] += chunk_duration
            self.usage_stats["chunks_processed"] += 1

            yield chunk.tobytes()

    def transcribe_stream(
        self,
        audio_chunks: AudioChunks,
        on_interim_result: Optional[Callable[[str], None]] = None,
        on_final_result: Optional[Callable[[str], None]] = None,
        on_usage_update: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Transcribe audio from a stream of audio chunks.

        Args:
            audio_chunks: Iterator of audio chunks as numpy arrays
            on_interim_result: Callback for interim results
            on_final_result: Callback for final results
            on_usage_update: Callback for usage updates
        """
        self.stop_event.clear()
        self.reset_usage_stats()

        audio_generator = self._audio_generator(audio_chunks)
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        logger.info("Starting speech recognition stream")
        responses = self.client.streaming_recognize(
            config=self.streaming_config, requests=requests
        )

        usage_update_interval = 1.0  # Update usage stats every second
        last_usage_update = time.time()

        try:
            for response in responses:
                if self.stop_event.is_set():
                    break

                if not response.results:
                    continue

                result = response.results[0]

                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript

                # Update usage stats
                self.usage_stats["total_characters"] = max(
                    self.usage_stats["total_characters"], len(transcript)
                )

                if result.is_final:
                    logger.info(f"Final transcript: {transcript}")
                    self.usage_stats["transcription_count"] += 1
                    if on_final_result:
                        on_final_result(transcript)
                else:
                    logger.debug(f"Interim transcript: {transcript}")
                    if on_interim_result:
                        on_interim_result(transcript)

                # Periodically update usage stats
                current_time = time.time()
                if current_time - last_usage_update > usage_update_interval:
                    last_usage_update = current_time
                    if on_usage_update:
                        on_usage_update(self.get_usage_stats())

        except Exception as e:
            logger.error(f"Error during transcription: {e}")

        # Final usage update
        if on_usage_update:
            on_usage_update(self.get_usage_stats())

    def stop(self):
        """Stop the transcription process."""
        logger.info("Stopping transcription")
        self.stop_event.set()
