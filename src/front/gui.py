"""GUI for the Audio Transcription App."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from src.back.constants import (
    WINDOW_TITLE,
    WINDOW_SIZE,
    FONT_TITLE,
    FONT_NORMAL,
    FONT_TEXT,
    PROGRESS_READY,
    SUPPORTED_FORMATS,
    MAX_FILE_SIZE_BYTES,
)
from src.back.transcription import TranscriptionAssistant
from src.back.env_manager import read_env_file, write_env_file


class TranscriptionGUI:
    """Tkinter GUI for the audio transcription app."""

    def __init__(self, initial_api_key=None):
        """Initialize the GUI application."""
        # Initialize assistant with API key if available
        self.assistant = TranscriptionAssistant(api_key=initial_api_key)
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(True, True)

        # Selected file path
        self.selected_file = None

        # Load API key (ffmpeg is auto-detected in ffmpeg/ folder at project root)
        self.loaded_api_key = initial_api_key or ""

        # Status message for startup/download progress
        self.status_message = tk.StringVar(value="Initializing...")

        self._create_widgets()
        self._load_api_key()

        # Check for ffmpeg after GUI is created (so we can show messages)
        self.root.after(100, self._check_ffmpeg_on_startup)

    def _create_widgets(self):
        """Create and layout GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text=WINDOW_TITLE,
            font=FONT_TITLE
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Select an MP3 or MP4 file to transcribe. Large files will be automatically split into chunks.",
            font=FONT_NORMAL
        )
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # Status message area (for startup/download messages)
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.status_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_message,
            font=("Arial", 8),
            foreground="blue",
            wraplength=700
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # API Key frame
        api_frame = ttk.LabelFrame(main_frame, text="OpenAI API Key", padding="5")
        api_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)

        # API Key label
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)

        # API Key entry (password style for security)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            show="*",
            width=50
        )
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))

        # Save API Key button
        self.save_api_btn = ttk.Button(
            api_frame,
            text="Save",
            command=self._save_api_key
        )
        self.save_api_btn.grid(row=0, column=2)

        # File selection frame
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # Select file button
        self.select_btn = ttk.Button(
            file_frame,
            text="Select Audio/Video File",
            command=self._select_file
        )
        self.select_btn.grid(row=0, column=0, padx=(0, 10))

        # Selected file label
        self.file_label = ttk.Label(
            file_frame,
            text="No file selected",
            foreground="gray"
        )
        self.file_label.grid(row=0, column=1, sticky=tk.W)

        # Transcribe button
        self.transcribe_btn = ttk.Button(
            main_frame,
            text="Transcribe",
            command=self._transcribe_file,
            state="disabled"
        )
        self.transcribe_btn.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # Progress bar
        self.progress_var = tk.StringVar(value=PROGRESS_READY)
        self.progress_label = ttk.Label(
            main_frame,
            textvariable=self.progress_var,
            font=FONT_NORMAL
        )
        self.progress_label.grid(row=6, column=0, columnspan=2, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Transcription text area
        text_frame = ttk.LabelFrame(main_frame, text="Transcription", padding="5")
        text_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=70,
            height=15,
            font=FONT_TEXT
        )
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Copy button
        self.copy_btn = ttk.Button(
            main_frame,
            text="Copy to Clipboard",
            command=self._copy_to_clipboard,
            state="disabled"
        )
        self.copy_btn.grid(row=9, column=0, columnspan=2, pady=(0, 10))

    def _load_api_key(self):
        """Load API key from .env file and populate the field."""
        if self.loaded_api_key:
            self.api_key_var.set(self.loaded_api_key)
            self.assistant.set_api_key(self.loaded_api_key)

    def _check_ffmpeg_on_startup(self):
        """Check for ffmpeg tools on startup and show status messages."""
        import sys
        from src.back.config import get_application_path
        from src.back.ffmpeg_downloader import download_ffmpeg_tools

        if sys.platform == 'win32':
            app_path = get_application_path()
            ffmpeg_dir = os.path.join(app_path, 'ffmpeg')
            ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
            ffprobe_exe = os.path.join(ffmpeg_dir, 'ffprobe.exe')

            # Check what's missing
            if not os.path.exists(ffprobe_exe) or (not os.path.exists(ffmpeg_exe) and not os.path.exists(ffprobe_exe)):
                # Show download dialog
                self.status_message.set("Checking for ffmpeg tools...")
                self.root.update_idletasks()

                # Download in a separate thread to avoid freezing GUI
                def download_thread():
                    def update_status(msg):
                        """Update status message in GUI thread safely."""
                        self.root.after(0, lambda: self.status_message.set(msg))

                    # Pass callback to download function
                    download_ffmpeg_tools(app_path, status_callback=update_status)

                    # Check final status and hide status after a delay
                    def hide_status_after_delay():
                        """Hide status frame after showing final message."""
                        self.root.after(3000, lambda: self.status_frame.grid_remove())

                    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
                        self.root.after(0, lambda: self.status_message.set("✅ Ready - ffmpeg tools are available"))
                        self.root.after(0, hide_status_after_delay)
                    elif os.path.exists(ffmpeg_exe):
                        self.root.after(0, lambda: self.status_message.set("⚠️ Warning - ffmpeg.exe found but ffprobe.exe is missing"))
                        self.root.after(0, hide_status_after_delay)
                    else:
                        self.root.after(0, lambda: self.status_message.set("❌ Error - ffmpeg tools not found. Please download manually."))

                thread = threading.Thread(target=download_thread)
                thread.daemon = True
                thread.start()
            else:
                self.status_message.set("✅ Ready - All tools available")
                # Hide status after showing ready message
                self.root.after(2000, lambda: self.status_frame.grid_remove())
        else:
            self.status_message.set("✅ Ready")
            # Hide status after showing ready message
            self.root.after(2000, lambda: self.status_frame.grid_remove())

    def _save_api_key(self):
        """Save API key to .env file."""
        api_key = self.api_key_var.get().strip()

        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key.")
            return

        try:
            # Read existing .env file
            env_vars = read_env_file()

            # Update API key
            env_vars['OPENAI_API_KEY'] = api_key

            # Write back to .env file (ffmpeg uses default location, no need to save path)
            write_env_file(env_vars)

            # Update the assistant
            self.assistant.set_api_key(api_key)

            messagebox.showinfo("Success", "API key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}")

    def _select_file(self):
        """Open file dialog to select audio/video file."""
        # Build file types string
        file_types_str = " ".join([f"*{ext}" for ext in SUPPORTED_FORMATS])

        file_path = filedialog.askopenfilename(
            title="Select Audio or Video File",
            filetypes=[
                ("Audio/Video Files", file_types_str),
                ("MP3 Files", "*.mp3"),
                ("MP4 Files", "*.mp4"),
                ("All Audio Files", file_types_str),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)

            # Get file size for display
            try:
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)

                # Show filename and size
                file_info = f"{filename} ({size_mb:.1f}MB)"

                # Color code based on size
                if file_size > MAX_FILE_SIZE_BYTES:
                    # File is large but we can split it automatically
                    self.file_label.config(text=file_info, foreground="orange")
                    # Show info message about automatic splitting
                    response = messagebox.askyesno(
                        "Large File Detected",
                        f"File size: {size_mb:.1f}MB (exceeds {MAX_FILE_SIZE_BYTES / (1024*1024):.0f}MB limit)\n\n"
                        f"The app will automatically split this file into chunks and transcribe each part.\n"
                        f"This may take longer but will work for files of any size.\n\n"
                        f"Continue with automatic splitting?",
                        icon="question"
                    )
                    if not response:
                        return
                # File is acceptable (will be split automatically if needed)
                elif file_size > MAX_FILE_SIZE_BYTES * 0.9:  # > 90% of limit
                    self.file_label.config(text=file_info, foreground="orange")
                else:
                    self.file_label.config(text=file_info, foreground="black")
            except Exception:
                self.file_label.config(text=filename, foreground="black")

            # Enable transcribe button only if API key is set
            if self.assistant.client:
                self.transcribe_btn.config(state="normal")
            else:
                messagebox.showwarning("API Key Required", "Please enter and save your OpenAI API key first.")

    def _update_progress(self, message, value):
        """Update progress bar and label."""
        self.progress_var.set(message)
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def _transcribe_file(self):
        """Transcribe the selected file."""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first.")
            return

        if not self.assistant.client:
            messagebox.showerror("Error", "Please enter and save your OpenAI API key first.")
            return

        # Disable buttons during transcription
        self.select_btn.config(state="disabled")
        self.transcribe_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Transcribing... Please wait...")

        # Run transcription in a separate thread to avoid freezing GUI
        thread = threading.Thread(target=self._transcribe_thread)
        thread.daemon = True
        thread.start()

    def _transcribe_thread(self):
        """Run transcription in a separate thread."""
        try:
            result = self.assistant.process_audio(
                self.selected_file,
                progress_callback=self._update_progress
            )

            # Update GUI in main thread
            self.root.after(0, self._transcription_complete, result)
        except Exception as e:
            self.root.after(0, self._transcription_error, str(e))

    def _transcription_complete(self, transcription):
        """Handle transcription completion."""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, transcription)
        self.select_btn.config(state="normal")
        self.transcribe_btn.config(state="normal")
        self.copy_btn.config(state="normal")
        self.progress_bar['value'] = 0
        self.progress_var.set(PROGRESS_READY)

    def _transcription_error(self, error_msg):
        """Handle transcription error."""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, f"Error: {error_msg}")
        self.select_btn.config(state="normal")
        self.transcribe_btn.config(state="normal")
        self.progress_bar['value'] = 0
        self.progress_var.set("Error occurred")
        messagebox.showerror("Transcription Error", error_msg)

    def _copy_to_clipboard(self):
        """Copy transcription text to clipboard."""
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Transcription copied to clipboard!")

    def launch(self):
        """Launch the GUI application."""
        self.root.mainloop()
