import tkinter as tk
from tkinter import filedialog
import threading  # threading 모듈을 import 해야 함
from analyzer import run_analysis  # analyzer.py에서 run_analysis 함수 불러오기

def select_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])

def start_program():
    if video_path:  # video_path가 None이 아니어야 함
        print("video_path:", video_path)  # 경로 출력
        threading.Thread(target=run_analysis, args=(video_path,)).start()
    else:
        print("video_path not exist")

app = tk.Tk()
app.title("exercise helper program")
app.geometry("400x200")

btn_select = tk.Button(app, text="video_upload", command=select_video, height=2, width=30)
btn_select.pack(pady=20)

btn_start = tk.Button(app, text="start", command=start_program, height=2, width=30)
btn_start.pack(pady=10)

app.mainloop()
