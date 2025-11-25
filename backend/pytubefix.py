import os
import re
import requests
from typing import Optional, Dict, Any, Callable

try:
	from pytubefix import YouTube
except Exception:  # pragma: no cover - import guarded
	YouTube = None

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
	if YouTube is None:
		raise RuntimeError("pytubefix not installed")
	yt = YouTube(url)
	title = getattr(yt, "title", None)
	thumbnail = getattr(yt, "thumbnail_url", None)
	thumb_path = _download_thumbnail(thumbnail, title) if thumbnail else None
	# collect streams
	formats = []
	try:
		streams = yt.streams
		for s in streams:
			fmt = {
				"itag": getattr(s, "itag", None),
				"mime_type": getattr(s, "mime_type", None),
				"res": getattr(s, "resolution", None),
				"type": ("audio" if getattr(s, "abr", None) else "video"),
				"filesize": getattr(s, "filesize", None),
			}
			formats.append(fmt)
	except Exception:
		pass
	return {"title": title, "thumbnail": thumb_path, "formats": formats}


def download(url: str, quality: str, output_path: str, progress_hook: Optional[Callable[[dict], None]] = None) -> None:
	if YouTube is None:
		raise RuntimeError("pytubefix not installed")
	yt = YouTube(url)
	_make_folder_if_not_exists(output_path)
	# choose audio or video
	is_audio = quality.lower().startswith("audio") or quality.lower().endswith("mp3")
	if is_audio:
		# choose first audio stream
		stream = None
		for s in yt.streams:
			if getattr(s, "abr", None):
				stream = s
				break
		if stream is None:
			raise RuntimeError("No audio stream available")
		out = stream.download(output_path)
		if progress_hook:
			progress_hook({"status": "finished", "filename": out})
		return

	# for video: try to match resolution number like '1080p'
	desired = None
	if isinstance(quality, str) and quality.endswith("p"):
		desired = quality

	stream = None
	for s in yt.streams:
		res = getattr(s, "resolution", None)
		if desired and res == desired:
			stream = s
			break
	if stream is None:
		# fallback to highest progressive
		for s in reversed(yt.streams):
			if getattr(s, "resolution", None):
				stream = s
				break
	if stream is None:
		raise RuntimeError("No suitable video stream found")
	out = stream.download(output_path)
	if progress_hook:
		progress_hook({"status": "finished", "filename": out})
