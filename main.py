#!/usr/bin/env python
"""SpeechText - A tool to transcribe audio from iPhone mic to text."""

import argparse
import os
import sys

from loguru import logger
from rich.console import Console

from speechtext.app import SpeechTextApp


def setup_logger():
    """Set up the logger configuration."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level="INFO",
    )


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Transcribe speech from iPhone microphone to text"
    )
    parser.add_argument(
        "-d",
        "--device",
        type=int,
        default=0,
        help="Audio input device index (default: 0)",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="en-US",
        help="Language code (default: en-US)",
    )
    parser.add_argument(
        "--no-auto-output",
        action="store_true",
        help="Disable automatic text output",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit",
    )
    args = parser.parse_args()

    setup_logger()
    console = Console()

    # List devices if requested (allow this without credentials)
    if args.list_devices:
        import sounddevice as sd

        console.print("[bold]Available audio devices:[/]")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                console.print(
                    f"[bold cyan]{i}:[/] {device['name']} "
                    f"(Inputs: {device['max_input_channels']})"
                )
        return 0

    # Check for Google Cloud credentials
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        console.print(
            "[bold red]Error:[/] Google Cloud credentials not found. "
            "Please set the GOOGLE_APPLICATION_CREDENTIALS "
            "environment variable to point to your service account key file.",
            style="red",
        )
        console.print(
            """See: https://cloud.google.com/speech-to-text/docs/\
before-you-begin""",
            style="blue underline",
        )
        return 1

    app = SpeechTextApp(
        device_index=args.device,
        language_code=args.language,
        auto_output=not args.no_auto_output,
    )

    try:
        app.run()
        return 0
    except Exception as e:
        logger.exception("Error in main application")
        console.print(f"[bold red]Error:[/] {str(e)}", style="red")
        return 1


if __name__ == "__main__":
    sys.exit(main())
