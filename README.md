# YT Downloader

A simple YouTube downloader GUI for Windows using Python, yt-dlp, and customtkinter. Downloads videos or audio in MP3/MP4 format with selectable quality.

<img width="595" height="511" alt="image" src="https://github.com/user-attachments/assets/c7a8e251-00e7-4cf6-a514-557cc58012c7" />

## Features
- Download YouTube videos as MP3 or MP4
- Select audio/video quality
- Choose download folder
- Progress bar and status updates
- Remembers last settings

## Requirements
- **Python 3.8+** (recommended)
- **FFmpeg** (must be on your system PATH)
- **pip** (Python package manager)

## Installation

1. **Clone or download this repository**

2. **Install required Python packages:**

```sh
pip install yt-dlp customtkinter
```

3. **Install FFmpeg:**
- Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Extract and add the `bin` folder to your system PATH
- To verify, run in terminal:
  ```sh
  ffmpeg -version
  ```

## Usage

1. Run the app:

```sh
python ytdownload.py
```

2. Enter a YouTube URL, select format and quality, choose a folder, and click **Download**.

## Notes
- Downloads are saved to the selected folder.
- MP3 conversion uses FFmpeg.
- Settings are saved in `%APPDATA%/yt_downloader/config.json`.

## Troubleshooting
- If you see errors about FFmpeg, make sure it is installed and on your PATH.
- If you have issues with customtkinter, ensure you installed the correct package (`customtkinter`).

## License
MIT License
