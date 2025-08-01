import os
import threading
import json
import yt_dlp
import customtkinter as ctk
from tkinter import filedialog

# Configuration
CONFIG_DIR = os.path.join(os.getenv('APPDATA'), 'ytmp3_downloader')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# Default configuration
default_config = {
    'download_folder': os.path.expanduser('~'),
    'format': 'mp3',
    'quality': '192'
}

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Load & save settings
def load_config():
    cfg = default_config.copy()
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            for k in default_config:
                if k in data:
                    cfg[k] = data[k]
    except Exception:
        pass
    return cfg

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f)

config = load_config()

# Configure customtkinter appearance
ctk.set_appearance_mode('System')  # Modes: System, Dark, Light
ctk.set_default_color_theme('blue')  # Themes: blue, dark-blue, green

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('YT Downloader')
        self.geometry('600x480')
        self.resizable(False, False)

        # --- URL Input ---
        self.url_entry = ctk.CTkEntry(self, placeholder_text='YouTube URL', width=550)
        self.url_entry.pack(pady=(20, 10))

        # --- Folder Selection ---
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(fill='x', padx=25, pady=(0, 20))
        self.folder_var = ctk.StringVar(value=config['download_folder'])
        self.folder_entry = ctk.CTkEntry(self.folder_frame, textvariable=self.folder_var)
        self.folder_entry.pack(side='left', expand=True, fill='x', pady=10, padx=(10,0))
        self.browse_button = ctk.CTkButton(self.folder_frame, text='Browse', width=100, command=self.browse_folder)
        self.browse_button.pack(side='right', pady=10, padx=10)

        # --- Format & Quality in one frame ---
        self.fq_frame = ctk.CTkFrame(self)
        self.fq_frame.pack(fill='x', padx=25, pady=(0, 20))

        # Format selection
        self.format_var = ctk.StringVar(value=config['format'])
        ctk.CTkLabel(self.fq_frame, text='Format:').pack(anchor='w', padx=10, pady=(10,0))
        fmt_inner = ctk.CTkFrame(self.fq_frame)
        fmt_inner.pack(anchor='w', padx=10, pady=5)
        self.mp3_radio = ctk.CTkRadioButton(fmt_inner, text='MP3', variable=self.format_var, value='mp3', command=self.refresh_quality)
        self.mp4_radio = ctk.CTkRadioButton(fmt_inner, text='MP4', variable=self.format_var, value='mp4', command=self.refresh_quality)
        self.mp3_radio.pack(side='left', padx=10)
        self.mp4_radio.pack(side='left', padx=10)

        # Quality selection
        self.quality_var = ctk.StringVar(value=config['quality'])
        ctk.CTkLabel(self.fq_frame, text='Quality:').pack(anchor='w', padx=10, pady=(10,0))
        self.qual_inner = ctk.CTkFrame(self.fq_frame)
        self.qual_inner.pack(anchor='w', padx=10, pady=5)
        self.quality_radios = []
        self.refresh_quality()

        # --- Status Label (hidden initially) ---
        self.status_label = ctk.CTkLabel(self, text='', width=550)

        # --- Progress Bar (hidden until download) ---
        self.progress_bar = ctk.CTkProgressBar(self, width=550)
        self.progress_bar.set(0)

        # --- Action Buttons ---
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=(10,20))
        self.download_button = ctk.CTkButton(btn_frame, text='Download', width=120, command=self.start_download)
        self.exit_button = ctk.CTkButton(btn_frame, text='Exit', width=120, command=self.quit)
        self.download_button.pack(side='left', padx=20)
        self.exit_button.pack(side='left', padx=20)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def refresh_quality(self):
        # clear existing radios
        for rb in self.quality_radios:
            rb.destroy()
        self.quality_radios.clear()
        # new options based on format
        fmt = self.format_var.get()
        options = ['128','192','256','320'] if fmt == 'mp3' else ['360p','480p','720p','1080p']
        for opt in options:
            rb = ctk.CTkRadioButton(self.qual_inner, text=opt, variable=self.quality_var, value=opt)
            rb.pack(side='left', padx=10)
            self.quality_radios.append(rb)
        # restore saved or default
        self.quality_var.set(config['quality'] if config['format']==fmt and config['quality'] in options else options[0])
        config['format'] = fmt

    def show_progress(self):
        self.status_label.configure(text='')
        self.status_label.pack()
        self.progress_bar.pack(pady=(5, 10))

    def hide_progress(self):
        self.progress_bar.pack_forget()

    def set_status(self, message):
        self.status_label.configure(text=message)

    def progress_hook(self, d):
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total
                self.progress_bar.set(percent)

    def download(self, url, folder, fmt, quality):
        opts = {'quiet': True, 'no_warnings': True, 'outtmpl': os.path.join(folder, '%(title)s.%(ext)s')}
        if fmt == 'mp3':
            opts.update({
                'format': 'bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality
                }]
            })
        else:
            height = quality.replace('p','')
            opts.update({
                'format': f"bestvideo[height<={height}]+bestaudio/best",
                'merge_output_format': 'mp4'
            })
        opts['progress_hooks'] = [self.progress_hook]
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.after(0, lambda: self.set_status('Download complete!'))
        except Exception as e:
            self.after(0, lambda: self.set_status(f'Error: {e}'))
        finally:
            self.after(0, self.hide_progress)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.set_status('Please enter a YouTube URL.')
            return
        folder = self.folder_var.get() or default_config['download_folder']
        fmt = self.format_var.get()
        quality = self.quality_var.get()
        config.update(download_folder=folder, format=fmt, quality=quality)
        save_config(config)
        self.show_progress()
        threading.Thread(target=self.download, args=(url, folder, fmt, quality), daemon=True).start()

if __name__ == '__main__':
    print('Requires FFmpeg on PATH and customtkinter library.')
    app = App()
    app.mainloop()

# Build EXE directly to Desktop:
#   pyinstaller --onefile --windowed --name YTDownloader \
#     --distpath "%USERPROFILE%\Desktop" ytdownload.py
