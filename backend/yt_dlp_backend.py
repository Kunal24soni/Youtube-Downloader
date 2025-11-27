import os
import re
import requests
from typing import Optional, Dict, Any, Callable

try:
    from yt_dlp import YoutubeDL
except Exception:  # pragma: no cover - import guarded
    YoutubeDL = None

BASE_THUMB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".thumbnails")

def _make_folder_if_not_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def _sanitize_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9 _-]", "_", name)
    name = name.strip()
    if not name:
        return "thumbnail"
    return name


def _download_thumbnail(thumbnail_url: str, title: str, out_dir: Optional[str] = None) -> Optional[str]:
    try:
        folder = out_dir or BASE_THUMB_DIR
        _make_folder_if_not_exists(folder)
        safe_title = _sanitize_filename(title)
        filename = f"{safe_title}.jpg"
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            return file_path
        resp = requests.get(thumbnail_url, timeout=15)
        resp.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(resp.content)
        return file_path
    except Exception:
        return None


def get_info(url: str) -> Dict[str, Any]:
    """Return metadata for a video using yt-dlp.

    Returns a dict with keys: title, id, thumbnail, channel, duration, formats (list of dicts)
    """
    if YoutubeDL is None:
        raise RuntimeError("yt_dlp not installed")
    ydl_opts = {"skip_download": True, "quiet": True, "no_warnings": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    title = info.get("title")
    thumbnail = info.get("thumbnail")
    thumb_path = _download_thumbnail(thumbnail, title) if thumbnail else None
    
    # Get channel and duration
    channel = info.get("channel") or info.get("uploader") or "Unknown"
    duration = info.get("duration") or 0  # in seconds
    
    formats = []
    for f in info.get("formats", []):
        formats.append({
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "height": f.get("height"),
            "width": f.get("width"),
            "filesize": f.get("filesize") or f.get("filesize_approx"),
            "format_note": f.get("format_note"),
            "vcodec": f.get("vcodec"),
            "acodec": f.get("acodec"),
        })
    return {"title": title, "id": info.get("id"), "thumbnail": thumb_path, "channel": channel, "duration": duration, "formats": formats}


def download(url: str, format_selector: str, output_path: str, progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
    """Download using yt-dlp.

    format_selector examples:
      - "bestaudio" for audio
      - "bestvideo[height<=1080]+bestaudio/best[height<=1080]" for video
    progress_hook receives yt-dlp progress dicts.
    """
    if YoutubeDL is None:
        raise RuntimeError("yt_dlp not installed")

    def _hook(d):
        if progress_hook:
            progress_hook(d)

    opts = {
        "format": format_selector,
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "progress_hooks": [_hook],
    }
    _make_folder_if_not_exists(output_path)
    with YoutubeDL(opts) as ydl:
        ydl.download([url])

