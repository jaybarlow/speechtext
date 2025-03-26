"""Text output module for handling text output to current field."""

import pyperclip
from pynput.keyboard import Key, Controller
from loguru import logger
import time


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

        # Small delay to ensure clipboard has been updated
        time.sleep(0.1)

        # Try Command+V (Mac)
        try:
            with self.keyboard.pressed(Key.cmd):
                self.keyboard.press("v")
                self.keyboard.release("v")
        except Exception as e:
            logger.warning(f"Command+V paste failed: {e}")
            # Fallback to Control+V (Windows/Linux)
            try:
                with self.keyboard.pressed(Key.ctrl):
                    self.keyboard.press("v")
                    self.keyboard.release("v")
            except Exception as e:
                logger.error(f"Control+V paste also failed: {e}")

        # Small delay before restoring clipboard
        time.sleep(0.1)

        # Restore the previous clipboard content
        try:
            pyperclip.copy(previous_clipboard)
        except Exception as e:
            logger.warning(f"Failed to restore clipboard: {e}")

    def _output_via_typing(self, text: str):
        """
        Output text by simulating typing.

        Args:
            text: The text to output
        """
        self.keyboard.type(text)
