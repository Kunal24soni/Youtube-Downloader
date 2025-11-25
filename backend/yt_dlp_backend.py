from pytubefix import YouTube
import requests
import os
import re
from typing import Optional


output_path = os.path.expanduser("D:/projects/Fetchtube/.thumbnails")


def make_folder_if_not_exists(path: str):
    if not os.path.exists(path):
        os.mkdir(path, exist_ok=True)


def _sanitize_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9 _-]", "_", name)
    name = name.strip()
    if not name:
        return "thumbnail"
    return name


def fetch_thumbnail(url: str, out_dir: Optional[str] = None) -> Optional[str]:
    try:
        yt = YouTube(url)
        thumbnail_url = yt.thumbnail_url
        title = yt.title

        folder = out_dir or output_path
        make_folder_if_not_exists(folder)

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
