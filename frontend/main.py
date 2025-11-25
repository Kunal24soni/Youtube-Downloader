import tkinter as tk
from tkinter import messagebox,ttk
from PIL import Image,ImageTk
from pathlib import Path

path = Path("Assets/icon.png")

class App:
    def __init__(self,root):     #initialize the window
        self.root = root
        self.root.title("FetchTube")
        #self.root.resizable(False,False)
        img = Image.open(path)
        icon = ImageTk.PhotoImage(img)
        self.root.iconphoto(True, icon)
        self.img = img
        self.create_widgets()
    
    def create_widgets(self):
        self.title = tk.Label(self.root,text="FetchTube",font=("roboto",40,"bold"),bg="#FF0000",fg="white",borderwidth=2,relief="solid")
        self.title.pack(fill="x")

        self.main_frame = tk.LabelFrame(self.root,text="main_frame",borderwidth=2,relief="solid")
        self.main_frame.pack(pady=10,padx=10)

        self.url_entry = tk.Entry(self.main_frame,font=("courier",12,"italic"),width=30,relief="flat",borderwidth=2)
        self.url_entry.grid(row=1,column=1,sticky="ew",pady=10)
        self.url_entry.insert(0,"https://www.youtube.com/watch?v=dQw4w9WgXcQl")

        self.url_entry.bind("<FocusIn>",lambda event:on_entry_click())
        self.url_entry.bind("<FocusOut>",lambda event:on_focus_click())

        self.clear_button = tk.Button(self.main_frame,text="X",command=lambda :clear(),width=3,height=1,relief="flat",bg="white",activebackground="white")
        self.clear_button.grid(row=1,column=2,sticky="ew")

        self.fetch_button = tk.Button(self.main_frame,text="Fetch downloads",command=lambda :fetch(),border=2,relief="solid",width=20)
        self.fetch_button.grid(row=2,column=1)

        def fetch():
            pass
        def clear():
            self.url_entry.delete(0,tk.END)

        def on_entry_click():
            if (self.url_entry.get()) == "enter a url":
                self.url_entry.delete(0,tk.END)
        def on_focus_click():
            if self.url_entry.get() == "":
                self.url_entry.insert(0,"enter a url")

        self.download_widgets()

    def download_widgets(self):
        img = Image.open(".thumbnail//thumb.jpg")
        resized_img = img.resize((160,100))
        thumb = ImageTk.PhotoImage(resized_img)

        self.video_info = tk.LabelFrame(self.main_frame,text="video_info")
        self.video_info.grid(row=3,column=1,sticky="nsew",pady=10,padx=10)

        self.thumb = tk.Label(self.video_info,text="thumbnail",image=thumb)
        self.thumb.img = thumb
        self.thumb.grid(row=1,column=1,rowspan=3)

        self.video_title = tk.Label(self.video_info,text="Anisible in 100 seconds \n Fireship",font=("helvitica",12,"bold"),anchor="nw")
        self.video_title.grid(row=1,column=2)
        self.download_frame = tk.LabelFrame(self.main_frame,text="download_frame")
        self.download_frame.grid(row=4,column=1,sticky="ew")

        format_label = tk.Label(self.download_frame,text="format:")
        format_label.grid(row=1,column=1,padx=20,sticky="ew")
        format_var = tk.StringVar(value="mp4")
        self.format_menu = ttk.Combobox(self.download_frame, textvariable=format_var,
                                        values=["mp3(audio)","mp4(video)","webm(video)"],
                                         width=6,state="readonly")
        self.format_menu.grid(row=2,column=1,sticky="ew",pady=10)
        self.format_var = format_var
        self.download_frame.grid_columnconfigure(1,weight=1)

        quality_label = tk.Label(self.download_frame,text="Quality")
        quality_label.grid(row=1,column=2)
        quality_var = tk.StringVar(value="1080p")
        self.quality_menu = ttk.Combobox(self.download_frame, textvariable=quality_var,
                                        values=["144p", "240p", "420p", "720p", "1080p"], width=10,state="readonly")
        self.quality_menu.grid(row=2,column=2)
        self.download_frame.grid_columnconfigure(2,weight=1)
        self.quality_var = quality_var

        self.size_label = tk.Label(self.download_frame,text="File size:",width=10)
        self.size_label.grid(row=1,column=3,pady=10)
        self.size = tk.Label(self.download_frame,width=10,text="50.00mb",bg="white",borderwidth=1,relief="solid",)
        self.size.grid(row=2,column=3,pady=10)
        self.download_frame.grid_columnconfigure(3,weight=1)

        self.browse_label = tk.Label(self.download_frame,text="D:\projects\FetchTube\.assets",bg="white",anchor="w")
        self.browse_label.grid(row=3,column=1,pady=10,sticky="ew")
        self.browse_button = tk.Button(self.download_frame,text="browse")
        self.browse_button.grid(row=3,column=2,pady=10,sticky="ew")

        self.download_button = tk.Button(self.download_frame,text="download",cursor="bottom_side")
        self.download_button.grid(row=3,column=3,pady=10,padx=10,sticky="ew")

        self.status_bar = ttk.Progressbar(self.download_frame,value=100)
        self.status_bar.grid(row=4,column=1,columnspan=3,sticky="ew",pady=10,padx=10)

        self.status_label = tk.Label(self.download_frame,text="100%",anchor="center",background=None)
        self.status_label.grid(row=5,column=1,columnspan=3)

        self.footer()

    def footer(self):
        self.footer = tk.Label(self.root,text="Dont't use copyrighted^© content without the the author's permission.\n We don't promote any type of plagralism")
        self.footer.pack(side="bottom", anchor="s")
if __name__=="__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop(0)