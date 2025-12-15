"""Utility functions for the Audio Transcription App."""

import os
import sys
import shutil
import subprocess

from .logging_config import logger

# Store original subprocess functions for lazy patching
# We patch lazily to avoid import-time issues with PyInstaller
_original_popen = subprocess.Popen
_original_run = subprocess.run
_subprocess_patched = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None


def check_ffmpeg(custom_path=None):
    """Check if ffmpeg is available in PATH or bundled with the app.

    Args:
        custom_path: Optional custom path to ffmpeg directory or executable

    Returns:
        tuple: (is_available: bool, ffmpeg_path: str or None)
    """
    logger.debug(f"Checking for ffmpeg, custom_path: {custom_path}")

    # If custom path is provided, check it first
    if custom_path and custom_path.strip():
        custom_path = os.path.normpath(custom_path.strip())  # Normalize path (handles / vs \)
        logger.debug(f"Checking custom path: {custom_path}")
        # If it's a directory, look for ffmpeg.exe inside
        if os.path.isdir(custom_path):
            ffmpeg_exe = os.path.join(custom_path, "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
                # Normalize to absolute path
                ffmpeg_exe = os.path.normpath(os.path.abspath(ffmpeg_exe))
                logger.info(f"Found ffmpeg at custom path: {ffmpeg_exe}")
                os.environ["PATH"] = os.path.dirname(ffmpeg_exe) + os.pathsep + os.environ.get("PATH", "")
                return True, ffmpeg_exe
            else:
                logger.warning(f"Custom path is a directory but ffmpeg.exe not found: {ffmpeg_exe}")
        # If it's a file path, check if it exists
        elif os.path.isfile(custom_path):
            if os.path.exists(custom_path):
                # Normalize to absolute path
                custom_path = os.path.normpath(os.path.abspath(custom_path))
                # Add parent directory to PATH
                parent_dir = os.path.dirname(custom_path)
                os.environ["PATH"] = parent_dir + os.pathsep + os.environ.get("PATH", "")
                return True, custom_path

    # First, try to find ffmpeg in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return True, ffmpeg_path

    # If running as exe, check in the same directory as the executable
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        # Check for ffmpeg.exe in the same directory
        ffmpeg_exe = os.path.join(exe_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_exe):
            # Set environment variable so pydub can find it
            os.environ["PATH"] = exe_dir + os.pathsep + os.environ.get("PATH", "")
            return True, ffmpeg_exe

        # Check in a subdirectory (common pattern)
        ffmpeg_dir = os.path.join(exe_dir, "ffmpeg")
        if os.path.exists(ffmpeg_dir):
            ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
                return True, ffmpeg_exe

    # Check in the application directory (for development)
    # Get project root path (go up from src/back/utils.py to project root)
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        # Running as script - go up from src/back/utils.py to project root
        current_file = os.path.abspath(__file__)
        # Go up three levels: from src/back/utils.py to project root
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    ffmpeg_exe = os.path.join(app_path, "ffmpeg.exe")
    if os.path.exists(ffmpeg_exe):
        os.environ["PATH"] = app_path + os.pathsep + os.environ.get("PATH", "")
        return True, ffmpeg_exe

    # Check in ffmpeg subdirectory
    ffmpeg_dir = os.path.join(app_path, "ffmpeg")
    logger.debug(f"Checking for ffmpeg in subdirectory: {ffmpeg_dir}")
    if os.path.exists(ffmpeg_dir):
        ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_exe):
            # Return the full path to the executable, normalized
            ffmpeg_exe = os.path.normpath(os.path.abspath(ffmpeg_exe))
            logger.info(f"Found ffmpeg in project subdirectory: {ffmpeg_exe}")
            os.environ["PATH"] = os.path.dirname(ffmpeg_exe) + os.pathsep + os.environ.get("PATH", "")
            return True, ffmpeg_exe
        else:
            logger.debug(f"ffmpeg directory exists but ffmpeg.exe not found: {ffmpeg_exe}")

    # Try to test if ffmpeg works
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode == 0:
            return True, "ffmpeg"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    logger.warning("ffmpeg not found in any of the checked locations")
    return False, None


def _patch_subprocess_for_windows():
    """Patch subprocess to suppress console window on Windows when running as .exe.

    This is called lazily to avoid import-time issues with PyInstaller.
    """
    global _subprocess_patched

    if _subprocess_patched:
        return

    if sys.platform == 'win32' and getattr(sys, 'frozen', False):
        def _popen_with_no_window(*args, **kwargs):
            """Wrapper for subprocess.Popen that suppresses console window on Windows."""
            # Add CREATE_NO_WINDOW flag to prevent console window
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            else:
                # Combine with existing flags
                kwargs['creationflags'] |= subprocess.CREATE_NO_WINDOW
            return _original_popen(*args, **kwargs)

        def _run_with_no_window(*args, **kwargs):
            """Wrapper for subprocess.run that suppresses console window on Windows."""
            # Add CREATE_NO_WINDOW flag to prevent console window
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            else:
                # Combine with existing flags
                kwargs['creationflags'] |= subprocess.CREATE_NO_WINDOW
            return _original_run(*args, **kwargs)

        # Apply the patches
        subprocess.Popen = _popen_with_no_window
        subprocess.run = _run_with_no_window
        _subprocess_patched = True
        logger.debug("Patched subprocess to suppress console windows")


def configure_pydub(ffmpeg_path):
    """Configure pydub to use the specified ffmpeg path.

    Args:
        ffmpeg_path: Path to ffmpeg executable or directory containing it
    """
    # Patch subprocess before configuring pydub (lazy patching to avoid import issues)
    _patch_subprocess_for_windows()

    logger.debug(f"Configuring pydub with ffmpeg_path: {ffmpeg_path}")

    if not PYDUB_AVAILABLE:
        logger.warning("pydub is not available, cannot configure ffmpeg")
        return

    if not ffmpeg_path:
        logger.warning("ffmpeg_path is empty, cannot configure pydub")
        return

    # Set pydub converter to use the explicit ffmpeg path
    if ffmpeg_path != "ffmpeg":  # Not just in PATH, but a specific path
        # Normalize the path first
        ffmpeg_path = os.path.normpath(ffmpeg_path)

        # If ffmpeg_path is a directory, get the exe
        if os.path.isdir(ffmpeg_path):
            ffmpeg_exe = os.path.join(ffmpeg_path, "ffmpeg.exe")
        elif os.path.isfile(ffmpeg_path):
            # Already a file path
            ffmpeg_exe = ffmpeg_path
        else:
            # Might be a file path that needs checking
            if ffmpeg_path.endswith(".exe"):
                ffmpeg_exe = ffmpeg_path
            else:
                # Try as directory first, then as file
                test_dir = os.path.join(ffmpeg_path, "ffmpeg.exe")
                if os.path.exists(test_dir):
                    ffmpeg_exe = test_dir
                else:
                    ffmpeg_exe = ffmpeg_path

        # Convert to absolute path and normalize
        ffmpeg_exe = os.path.normpath(os.path.abspath(ffmpeg_exe))

        # Only set if the file actually exists
        if os.path.exists(ffmpeg_exe) and os.path.isfile(ffmpeg_exe):
            # Ensure the directory is in PATH for subprocess calls
            ffmpeg_dir = os.path.dirname(ffmpeg_exe)
            current_path = os.environ.get("PATH", "")
            if ffmpeg_dir not in current_path:
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path

            # For Windows, pydub needs the full path to the executable
            # Use absolute path with proper Windows formatting
            ffmpeg_exe_abs = os.path.abspath(ffmpeg_exe)

            # Set pydub converter
            # On Windows, pydub can use either:
            # 1. Full path to executable: "C:/path/to/ffmpeg.exe"
            # 2. Directory path if ffmpeg is in PATH: "ffmpeg"
            # We'll use the full path to be explicit
            # Use forward slashes as pydub handles them better cross-platform
            # IMPORTANT: Keep the original case (.exe not .EXE) as Windows is case-sensitive in some contexts
            # Ensure we preserve lowercase .exe extension
            ffmpeg_exe_for_pydub = ffmpeg_exe_abs.replace("\\", "/")
            # Fix case if it got converted to uppercase
            if ffmpeg_exe_for_pydub.endswith(".EXE"):
                ffmpeg_exe_for_pydub = ffmpeg_exe_for_pydub[:-4] + ".exe"
            AudioSegment.converter = ffmpeg_exe_for_pydub
            AudioSegment.ffmpeg = ffmpeg_exe_for_pydub
            logger.info(f"Configured pydub converter to: {ffmpeg_exe_for_pydub}")

            # CRITICAL: pydub uses ffprobe for media info via mediainfo_json
            # Without ffprobe, AudioSegment.from_file() will fail
            ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")
            if os.path.exists(ffprobe_exe):
                ffprobe_exe_abs = os.path.abspath(ffprobe_exe).replace("\\", "/")
                # Fix case if needed
                if ffprobe_exe_abs.endswith(".EXE"):
                    ffprobe_exe_abs = ffprobe_exe_abs[:-4] + ".exe"
                AudioSegment.ffprobe = ffprobe_exe_abs
                logger.info(f"Configured pydub ffprobe to: {ffprobe_exe_abs}")
            else:
                logger.error(f"ffprobe.exe not found at: {ffprobe_exe}")
                logger.error("pydub requires ffprobe.exe to read media file information!")
                logger.error("The error '[WinError 2] The system cannot find the file specified' is because ffprobe is missing.")
                logger.error("Please download ffprobe.exe and place it in the ffmpeg folder.")
                # Try to use ffmpeg as fallback, but this likely won't work for mediainfo_json
                AudioSegment.ffprobe = ffmpeg_exe_for_pydub
                logger.warning("Using ffmpeg as fallback for ffprobe (this may not work)")

            # IMPORTANT: Also ensure the directory is in PATH for subprocess calls
            # pydub uses subprocess.Popen which needs ffmpeg in PATH or as full path
            # We've already added it to PATH above, but let's make sure
            import subprocess
            try:
                # Test if ffmpeg can be called directly
                test_result = subprocess.run(
                    [ffmpeg_exe_abs, "-version"],
                    capture_output=True,
                    timeout=2,
                    text=True
                )
                if test_result.returncode != 0:
                    # If direct call fails, there might be a dependency issue
                    pass
            except Exception:
                # If test fails, continue anyway - might work during actual use
                pass
