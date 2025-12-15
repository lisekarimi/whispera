"""Build script for creating Windows executable using PyInstaller."""

import os
import shutil
import sys

try:
    import PyInstaller.__main__
except ImportError:
    print("Error: PyInstaller is not installed.")
    print("Please install it using: uv sync")
    print("Or: pip install pyinstaller")
    sys.exit(1)

# Determine separator for --add-data based on OS
if sys.platform == 'win32':
    sep = ';'
else:
    sep = ':'

# Clean previous builds
print("Cleaning previous builds...")
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('Whispera.spec'):
    os.remove('Whispera.spec')

# PyInstaller arguments
args = [
    'main.py',
    '--name=Whispera',
    '--onefile',
    '--windowed',  # No console window (GUI app)
    '--hidden-import=openai',
    '--hidden-import=dotenv',
    '--hidden-import=src.back',
    '--hidden-import=src.front',
    '--collect-all=openai',
    '--noconfirm',
    '--clean',
]

# SECURITY: Do NOT include .env file in the build
# Users should create their own .env file next to the exe, or use the GUI to enter API key
print("🔒 Security: .env file will NOT be included in the build.")
print("   Users can either:")
print("   1. Create a .env file next to the .exe with: OPENAI_API_KEY=your_key")
print("   2. Enter the API key directly in the GUI (more secure)")

PyInstaller.__main__.run(args)

print("\n" + "="*50)
print("✅ Build complete! Executable is in the 'dist' folder.")
print("="*50)
print("\n📝 IMPORTANT:")
print("   1. The executable is: dist\\Whispera.exe")
print("\n🔒 SECURITY - API Key Configuration:")
print("   Option 1 (Recommended): Enter API key directly in the GUI")
print("      - Launch the app and enter your API key in the GUI")
print("      - Click 'Save' to store it securely in a .env file next to the exe")
print("   Option 2: Create a .env file manually")
print("      - Create a file named '.env' in the same folder as the .exe")
print("      - Add this line: OPENAI_API_KEY=your_api_key_here")
print("\n⚠️  SECURITY NOTE:")
print("   The .env file is NOT included in the build for security reasons.")
print("   Each user must provide their own API key.")
print("\n📦 FFmpeg for Large Files:")
print("   For automatic file splitting, ffmpeg is needed.")
print("   Option 1: Place ffmpeg.exe in the same folder as the .exe")
print("   Option 2: Install ffmpeg system-wide (add to PATH)")
print("   Download: https://ffmpeg.org/download.html")
print("   Or use: winget install ffmpeg")
print("\n")
