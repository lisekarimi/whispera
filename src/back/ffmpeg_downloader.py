"""Automatic ffmpeg downloader for the Audio Transcription App."""

import os
import sys
import urllib.request
import zipfile
import shutil

from .logging_config import logger

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_ZIP = "ffmpeg.zip"
FFMPEG_DIR = "ffmpeg"


def download_ffmpeg_tools(app_path, status_callback=None):
    """Download ffmpeg and ffprobe if they're missing.

    Args:
        app_path: Application root path where ffmpeg folder should be created
        status_callback: Optional callback function(status_message) to update GUI

    Returns:
        tuple: (ffmpeg_found: bool, ffprobe_found: bool)
    """
    ffmpeg_dir = os.path.join(app_path, FFMPEG_DIR)
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")

    # Check what's missing
    ffmpeg_exists = os.path.exists(ffmpeg_exe)
    ffprobe_exists = os.path.exists(ffprobe_exe)

    if ffmpeg_exists and ffprobe_exists:
        logger.info("Both ffmpeg.exe and ffprobe.exe are already present.")
        return True, True

    # Determine what needs to be downloaded
    needs_download = False
    if not ffmpeg_exists:
        msg = "ffmpeg.exe is missing. Will download..."
        logger.warning(msg)
        if status_callback:
            status_callback(msg)
        needs_download = True
    if not ffprobe_exists:
        msg = "ffprobe.exe is missing. Will download..."
        logger.warning(msg)
        if status_callback:
            status_callback(msg)
        needs_download = True

    if not needs_download:
        return ffmpeg_exists, ffprobe_exists

    # Download and extract
    msg = "Downloading ffmpeg tools..."
    logger.info(msg)
    if status_callback:
        status_callback(msg)

    logger.info(f"URL: {FFMPEG_URL}")
    msg = "This may take a few minutes..."
    logger.info(msg)
    if status_callback:
        status_callback(msg)

    try:
        zip_path = os.path.join(app_path, FFMPEG_ZIP)

        # Download the zip file
        msg = "Downloading from server..."
        logger.info(msg)
        if status_callback:
            status_callback(msg)

        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
        msg = "✓ Download complete!"
        logger.info(msg)
        if status_callback:
            status_callback(msg)

        # Extract the zip file
        msg = "Extracting ffmpeg..."
        logger.info(msg)
        if status_callback:
            status_callback(msg)
        extract_dir = os.path.join(app_path, "ffmpeg_extract_temp")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Find ffmpeg.exe and ffprobe.exe in the extracted folder
        ffmpeg_found = False
        ffprobe_found = False

        for root, dirs, files in os.walk(extract_dir):
            # Look for the bin directory which contains the executables
            if "bin" in dirs and "ffmpeg-" in root:
                bin_dir = os.path.join(root, "bin")
                if os.path.exists(bin_dir):
                    # Create target directory
                    if not os.path.exists(ffmpeg_dir):
                        os.makedirs(ffmpeg_dir)

                    # Copy ffmpeg.exe if missing
                    if not ffmpeg_exists:
                        ffmpeg_src = os.path.join(bin_dir, "ffmpeg.exe")
                        if os.path.exists(ffmpeg_src):
                            shutil.copy(ffmpeg_src, ffmpeg_exe)
                            msg = f"✓ ffmpeg.exe copied to {ffmpeg_dir}/"
                            logger.info(msg)
                            if status_callback:
                                status_callback(msg)
                            ffmpeg_found = True

                    # Copy ffprobe.exe if missing
                    if not ffprobe_exists:
                        ffprobe_src = os.path.join(bin_dir, "ffprobe.exe")
                        if os.path.exists(ffprobe_src):
                            shutil.copy(ffprobe_src, ffprobe_exe)
                            msg = f"✓ ffprobe.exe copied to {ffmpeg_dir}/"
                            logger.info(msg)
                            if status_callback:
                                status_callback(msg)
                            ffprobe_found = True

                    if (ffmpeg_exists or ffmpeg_found) and (ffprobe_exists or ffprobe_found):
                        break

        # Fallback: search for files directly (older extraction structure)
        if not ffmpeg_found and not ffmpeg_exists:
            msg = "Searching for ffmpeg files..."
            logger.info(msg)
            if status_callback:
                status_callback(msg)
            for root, dirs, files in os.walk(extract_dir):
                if "ffmpeg.exe" in files:
                    ffmpeg_src = os.path.join(root, "ffmpeg.exe")
                    if not os.path.exists(ffmpeg_dir):
                        os.makedirs(ffmpeg_dir)
                    shutil.copy(ffmpeg_src, ffmpeg_exe)
                    msg = f"✓ ffmpeg.exe copied to {ffmpeg_dir}/"
                    logger.info(msg)
                    if status_callback:
                        status_callback(msg)
                    ffmpeg_found = True

                    # Also look for ffprobe.exe in the same directory
                    if not ffprobe_exists:
                        ffprobe_src = os.path.join(root, "ffprobe.exe")
                        if os.path.exists(ffprobe_src):
                            shutil.copy(ffprobe_src, ffprobe_exe)
                            msg = f"✓ ffprobe.exe copied to {ffmpeg_dir}/"
                            logger.info(msg)
                            if status_callback:
                                status_callback(msg)
                            ffprobe_found = True
                    break

        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

        # Final check
        final_ffmpeg = os.path.exists(ffmpeg_exe)
        final_ffprobe = os.path.exists(ffprobe_exe)

        if final_ffmpeg and final_ffprobe:
            msg = "✅ ffmpeg setup complete! Both ffmpeg.exe and ffprobe.exe are ready."
            logger.info(msg)
            if status_callback:
                status_callback(msg)
            return True, True
        elif final_ffmpeg:
            msg = "⚠️  ffmpeg.exe is ready, but ffprobe.exe is still missing."
            logger.warning(msg)
            if status_callback:
                status_callback(msg)
            logger.warning("   The app may not work correctly without ffprobe.exe.")
            return True, False
        else:
            msg = "❌ Failed to download ffmpeg tools."
            logger.error(msg)
            if status_callback:
                status_callback(msg)
            return False, False

    except Exception as e:
        error_msg = f"❌ Error downloading ffmpeg: {e}"
        logger.error(error_msg, exc_info=True)
        if status_callback:
            status_callback(error_msg)
        logger.error("\nYou can manually download ffmpeg from:")
        logger.error("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
        logger.error(f"\nThen extract ffmpeg.exe and ffprobe.exe to: {ffmpeg_dir}")
        return False, False
