import os, sys, threading
import tkinter as tk
from tkinter import messagebox, ttk,filedialog
from PIL import Image, ImageTk
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend import core as backend_core

ICON_PATH:Path = Path("Assets/icon.png")
DEFAULT_THUMB:Path = Path(".thumbnails/default.jpg")

def _grid(widget, row, col, **kw): widget.grid(row=row, column=col, **kw)
def _label(parent, text, **kw): return tk.Label(parent, text=text, **kw)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("FetchTube")
        self.root.geometry("800x600")
        self.root.minsize(800, 500)
        self.root.configure(bg="#55ff55")
        try:
            self.root.iconphoto(True, ImageTk.PhotoImage(Image.open(ICON_PATH)))
        except: pass
        self.video_cache = {}
        self.output_path:Path = os.path.join(str(Path.cwd()),"donwloads")
        self.create_widgets()

    def create_widgets(self):
        title = _label(self.root, "FetchTube", font=("roboto", 40, "bold"), bg="#FF0000", fg="white", borderwidth=2, relief="solid")
        title.pack(fill="x")
        
        self.main_frame = tk.Frame(self.root, borderwidth=2, relief="solid",bg="#fffda0")
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.url_entry = tk.Entry(self.main_frame, font=("courier", 12), relief="flat", borderwidth=2, fg="gray")
        _grid(self.url_entry, 1, 1, sticky="ew", pady=10, padx=10)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.url_entry.bind("<FocusIn>", lambda e: e.widget.delete(0, "end") if e.widget.get()=="enter a url" else None)
        self.url_entry.bind("<FocusOut>", lambda e: e.widget.insert(0, "enter a url") if not e.widget.get() else None)

        _grid(tk.Button(self.main_frame, text="X", command=lambda: self.url_entry.delete(0, "end"), width=3, height=1, relief="flat", bg="white"), 1, 2, sticky="ew", padx=5)
        _grid(tk.Button(self.main_frame, text="Fetch downloads", command=self.fetch, border=2, relief="solid",bg="#ff3232",activebackground="#ff1111"), 2, 1, sticky="ew", padx=10,)
        
        self.status_label_fetch = _label(self.main_frame, "Ready", fg="blue", font=("arial", 10),width=7)
        _grid(self.status_label_fetch, 2, 2, sticky="ew", padx=5)
        
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=0)
        self.download_widgets()

    def fetch(self):
        url = self.url_entry.get().strip()
        if not url: messagebox.showwarning("URL required", "Please enter a video URL"); return
        
        self.status_label_fetch.config(text="Fetching...", fg="orange")
        self.root.update_idletasks()
        
        def _work():
            try:
                if url in self.video_cache:
                    self.root.after(0, lambda: self.status_label_fetch.config(text="Loading from cache...", fg="blue"))
                    info = self.video_cache[url]
                else:
                    info = backend_core.get_info(url)
                    self.video_cache[url] = info
                self.root.after(0, lambda: self._update_info(info))
                self.root.after(0, lambda: self.status_label_fetch.config(text="Ready", fg="green"))
            except Exception as e:
                self.root.after(0, lambda: self.status_label_fetch.config(text="Error", fg="red"))
                self.root.after(0, lambda: messagebox.showerror("Fetch failed", str(e)))
        threading.Thread(target=_work, daemon=True).start()

    def _update_info(self, info):
        self.video_title.config(text=info.get("title") or "Unknown")
        self.video_channel.config(text=f"Channel: {info.get('channel') or 'Unknown'}")
        dur = info.get("duration") or 0
        self.video_duration.config(text=f"Duration: {dur//60}:{dur%60:02d}")
        
        try:
            thumb_path = info.get("thumbnail")
            img = Image.open(thumb_path) if (thumb_path and Path(thumb_path).exists()) else (Image.open(DEFAULT_THUMB) if DEFAULT_THUMB.exists() else None)
            if img:
                img = ImageTk.PhotoImage(img.resize((160, 100)))
                self.thumb.config(image=img)
                self.thumb.img = img
        except: pass

        self.format_quality_sizes = {}
        available_qualities = set()
        for fmt in info.get("formats") or []:
            if not (fs := fmt.get("filesize")) or fs <= 0: continue
            is_audio = (ac := fmt.get("acodec")) and ac != "none" and (not (vc := fmt.get("vcodec")) or vc == "none")
            is_video = (vc := fmt.get("vcodec")) and vc != "none"
            
            if is_audio: self.format_quality_sizes[("mp3(audio)", "audio")] = max(self.format_quality_sizes.get(("mp3(audio)", "audio"), 0), fs)
            if is_video and (h := fmt.get("height")):
                qual_str = f"{h}p"
                available_qualities.add(qual_str)
                for c in ("mp4(video)", "webm(video)"):
                    self.format_quality_sizes[(c, qual_str)] = max(self.format_quality_sizes.get((c, qual_str), 0), fs)
        
        # Update quality menu with available qualities, sorted by resolution
        sorted_quals = sorted(available_qualities, key=lambda x: int(x[:-1]))
        self.quality_menu.config(values=sorted_quals)
        if sorted_quals and self.quality_var.get() not in sorted_quals:
            self.quality_var.set(sorted_quals[-1])  # Set to highest available
        
        self._update_size_label()

    def _on_format_changed(self, *args):
        fmt = self.format_var.get()
        self.quality_menu.config(state="disabled" if "audio" in fmt or "mp3" in fmt else "readonly")
        self._update_size_label()

    def _update_size_label(self):
        fmt, qual = self.format_var.get(), self.quality_var.get()
        qual_key = "audio" if "audio" in fmt or "mp3" in fmt else qual
        size_bytes = self.format_quality_sizes.get((fmt, qual_key), 0)
        self.size.config(text=f"{size_bytes/1024/1024:.2f} MB" if size_bytes > 0 else "unknown")

    def download_widgets(self):
        img = Image.open(DEFAULT_THUMB) if DEFAULT_THUMB.exists() else Image.new("RGB", (160, 100), color=(200,200,200))
        img = ImageTk.PhotoImage(img.resize((160, 100)))
        
        self.video_info = tk.Frame(self.main_frame, borderwidth=2, relief="solid",bg="#fffd00")
        _grid(self.video_info, 3, 1, sticky="nsew", pady=10, padx=10,columnspan=2)
        
        self.thumb = _label(self.video_info, "", image=img,relief="solid"); self.thumb.img = img
        _grid(self.thumb, 1, 1, rowspan=4, padx=10, pady=10)
        
        self.video_title = _label(self.video_info, "Title", font=("helvitica", 13, "bold"),bg="#fffb00", anchor="nw", wraplength=300, justify="left")
        _grid(self.video_title, 1, 2, sticky="nw", padx=5, pady=10)
        
        self.video_channel = _label(self.video_info, "Channel: Unknown", font=("helvitica", 10),bg="#fffb00", anchor="nw", fg="gray")
        _grid(self.video_channel, 2, 2, sticky="nw", padx=5)
        
        self.video_duration = _label(self.video_info, "Duration: 0:00", font=("helvitica", 10),bg="#fffb00", anchor="nw", fg="gray")
        _grid(self.video_duration, 3, 2, sticky="nw", padx=5)
        
        self.download_frame = tk.Frame(self.main_frame, borderwidth=2, relief="solid",bg="#fffb00")
        _grid(self.download_frame, 4, 1, sticky="ew",columnspan=2,padx=10,pady=10)
        
        fmt_var = tk.StringVar(value="mp4(video)")
        _grid(_label(self.download_frame, "format:"), 1, 1, padx=20)
        fmt_combo = ttk.Combobox(self.download_frame, textvariable=fmt_var, values=["mp3(audio)","mp4(video)","webm(video)"], width=12, state="readonly")
        _grid(fmt_combo, 2, 1, sticky="ew", pady=10,padx=20)
        fmt_var.trace_add("write", self._on_format_changed)
        self.format_var = fmt_var
        
        qual_var = tk.StringVar(value="1080p")
        _grid(_label(self.download_frame, "Quality"), 1, 2,padx=10)
        self.quality_menu = ttk.Combobox(self.download_frame, textvariable=qual_var, values=["144p","240p","420p","720p","1080p"], width=10, state="readonly")
        _grid(self.quality_menu, 2, 2,padx=20,sticky="ew",pady=10)
        qual_var.trace_add("write", lambda *a: self._update_size_label())
        self.quality_var = qual_var
        
        _grid(_label(self.download_frame, "File size:"), 1, 3, pady=10,padx=10)
        self.size = _label(self.download_frame, "unknown", bg="white", borderwidth=1, relief="solid", width=10)
        _grid(self.size, 2, 3, pady=10,padx=10,sticky="ew")

        self.browse_buttons_frame = tk.Frame(self.download_frame,bg="#fffb00")
        _grid(self.browse_buttons_frame,3,1,pady=10,padx=10,columnspan=2,sticky="ew")
        self.browse_buttons_frame.columnconfigure(1,weight=1)

        self.browse_label = tk.Label(self.browse_buttons_frame, text=self.output_path, bg="white", anchor="w",relief="sunken",width=30)
        _grid(self.browse_label,3,1,sticky="ew",pady=10)
        _grid(tk.Button(self.browse_buttons_frame, text="browse",command=self.browse_dir,relief="sunken",bd=2,width=12), 3, 2, pady=10, sticky="ew")

        _grid(tk.Button(self.download_frame, text="download", command=self.start_download,cursor="bottom_side",bg="#ff0000",fg="white",relief="solid"), 3, 3, pady=10, padx=10, sticky="ew")

        self.status_bar = ttk.Progressbar(self.download_frame, value=0, maximum=100)
        _grid(self.status_bar, 4, 1, columnspan=3, sticky="ew", pady=10, padx=10)
        
        self.status_label = _label(self.download_frame, "0%", anchor="center")
        _grid(self.status_label, 5, 1, columnspan=3,pady=10)
        
        for i in (1,2,3): self.download_frame.grid_columnconfigure(i, weight=1)
        
        _label(self.root, "Don't use copyrighted content without permission.", font=("arial", 8),bg="#55ff55").pack(side="bottom", anchor="s")
        self.format_quality_sizes = {}

    def browse_dir(self):
        new_path = filedialog.askdirectory(initialdir=self.output_path)
        if not new_path: return
        self.output_path = new_path
        self.browse_label.config(text=new_path)

    def _progress_hook(self, d):
        def _upd():
            s = d.get("status")
            if s == "downloading":
                tb, db = d.get("total_bytes") or d.get("total_bytes_estimate") or d.get("filesize"), d.get("downloaded_bytes")
                if tb and db:
                    pct = int(db/tb*100)
                    self.status_bar['value'] = pct
                    self.status_label.config(text=f"{pct}% ({db/1024/1024:.1f}MB / {tb/1024/1024:.1f}MB)")
                    self.root.update_idletasks()
            elif s == "finished":
                self.status_bar['value'] = 100
                self.status_label.config(text="100% - Complete!")
        try: self.root.after(0, _upd)
        except: pass

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url: messagebox.showwarning("URL required", "Enter URL"); return
        
        self.status_bar['value'] = 0
        self.status_label.config(text="Starting...")
        self.root.update_idletasks()
        
        def _work():
            try:
                self.root.after(0, lambda: self.status_label.config(text="Downloading..."))
                backend_core.download(url, self.format_var.get(), self.quality_var.get(), self.output_path, progress_hook=self._progress_hook)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Download finished!"))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text="Failed"))
                self.root.after(0, lambda: messagebox.showerror("Failed", str(e)))
        threading.Thread(target=_work, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
