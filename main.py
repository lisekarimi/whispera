"""Main entry point for the Audio Transcription App."""

from src.back.config import load_config
from src.front.gui import TranscriptionGUI


def main():
    """Main function to start the application."""
    # Load configuration
    config = load_config()

    # Create and launch GUI
    # FFmpeg is auto-detected in ffmpeg/ folder at project root
    app = TranscriptionGUI(
        initial_api_key=config['openai_api_key']
    )
    app.launch()


if __name__ == "__main__":
    main()
