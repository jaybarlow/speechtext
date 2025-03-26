"""Text output module for handling text output to current field."""

import pyperclip
from pynput.keyboard import Key, Controller
from loguru import logger


class TextOutputManager:
    """Manages outputting text to the current field."""

    def __init__(self):
        """Initialize the text output manager."""
        self.keyboard = Controller()

    def output_text(self, text: str, use_clipboard: bool = True):
        """
        Output text to the current field.

        Args:
            text: The text to output
            use_clipboard: Whether to use the clipboard (default: True)
        """
        if not text:
            return

        logger.info(f"Outputting text: {text}")

        if use_clipboard:
            self._output_via_clipboard(text)
        else:
            self._output_via_typing(text)

    def _output_via_clipboard(self, text: str):
        """
        Output text via clipboard paste.

        Args:
            text: The text to output
        """
        # Store the current clipboard content
        try:
            previous_clipboard = pyperclip.paste()
        except Exception:
            previous_clipboard = ""

        # Copy the new text to clipboard
        pyperclip.copy(text)

        # Paste the text
        with self.keyboard.pressed(Key.cmd):
            self.keyboard.press("v")
            self.keyboard.release("v")

        # Restore the previous clipboard content
        pyperclip.copy(previous_clipboard)

    def _output_via_typing(self, text: str):
        """
        Output text by simulating typing.

        Args:
            text: The text to output
        """
        self.keyboard.type(text)
