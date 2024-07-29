import os
import time
from gtts import gTTS
from playsound import playsound, PlaysoundException

def speak(audio, lang='en'):
    tts = gTTS(text=audio, lang=lang)
    filename = "speech.mp3"
    tts.save(filename)

    for _ in range(3):
        try:
            playsound(filename)
            break
        except PlaysoundException as e:
            print(f"Error playing sound: {e}")
            time.sleep(1)

    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            print(f"Error removing file: {e}")
