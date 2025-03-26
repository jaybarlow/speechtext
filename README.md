# SpeechText

A Python application that transcribes audio from your iPhone's microphone (via Continuity Camera or connected to your Mac) to text in real-time, and automatically pastes the transcribed text to your current text field.

## Prerequisites

- Python 3.12+
- Google Cloud Speech-to-Text API credentials
- iPhone connected to your Mac (via Continuity Camera or cable)

## Setup

1. Clone this repository
2. Set up a Google Cloud project and enable the Speech-to-Text API
3. Download a service account key file and set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

1. Install dependencies:

```bash
uv pip install -r requirements.txt
# or
uv pip install --editable .
```

## Usage

List available audio devices:

```bash
python main.py --list-devices
```

Start transcription (use device 0 which is typically the iPhone microphone):

```bash
python main.py --device 0
```

Additional options:

```bash
python main.py --help
```

## Tasks

```bash
task run        # Run the app
task test       # Run tests
task format     # Format with black
task lint       # Lint with ruff
task typecheck  # Run mypy
```

## How It Works

1. The application captures audio from your iPhone's microphone
2. Audio is streamed to Google's Speech-to-Text API for real-time transcription
3. Transcribed text is displayed in the terminal and automatically pasted to the current text field

## License

MIT
