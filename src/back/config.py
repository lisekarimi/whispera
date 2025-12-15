"""Configuration management for the Audio Transcription App."""

import os
import sys
from dotenv import load_dotenv

# Suppress pydub warnings about ffmpeg - we'll configure it explicitly
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

from .utils import check_ffmpeg, configure_pydub
from .logging_config import logger


def get_application_path():
    """Get the application path (works for both script and frozen exe)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script - go up from src/back/ to project root
        current_file = os.path.abspath(__file__)
        # Go up two levels: from src/back/config.py to project root
        return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))


def load_config():
    """Load configuration from .env file and set up ffmpeg."""
    application_path = get_application_path()
    env_path = os.path.join(application_path, '.env')
    load_dotenv(env_path)

    # Note: ffmpeg download is handled by the GUI on startup to show status messages
    # This allows users to see progress when running as .exe (no console)

    # Check for ffmpeg in default location (ffmpeg/ folder at project root)
    # We always use the default location, ignoring FFMPEG_PATH env var
    ffmpeg_available, ffmpeg_path = check_ffmpeg(None)

    # Configure pydub to use ffmpeg if available
    if PYDUB_AVAILABLE and ffmpeg_available and ffmpeg_path:
        configure_pydub(ffmpeg_path)

    # Get API key from environment
    openai_api_key = os.getenv('OPENAI_API_KEY')

    return {
        'application_path': application_path,
        'ffmpeg_available': ffmpeg_available,
        'ffmpeg_path': ffmpeg_path,
        'openai_api_key': openai_api_key,
        'pydub_available': PYDUB_AVAILABLE
    }
