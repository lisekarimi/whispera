"""Helper script to download and setup ffmpeg for Windows."""

import os
import sys
import urllib.request
import zipfile
import shutil

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_ZIP = "ffmpeg.zip"
FFMPEG_DIR = "ffmpeg"

def download_ffmpeg():
    """Download ffmpeg for Windows."""
    print("Downloading ffmpeg...")
    print(f"URL: {FFMPEG_URL}")
    print("This may take a few minutes...")

    try:
        # Download the zip file
        urllib.request.urlretrieve(FFMPEG_URL, FFMPEG_ZIP)
        print("✓ Download complete!")

        # Extract the zip file
        print("Extracting ffmpeg...")
        with zipfile.ZipFile(FFMPEG_ZIP, 'r') as zip_ref:
            zip_ref.extractall(".")

        # Find ffmpeg.exe and ffprobe.exe in the extracted folder
        ffmpeg_found = False
        ffprobe_found = False

        for root, dirs, files in os.walk("."):
            # Look for the bin directory which contains the executables
            if "bin" in dirs and "ffmpeg-" in root:
                bin_dir = os.path.join(root, "bin")
                if os.path.exists(bin_dir):
                    # Create target directory
                    if not os.path.exists(FFMPEG_DIR):
                        os.makedirs(FFMPEG_DIR)

                    # Copy ffmpeg.exe
                    ffmpeg_src = os.path.join(bin_dir, "ffmpeg.exe")
                    if os.path.exists(ffmpeg_src):
                        shutil.copy(ffmpeg_src, os.path.join(FFMPEG_DIR, "ffmpeg.exe"))
                        print(f"✓ ffmpeg.exe found and copied to {FFMPEG_DIR}/")
                        ffmpeg_found = True

                    # Copy ffprobe.exe (REQUIRED for pydub!)
                    ffprobe_src = os.path.join(bin_dir, "ffprobe.exe")
                    if os.path.exists(ffprobe_src):
                        shutil.copy(ffprobe_src, os.path.join(FFMPEG_DIR, "ffprobe.exe"))
                        print(f"✓ ffprobe.exe found and copied to {FFMPEG_DIR}/")
                        ffprobe_found = True

                    if ffmpeg_found:
                        break

        # Fallback: search for files directly (older extraction structure)
        if not ffmpeg_found:
            for root, dirs, files in os.walk("."):
                if "ffmpeg.exe" in files:
                    ffmpeg_path = os.path.join(root, "ffmpeg.exe")
                    if not os.path.exists(FFMPEG_DIR):
                        os.makedirs(FFMPEG_DIR)
                    shutil.copy(ffmpeg_path, os.path.join(FFMPEG_DIR, "ffmpeg.exe"))
                    print(f"✓ ffmpeg.exe found and copied to {FFMPEG_DIR}/")
                    ffmpeg_found = True

                    # Also look for ffprobe.exe in the same directory
                    ffprobe_path = os.path.join(root, "ffprobe.exe")
                    if os.path.exists(ffprobe_path):
                        shutil.copy(ffprobe_path, os.path.join(FFMPEG_DIR, "ffprobe.exe"))
                        print(f"✓ ffprobe.exe found and copied to {FFMPEG_DIR}/")
                        ffprobe_found = True
                    break

        if not ffmpeg_found:
            print("❌ Error: ffmpeg.exe not found in the downloaded archive!")
            return False

        if not ffprobe_found:
            print("⚠️  Warning: ffprobe.exe not found in the archive!")
            print("   The app needs ffprobe.exe for reading media file information.")
            print("   You may need to download it separately or the archive structure may have changed.")

        # Clean up
        os.remove(FFMPEG_ZIP)
        # Remove extracted folder (find and remove it)
        for root, dirs, files in os.walk("."):
            if "ffmpeg-" in root and os.path.basename(root).startswith("ffmpeg-"):
                shutil.rmtree(root, ignore_errors=True)
                break

        print("\n✅ ffmpeg setup complete!")
        print(f"ffmpeg.exe is now in the '{FFMPEG_DIR}' folder.")
        if ffprobe_found:
            print(f"ffprobe.exe is also in the '{FFMPEG_DIR}' folder.")
        print("The app will automatically find them when you run it.")
        return True

    except Exception as e:
        print(f"\n❌ Error downloading ffmpeg: {e}")
        print("\nYou can manually download ffmpeg from:")
        print("https://ffmpeg.org/download.html")
        print("\nThen place ffmpeg.exe in the same folder as the app.")
        return False

if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is for Windows only.")
        print("For other platforms, install ffmpeg using your package manager:")
        print("  - macOS: brew install ffmpeg")
        print("  - Linux: sudo apt install ffmpeg")
        sys.exit(1)

    print("=" * 50)
    print("FFmpeg Downloader for Audio Transcription App")
    print("=" * 50)
    print()

    response = input("Download and setup ffmpeg? (y/n): ").strip().lower()
    if response == 'y':
        download_ffmpeg()
    else:
        print("Cancelled. You can run this script again later.")
        print("Or manually install ffmpeg from: https://ffmpeg.org/download.html")
