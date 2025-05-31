# Surveillance Tool (Educational Project)

This is an **educational surveillance tool** built in Python that captures webcam footage, system information, clipboard contents, screenshots, and audio recordings. It simulates functionalities used in ethical hacking and red-team exercises.

> ⚠️ **Disclaimer:** This tool is created strictly for **educational purposes** and cybersecurity learning. Unauthorized use against individuals or systems without consent is illegal and unethical.

---

## 🔍 Features

- 🎥 **Webcam Capture**: Takes a snapshot using the system's webcam  
- 📋 **Clipboard Sniffer**: Extracts current clipboard contents  
- 💻 **System Info Extractor**: Gathers system and hardware details  
- 📸 **Screenshot Grabber**: Captures the current screen view  
- 🎤 **Audio Recorder**: Records microphone input (configurable duration)  
- 🗂️ **Data Export**: Stores gathered data in text and media files  
- 🕒 **Execution Delay**: Pauses before data collection begins (default 10 seconds)

---

## 🛠️ Technologies Used

- **Python 3**
- `cv2` (OpenCV)
- `pyautogui`
- `sounddevice`
- `scipy.io.wavfile`
- `platform`, `socket`, `uuid`, and more for system data
- `tkinter.filedialog` (optional, for GUI-based file saving)

---

## 🚀 How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/surveillance-tool.git
   cd surveillance-tool
   ```

2. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Tool**
   ```bash
   python main.py
   ```

> By default, the tool waits 10 seconds before capturing data. You can modify this in the `time.sleep()` call near the top of the script.

---

## 📁 Files Generated

The tool will generate the following files:

- `system_info.txt` – System hardware and network info  
- `clipboard.txt` – Clipboard contents  
- `screenshot.png` – A screenshot of the current desktop  
- `webcam.png` – Image from the webcam  
- `audio.wav` – Microphone audio recording

---

## 📂 Project Structure

```
📦surveillance-tool
 ┣ 📜main.py
 ┣ 📜README.md
 ┣ 📜requirements.txt
 ┣ 📂outputs
 ┃ ┣ 📜system_info.txt
 ┃ ┣ 📜clipboard.txt
 ┃ ┣ 📷screenshot.png
 ┃ ┣ 📷webcam.png
 ┃ ┗ 🔊audio.wav
```

---

## ⚠️ Ethical Considerations

This project is meant for:

- **Cybersecurity education**
- **Learning how malware and surveillance tools operate**
- **Understanding red-team techniques in ethical hacking**

**DO NOT** use this on anyone's device without clear, informed consent. Doing so is a violation of privacy laws and may lead to legal consequences.

---

## 🧠 Author

**Sohaib Ali Khan Sherwani**  
Student, BS Cybersecurity  
National University of Computer and Emerging Sciences (FAST)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE), but should only be used for legal and ethical learning.
