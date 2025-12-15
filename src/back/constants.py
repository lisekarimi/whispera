"""Constants for the Audio Transcription App."""

# OpenAI Whisper API model
AUDIO_MODEL = "whisper-1"

# Supported audio/video file formats
SUPPORTED_FORMATS = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']

# File size limits
MAX_FILE_SIZE_MB = 25  # Maximum file size for direct upload (MB)
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
CHUNK_SIZE_MB = 20  # Size for splitting large files (MB)

# Audio processing settings
AUDIO_BITRATE_HIGH = "128k"  # High quality bitrate for audio chunks
AUDIO_BITRATE_LOW = "64k"    # Low quality bitrate if high quality is too large
CHUNK_SIZE_SAFETY_FACTOR = 0.9  # Use 90% of max size to be safe

# GUI settings
WINDOW_TITLE = "Whispera"
WINDOW_SIZE = "800x600"
FONT_TITLE = ("Arial", 16, "bold")
FONT_NORMAL = ("Arial", 9)
FONT_TEXT = ("Arial", 10)

# Progress messages
PROGRESS_READY = "Ready"
PROGRESS_PROCESSING = "Processing file..."
PROGRESS_SPLITTING = "File is large, splitting into chunks..."
PROGRESS_TRANSCRIBING = "Transcribing audio..."
PROGRESS_COMBINING = "Combining transcriptions..."
PROGRESS_COMPLETE = "Complete!"
