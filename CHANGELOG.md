# Changelog

All notable changes and features of Whispera.

## [1.0.0] - Initial Release

### Core Functionality
- **Audio Transcription**: Transcribe audio files to text using OpenAI Whisper API
- **Native GUI**: Desktop application built with tkinter (no browser required)
- **File Selection**: Support for multiple audio/video formats (MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM)
- **Large File Handling**: Automatic file splitting for files larger than 25MB
- **Progress Tracking**: Visual progress bar showing transcription status
- **Copy to Clipboard**: One-click copy of transcribed text

### Configuration
- **API Key Management**: Enter API key directly in GUI or via .env file
- **Environment Variables**: Support for .env file configuration

### Deployment
- **Windows Executable**: Standalone .exe file build with PyInstaller
- **Portable**: No installation required, runs directly from executable

### Limitations
- Maximum audio duration: 2 hours
- Windows platform only (executable)
