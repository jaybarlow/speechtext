# SpeechText

A Python application that transcribes audio from your iPhone's microphone (via Continuity Camera or connected to your Mac) to text in real-time, and automatically pastes the transcribed text to your current text field.

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- Real-time transcription from iPhone microphone to text
- Automatic text output to any active text field
- Support for multiple languages (default: English US)
- Real-time display of transcription in a beautiful terminal UI
- Cost monitoring for Google Cloud Speech-to-Text API usage
- Simple command-line interface with customizable options

## Architecture

The application is structured into modular components:

- `audio`: Handles audio recording and streaming
- `transcription`: Manages the speech-to-text conversion using Google Cloud API
- `output`: Handles the output of transcribed text to the system

## Prerequisites

- Python 3.12+
- Google Cloud Speech-to-Text API credentials
- iPhone connected to your Mac (via Continuity Camera or cable)
- macOS (for automatic text output functionality)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd speechtext
   ```

2. Create and activate a virtual environment (using `uv`):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   uv pip install --editable .
   # or
   uv pip install -r requirements.txt
   ```

4. Set up Google Cloud credentials:
   - Create a Google Cloud project and enable the Speech-to-Text API
   - Create a service account and download the JSON key file
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
     ```

## Usage

### Basic Usage

List available audio devices:
```bash
python main.py --list-devices
# or
task list-devices
```

Start transcription (use device 0, which is typically the iPhone microphone):
```bash
python main.py --device 0
# or
task run -- --device 0
```

### Command-line Options

```
-d, --device        Audio input device index (default: 0)
-l, --language      Language code (default: en-US)
--no-auto-output    Disable automatic text output
--list-devices      List available audio devices and exit
```

### Using Task Runner

The project includes a Taskfile for common operations:

```bash
task run           # Run the app
task list-devices  # List available audio devices
task test          # Run tests
task format        # Format with black
task lint          # Lint with ruff
task typecheck     # Run mypy
task check-all     # Run all quality checks
```

## How It Works

1. **Audio Capture**: The application captures audio from your iPhone's microphone using the `AudioRecorder` class.
2. **Streaming Transcription**: Audio chunks are streamed to Google's Speech-to-Text API via the `SpeechTranscriber` class.
3. **Real-time Display**: Transcribed text is displayed in a rich terminal UI with usage statistics.
4. **Automatic Output**: The `TextOutputManager` automatically pastes the transcribed text to the current active text field.

## Components

- **SpeechTextApp**: Main application controller that coordinates all components
- **AudioRecorder**: Handles audio capture and streaming
- **SpeechTranscriber**: Manages the connection to Google Cloud Speech-to-Text API
- **TextOutputManager**: Handles system-level text output

## Development

### Project Structure

```
speechtext/
├── audio/
│   └── recorder.py       # Audio capture handling
├── transcription/
│   └── speech_to_text.py # Google API integration
├── output/
│   └── text_output.py    # System text output management
└── app.py                # Main application class
```

### Quality Tools

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **Mypy**: Static type checking
- **Pytest**: Testing framework

### Adding New Features

1. Create a feature branch
2. Implement your changes
3. Add tests
4. Run quality checks: `task check-all`
5. Submit a pull request

## Troubleshooting

- **No audio devices found**: Make sure your iPhone is properly connected and Continuity Camera is enabled
- **API credentials error**: Verify your Google Cloud credentials are properly set up
- **Text output not working**: Ensure accessibility permissions are granted for terminal applications

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
