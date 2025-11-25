import os
from typing import Dict, Any, Optional, Callable

try:
	from . import yt_dlp_backend as ytdlp
except Exception:
	ytdlp = None

try:
	from . import pytubefix as pfix
except Exception:
	pfix = None


def get_info(url: str) -> Dict[str, Any]:
	"""Get video info. Try yt-dlp first, then pytubefix.

	Returns a dict with keys: title, thumbnail, formats
	"""
	last_err = None
	if ytdlp is not None:
		try:
			return ytdlp.get_info(url)
		except Exception as e:
			last_err = e
	if pfix is not None:
		try:
			return pfix.get_info(url)
		except Exception as e:
			last_err = e
	raise RuntimeError(f"No backend available or both backends failed: {last_err}")


def _select_yt_format(format_choice: str, quality: str) -> str:
	# format_choice: 'mp3(audio)', 'mp4(video)', 'webm(video)'
	if "audio" in format_choice or format_choice.startswith("mp3"):
		return "bestaudio"
	# video: map quality like '1080p' to a yt-dlp selector
	if quality and quality.endswith("p"):
		try:
			h = int(quality[:-1])
			return f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"
		except Exception:
			pass
	return "best"


def download(url: str, format_choice: str, quality: str, dest: Optional[str] = None, progress_hook: Optional[Callable[[dict], None]] = None) -> None:
	"""Download a video or audio. Uses yt-dlp if available, else pytubefix.

	- `format_choice` examples: 'mp3(audio)', 'mp4(video)'
	- `quality` examples: '1080p', '720p'
	- `dest` is the directory to save into (defaults to current working dir)
	- `progress_hook` will be called with backend-specific progress dicts
	"""
	out = dest or os.getcwd()
	if ytdlp is not None:
		try:
			fmt = _select_yt_format(format_choice, quality)
			ytdlp.download(url, fmt, out, progress_hook=progress_hook)
			return
		except Exception:
			# fall through to pytubefix
			pass
	if pfix is not None:
		# pytubefix download expects quality string
		pfix.download(url, quality, out, progress_hook=progress_hook)
		return
	raise RuntimeError("No download backend available")
