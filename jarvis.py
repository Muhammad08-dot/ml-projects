import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import os
import pyautogui
import psutil
import webbrowser
import threading
import customtkinter as ctk
from PIL import Image

# --- CONFIGURATION ---
genai.configure(api_key="AIzaSyA5hU7RFVyFrcfIjmuQ_K9qcuyXqmTbU2w")
model = genai.GenerativeModel('gemini-1.5-flash')

engine = pyttsx3.init()
engine.setProperty('rate', 180) # Thori tez voice

def speak(text, gui_label=None):
    if gui_label: gui_label.configure(text=f"JARVIS: {text}")
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# --- JARVIS ENGINE ---
class JarvisEngine:
    def __init__(self, gui):
        self.gui = gui
        self.is_running = True

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.gui.status_label.configure(text="LISTENING...", text_color="#00D2FF")
            audio = r.listen(source)
            try:
                query = r.recognize_google(audio)
                self.gui.update_command(query)
                return query.lower()
            except:
                return ""

    def run(self):
        speak("Systems initialized. Full access granted, Muhammad.", self.gui.status_label)
        while self.is_running:
            query = self.listen()
            if not query: continue

            # 1. SYSTEM CONTROLS
            if "open" in query:
                app = query.replace("open", "").strip()
                os.system(f"start {app}")
                speak(f"Opening {app}", self.gui.status_label)

            elif "close" in query:
                app = query.replace("close", "").strip()
                if "window" in app or "this" in app:
                    pyautogui.hotkey('alt', 'f4')
                else:
                    os.system(f"taskkill /f /im {app}.exe")
                speak(f"Closing {app}", self.gui.status_label)

            elif "volume up" in query:
                for _ in range(10): pyautogui.press("volumeup")
                speak("Volume increased", self.gui.status_label)

            elif "screenshot" in query:
                pyautogui.screenshot("jarvis_ss.png")
                speak("Screenshot saved", self.gui.status_label)

            elif "minimize" in query:
                pyautogui.hotkey('win', 'd')
                speak("Minimizing", self.gui.status_label)

            elif "stop" in query or "exit" in query:
                speak("Going offline, Sir.", self.gui.status_label)
                self.is_running = False
                os._exit(0)

            # 2. AI BRAIN
            else:
                try:
                    response = model.generate_content(query)
                    speak(response.text, self.gui.status_label)
                except:
                    speak("I am having trouble connecting to my servers.", self.gui.status_label)

# --- GUI INTERFACE ---
class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("J.A.R.V.I.S")
        self.geometry("500x600")
        self.configure(fg_color="#010B13")

        # UI Elements
        self.title_label = ctk.CTkLabel(self, text="J.A.R.V.I.S", font=("Orbitron", 35, "bold"), text_color="#00D2FF")
        self.title_label.pack(pady=30)

        # Core Animation Placeholder
        self.core = ctk.CTkButton(self, text="ARC REACTOR", width=220, height=220, corner_radius=110,
                                 fg_color="#001F2B", border_color="#00D2FF", border_width=4,
                                 font=("Consolas", 12), text_color="#00D2FF", hover=False)
        self.core.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="SYSTEM READY", font=("Consolas", 16), text_color="#00D2FF")
        self.status_label.pack(pady=10)

        self.last_cmd = ctk.CTkLabel(self, text="Command: None", font=("Consolas", 12), text_color="gray")
        self.last_cmd.pack(pady=20)

    def update_command(self, cmd):
        self.last_cmd.configure(text=f"Last Command: {cmd}")

# --- EXECUTION ---
if __name__ == "__main__":
    app = JarvisGUI()
    jarvis = JarvisEngine(app)
    
    # Jarvis logic ko background thread mein start karein
    thread = threading.Thread(target=jarvis.run, daemon=True)
    thread.start()
    
    app.mainloop()