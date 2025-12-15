"""Transcription assistant for audio-to-text conversion."""

import os
import tempfile
from openai import OpenAI

from .logging_config import logger

from .constants import (
    AUDIO_MODEL,
    SUPPORTED_FORMATS,
    MAX_FILE_SIZE_BYTES,
    CHUNK_SIZE_MB,
    AUDIO_BITRATE_HIGH,
    AUDIO_BITRATE_LOW,
    CHUNK_SIZE_SAFETY_FACTOR,
    PROGRESS_SPLITTING,
    PROGRESS_TRANSCRIBING,
    PROGRESS_COMBINING,
    PROGRESS_COMPLETE,
)
from .utils import check_ffmpeg, configure_pydub, PYDUB_AVAILABLE

# Import AudioSegment only if available
if PYDUB_AVAILABLE:
    from pydub import AudioSegment
else:
    AudioSegment = None


class TranscriptionAssistant:
    """Assistant for transcribing audio to text."""

    def __init__(self, audio_model=AUDIO_MODEL, api_key=None):
        """Initialize the transcription assistant with specified model."""
        self.audio_model = audio_model
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = OpenAI(api_key=api_key)

    def set_api_key(self, api_key):
        """Update the API key and recreate the client."""
        self.api_key = api_key
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    def _split_audio_file(self, audio_path, max_size_mb=CHUNK_SIZE_MB):
        """Split audio file into chunks that are under the size limit."""
        if not PYDUB_AVAILABLE:
            return None, "pydub library not available. Please install it: pip install pydub\nNote: ffmpeg is also required for audio processing."

        # Get ffmpeg path from environment
        ffmpeg_custom = os.getenv('FFMPEG_PATH', '')
        ffmpeg_available, ffmpeg_path = check_ffmpeg(ffmpeg_custom)
        if not ffmpeg_available:
            return None, (
                "ffmpeg is not installed or not found.\n\n"
                "To enable automatic file splitting, please install ffmpeg:\n\n"
                "Option 1 (Recommended): Download from https://ffmpeg.org/download.html\n"
                "  - Extract and add to PATH, OR\n"
                "  - Place ffmpeg.exe in the same folder as this app\n\n"
                "Option 2: Use package manager\n"
                "  - Chocolatey: choco install ffmpeg\n"
                "  - Winget: winget install ffmpeg\n\n"
                "After installing, restart the application."
            )

        try:
            logger.info(f"Starting audio file split for: {audio_path}")
            # Configure pydub with ffmpeg path BEFORE using it
            configure_pydub(ffmpeg_path)

            # Double-check the converter and ffprobe are set and the files exist
            if PYDUB_AVAILABLE and AudioSegment:
                converter_path = getattr(AudioSegment, 'converter', None)
                ffprobe_path = getattr(AudioSegment, 'ffprobe', None)
                logger.debug(f"AudioSegment.converter is set to: {converter_path}")
                logger.debug(f"AudioSegment.ffprobe is set to: {ffprobe_path}")

                # Fix converter if needed
                if not converter_path or not os.path.exists(converter_path.replace("/", "\\")):
                    logger.warning(f"Converter path invalid or not set: {converter_path}, attempting to fix...")
                    if os.path.isfile(ffmpeg_path):
                        AudioSegment.converter = os.path.abspath(ffmpeg_path).replace("\\", "/")
                    elif os.path.isdir(ffmpeg_path):
                        ffmpeg_exe = os.path.join(ffmpeg_path, "ffmpeg.exe")
                        if os.path.exists(ffmpeg_exe):
                            AudioSegment.converter = os.path.abspath(ffmpeg_exe).replace("\\", "/")
                    AudioSegment.ffmpeg = AudioSegment.converter
                    logger.info(f"Fixed converter path to: {AudioSegment.converter}")

                # CRITICAL: Ensure ffprobe is set (pydub needs it for media info)
                if not ffprobe_path or not os.path.exists(ffprobe_path.replace("/", "\\")):
                    logger.warning(f"ffprobe path invalid or not set: {ffprobe_path}, attempting to fix...")
                    if os.path.isdir(ffmpeg_path):
                        ffprobe_exe = os.path.join(ffmpeg_path, "ffprobe.exe")
                        if os.path.exists(ffprobe_exe):
                            AudioSegment.ffprobe = os.path.abspath(ffprobe_exe).replace("\\", "/")
                            logger.info(f"Fixed ffprobe path to: {AudioSegment.ffprobe}")
                        else:
                            # Fallback: use ffmpeg if ffprobe doesn't exist
                            logger.warning("ffprobe.exe not found, using ffmpeg as fallback")
                            AudioSegment.ffprobe = AudioSegment.converter

            # Load audio file - this is where the error occurs if ffmpeg isn't found
            logger.debug(f"Loading audio file: {audio_path}")
            audio = AudioSegment.from_file(audio_path)
            logger.info(f"Audio file loaded successfully, duration: {len(audio)}ms")
            file_size = os.path.getsize(audio_path)
            max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes

            # If file is small enough, return None (no splitting needed)
            if file_size <= max_size:
                return None, None

            # Calculate chunk duration based on file size and duration
            duration_ms = len(audio)
            bytes_per_ms = file_size / duration_ms if duration_ms > 0 else 0
            chunk_duration_ms = int((max_size / bytes_per_ms) * CHUNK_SIZE_SAFETY_FACTOR) if bytes_per_ms > 0 else duration_ms

            if chunk_duration_ms <= 0:
                chunk_duration_ms = duration_ms // 2  # Fallback: split in half

            # Create temporary directory for chunks
            temp_dir = tempfile.mkdtemp()
            chunk_paths = []

            # Split into chunks
            num_chunks = (duration_ms // chunk_duration_ms) + (1 if duration_ms % chunk_duration_ms > 0 else 0)

            for i in range(num_chunks):
                start_ms = i * chunk_duration_ms
                end_ms = min((i + 1) * chunk_duration_ms, duration_ms)

                chunk = audio[start_ms:end_ms]
                chunk_path = os.path.join(temp_dir, f"chunk_{i+1}.mp3")

                # Export chunk
                chunk.export(chunk_path, format="mp3", bitrate=AUDIO_BITRATE_HIGH)

                # Verify chunk size
                chunk_size = os.path.getsize(chunk_path)
                if chunk_size > max_size:
                    # If still too large, try lower bitrate
                    chunk.export(chunk_path, format="mp3", bitrate=AUDIO_BITRATE_LOW)
                    chunk_size = os.path.getsize(chunk_path)

                chunk_paths.append(chunk_path)

            return chunk_paths, None

        except Exception as e:
            logger.error(f"Error splitting audio file: {str(e)}", exc_info=True)
            # Log converter status for debugging
            if PYDUB_AVAILABLE and AudioSegment:
                converter = getattr(AudioSegment, 'converter', None)
                logger.error(f"AudioSegment.converter at time of error: {converter}")
            return None, f"Error splitting audio file: {str(e)}\nNote: ffmpeg may be required. Install from: https://ffmpeg.org/"

    def transcribe_audio_chunk(self, audio_path, progress_callback=None, chunk_info=None):
        """Transcribe a single audio chunk."""
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.audio_model,
                    file=audio_file,
                    response_format="text"
                )
                return transcription
        except Exception as e:
            error_msg = str(e)
            if "400" in error_msg or "invalid_request_error" in error_msg:
                return f"Error: Invalid file format or file is corrupted. Details: {error_msg}"
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                return f"Error: Invalid API key. Details: {error_msg}"
            else:
                return f"Error during transcription: {error_msg}"

    def transcribe_audio(self, audio_path, progress_callback=None):
        """Transcribe the uploaded audio file using OpenAI Whisper API."""
        if not self.client:
            return "Error: OpenAI API key not set. Please enter your API key in the settings."

        file_size = os.path.getsize(audio_path)

        # Check if file needs splitting
        if file_size > MAX_FILE_SIZE_BYTES:
            if progress_callback:
                progress_callback(PROGRESS_SPLITTING, 10)

            # Split the file
            chunk_paths, error = self._split_audio_file(audio_path, max_size_mb=CHUNK_SIZE_MB)
            if error:
                return error

            if not chunk_paths:
                # File was small enough after processing, transcribe normally
                return self.transcribe_audio_chunk(audio_path, progress_callback)

            # Transcribe each chunk
            transcriptions = []
            num_chunks = len(chunk_paths)
            temp_dir = os.path.dirname(chunk_paths[0])

            try:
                for i, chunk_path in enumerate(chunk_paths):
                    if progress_callback:
                        progress = 20 + int((i / num_chunks) * 70)
                        progress_callback(f"Transcribing chunk {i+1} of {num_chunks}...", progress)

                    chunk_transcription = self.transcribe_audio_chunk(chunk_path, progress_callback)
                    if chunk_transcription.startswith("Error"):
                        return chunk_transcription

                    transcriptions.append(chunk_transcription)

                # Combine all transcriptions
                if progress_callback:
                    progress_callback(PROGRESS_COMBINING, 95)

                combined_transcription = "\n\n".join(transcriptions)

                if progress_callback:
                    progress_callback(PROGRESS_COMPLETE, 100)

                return combined_transcription

            finally:
                # Clean up temporary chunk files
                try:
                    for chunk_path in chunk_paths:
                        if os.path.exists(chunk_path):
                            os.remove(chunk_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                except Exception:
                    pass  # Ignore cleanup errors

        # File is small enough, transcribe normally
        if progress_callback:
            progress_callback(PROGRESS_TRANSCRIBING, 30)

        try:
            transcription = self.transcribe_audio_chunk(audio_path, progress_callback)
            if progress_callback:
                progress_callback(PROGRESS_COMPLETE, 100)
            return transcription
        except Exception as e:
            return f"Error during transcription: {str(e)}"

    def process_audio(self, audio_path, progress_callback=None):
        """Handle the complete process: transcribe audio to text."""
        if progress_callback:
            progress_callback("Processing file...", 10)

        if not audio_path:
            return "Please select an audio or video file."

        try:
            # Check if file exists
            if not os.path.exists(audio_path):
                return "Error: File not found. Please select a valid file."

            # Check file format
            file_lower = audio_path.lower()
            if not any(file_lower.endswith(ext) for ext in SUPPORTED_FORMATS):
                return f"Error: Unsupported file format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"

            # Get transcription
            transcription = self.transcribe_audio(audio_path, progress_callback)

            if transcription.startswith("Error"):
                return transcription

            return transcription

        except Exception as e:
            return f"Error processing file: {str(e)}"
