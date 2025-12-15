# Whispera

A Python application that transcribes audio recordings to text using OpenAI's Whisper API.

**Why this app?** We created this app because we couldn't find a tool that allows transcribing meetings up to 2 hours at a reasonable price without requiring subscriptions or monthly access. This app gives you full control over your transcription needs using your own OpenAI API key, avoiding expensive subscription-based services.

## Features

- 🎤 **Audio Transcription**: Uses OpenAI Whisper API for accurate speech-to-text conversion
- 🖥️ **Native GUI**: Clean tkinter-based desktop application (no browser needed)
- 📋 **Copy Button**: Easy one-click copy of transcribed text
- 📁 **File Selection**: Simple file dialog to select MP3 or MP4 files
- 📊 **Progress Bar**: Visual feedback during transcription
- 💻 **Windows Executable**: Can be built as a standalone .exe file

## Quick Start

### Run Locally

```bash
make local
```

### Build Windows Executable

```bash
make build-exe
```

**Note**: The executable is only for **WINDOWS**.

The executable will be in the `dist` folder: `dist\Whispera.exe`

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/lisekarimi/whispera.git
   cd whispera
   ```

1. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

2. Or enter your API key directly in the GUI when you run the app.

**Note**: This tool can transcribe audio up to **2 hours maximum**.

## Usage

1. Click "Select Audio/Video File" to choose an MP3 or MP4 file
2. Click "Transcribe" to start the transcription
3. View the transcribed text in the text area
4. Click "Copy to Clipboard" to copy the transcription
5. Paste the transcribed text into ChatGPT or Claude to generate meeting notes
