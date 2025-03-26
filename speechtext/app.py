"""Main application for speech-to-text transcription."""

import threading
import time
from typing import Optional, Dict, Any

from loguru import logger
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

from speechtext.audio.recorder import AudioRecorder
from speechtext.transcription.speech_to_text import SpeechTranscriber
from speechtext.output.text_output import TextOutputManager


class SpeechTextApp:
    """Main application for speech-to-text transcription."""

    def __init__(
        self,
        device_index: int = 0,
        sample_rate: int = 16000,
        language_code: str = "en-US",
        auto_output: bool = True,
    ):
        """
        Initialize the speech-to-text application.

        Args:
            device_index: Index of the audio input device
            sample_rate: Audio sample rate in Hz
            language_code: Language code for transcription
            auto_output: Automatically output transcriptions
        """
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.language_code = language_code
        self.auto_output = auto_output

        self.console = Console()
        self.recorder = AudioRecorder(
            device_index=self.device_index, sample_rate=self.sample_rate
        )
        self.transcriber = SpeechTranscriber(
            language_code=self.language_code, sample_rate=self.sample_rate
        )
        self.output_manager = TextOutputManager()

        self.running = False
        self.transcription_thread: Optional[threading.Thread] = None
        self.current_transcript = ""
        self.last_output_transcript = ""
        self.current_usage: Dict[str, Any] = {}

    def _handle_interim_result(self, text: str):
        """
        Handle interim transcription result.

        Args:
            text: Interim transcript text
        """
        self.current_transcript = text
        self._update_display()

    def _handle_final_result(self, text: str):
        """
        Handle final transcription result.

        Args:
            text: Final transcript text
        """
        self.current_transcript = text
        self._update_display()

        # Only output to the current text field if auto_output is enabled
        if self.auto_output and text != self.last_output_transcript:
            self.output_manager.output_text(text, use_clipboard=False)
            self.last_output_transcript = text

    def _handle_usage_update(self, usage_stats: Dict[str, Any]):
        """
        Handle usage statistics update.

        Args:
            usage_stats: Dictionary with usage statistics
        """
        self.current_usage = usage_stats
        self._update_display()

    def _update_display(self):
        """Update the console display with current transcript and usage info."""
        self.console.clear()

        # Create transcript panel
        transcript_text = Text()
        transcript_text.append("Current Transcript: ", style="bold cyan")
        transcript_text.append(self.current_transcript)
        self.console.print(
            Panel(transcript_text, title="Transcript", border_style="cyan")
        )

        # Create usage statistics panel if available
        if self.current_usage:
            usage_table = Table(
                title="Usage Statistics", show_header=True, header_style="bold yellow"
            )
            usage_table.add_column("Metric", style="dim", width=20)
            usage_table.add_column("Value", justify="right")

            # Add usage rows
            usage_table.add_row(
                "Audio Duration",
                f"{self.current_usage['total_audio_seconds']:.2f} seconds",
            )
            usage_table.add_row(
                "Billable Units",
                f"{self.current_usage['billable_chunks']} (15-second chunks)",
            )
            usage_table.add_row(
                "Estimated Cost", f"${self.current_usage['estimated_cost_usd']:.4f} USD"
            )
            usage_table.add_row(
                "Transcription Count", f"{self.current_usage['transcription_count']}"
            )
            usage_table.add_row(
                "Total Characters", f"{self.current_usage['total_characters']}"
            )
            usage_table.add_row(
                "Session Duration",
                f"{self.current_usage['elapsed_seconds']:.1f} seconds",
            )

            self.console.print(
                Panel(usage_table, title="Usage & Cost", border_style="yellow")
            )

        # Instructions
        self.console.print("Press Ctrl+C to stop", style="bold red")

    def _transcription_worker(self):
        """Worker thread for transcription."""
        audio_chunks = self.recorder.get_audio_chunks()
        self.transcriber.transcribe_stream(
            audio_chunks,
            on_interim_result=self._handle_interim_result,
            on_final_result=self._handle_final_result,
            on_usage_update=self._handle_usage_update,
        )

    def start(self):
        """Start the speech-to-text application."""
        if self.running:
            return

        logger.info("Starting SpeechText application")
        self.console.clear()
        self.console.print("Starting SpeechText...", style="bold green")
        self.console.print(
            f"Using device: {self.device_index}",
            style="bold blue",
        )
        self.console.print(
            f"Language: {self.language_code}",
            style="bold blue",
        )
        self.console.print("Press Ctrl+C to stop", style="bold red")

        self.running = True
        self.recorder.start()

        self.transcription_thread = threading.Thread(
            target=self._transcription_worker,
        )
        self.transcription_thread.daemon = True
        self.transcription_thread.start()

    def stop(self):
        """Stop the speech-to-text application."""
        if not self.running:
            return

        logger.info("Stopping SpeechText application")
        self.running = False

        self.transcriber.stop()
        self.recorder.stop()

        if self.transcription_thread:
            self.transcription_thread.join(timeout=2)

        # Final display of usage statistics
        if self.current_usage:
            self.console.print("\nFinal Usage Statistics:", style="bold yellow")
            self.console.print(
                f"Total Audio Duration: {self.current_usage['total_audio_seconds']:.2f} seconds"
            )
            self.console.print(
                f"Billable 15-second Chunks: {self.current_usage['billable_chunks']}"
            )
            self.console.print(
                f"Estimated Cost: ${self.current_usage['estimated_cost_usd']:.4f} USD"
            )
            self.console.print(
                f"Total Transcriptions: {self.current_usage['transcription_count']}"
            )

        self.console.print("SpeechText stopped", style="bold yellow")

    def run(self):
        """Run the speech-to-text application."""
        try:
            self.start()
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
        finally:
            if self.running:
                self.stop()
