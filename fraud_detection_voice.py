import os
import time
from gtts import gTTS
import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import joblib
import numpy as np
import requests
from sklearn.preprocessing import StandardScaler
import re
from googletrans import Translator
import pygame

# Initialize pygame
pygame.mixer.init()

# Initialize the speech engine
engine = pyttsx3.init()

# Initialize the translator
translator = Translator()

# Define supported languages and their language codes
supported_languages = {
    'english': 'en',
    'hindi': 'hi',
    'tamil': 'ta',
    'telugu': 'te',
    'marathi': 'mr',
    'bengali': 'bn',
    'gujarati': 'gu',
    'kannada': 'kn',
    'malayalam': 'ml',
    'punjabi': 'pa'
}

# Set default language
user_language = 'english'

def speak(audio, lang='en'):
    tts = gTTS(text=audio, lang=lang)
    filename = "speech.mp3"
    tts.save(filename)
    
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.music.unload()  # Unload the music file
    time.sleep(1)  # Wait for 1 second to ensure the file is fully released
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Error removing file: {e}")

def get_time():
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak(f"The current time is {current_time}", supported_languages[user_language])

def get_date():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().strftime("%B")
    day = datetime.datetime.now().day
    speak(f"The date is {day} {month} {year}", supported_languages[user_language])

def wish_me():
    speak("Welcome back!", supported_languages[user_language])
    speak("The current time is", supported_languages[user_language])
    get_time()
    speak("The current date is", supported_languages[user_language])
    get_date()
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak("Good Morning!", supported_languages[user_language])
    elif 12 <= hour < 18:
        speak("Good Afternoon!", supported_languages[user_language])
    elif 18 <= hour < 24:
        speak("Good Evening!", supported_languages[user_language])
    else:
        speak("Good Night!", supported_languages[user_language])
    speak("How can I assist you with your UPI transactions today?", supported_languages[user_language])

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
    except Exception as e:
        print(e)
        speak("Say that again, please...", supported_languages[user_language])
        return "None"
    
    return query.lower()

# Load the trained fraud detection model and the scaler
model = joblib.load('fraud_detection_model.pkl')
scaler = joblib.load('scaler.pkl')

# Function to recognize speech and return the text
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please speak your UPI transaction details (you have 20 seconds):", supported_languages[user_language])
        print("Listening for transaction details...")
        audio = recognizer.listen(source, timeout=20, phrase_time_limit=20)
        try:
            text = recognizer.recognize_google(audio, language='en-in')
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            speak("Sorry, I could not understand the audio.", supported_languages[user_language])
        except sr.RequestError as e:
            speak(f"Could not request results from Google Speech Recognition service; {e}", supported_languages[user_language])
        except Exception as e:
            speak(f"An error occurred: {e}", supported_languages[user_language])
    return ""

# Function to preprocess the transaction details
def preprocess_transaction_details(details):
    # Extract features from the details
    amount = re.findall(r'\b\d+\b', details)
    upi_id = re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z]+\b', details)
    
    # Create a feature vector
    features = np.array([len(details), len(amount), len(upi_id)] + [0] * 7)  # Ensure 10 features
    
    # Standardize the features using the pre-fitted scaler
    features = scaler.transform(features.reshape(1, -1))
    return features

# Function to detect fraud
def detect_fraud(transaction_details):
    features = preprocess_transaction_details(transaction_details)
    prediction = model.predict(features)
    if prediction[0] == 1:
        speak("Warning: This UPI transaction is potentially fraudulent.", supported_languages[user_language])
    else:
        speak("This UPI transaction appears to be safe.", supported_languages[user_language])

# Function to provide personalized financial advice
def provide_financial_advice(query):
    if 'spending habit' in query:
        speak("Based on your recent transactions, I recommend cutting down on discretionary spending to save more.", supported_languages[user_language])
    elif 'investment' in query:
        speak("Considering the current market trends, it might be a good time to invest in mutual funds.", supported_languages[user_language])
    elif 'savings' in query:
        speak("I suggest setting up an automatic transfer to your savings account every month.", supported_languages[user_language])
    elif 'loan' in query:
        speak("You may want to consider refinancing your loan to take advantage of lower interest rates.", supported_languages[user_language])
    else:
        speak("I'm here to help with any financial advice you need. Just ask!", supported_languages[user_language])

# Function to fetch daily financial updates (stub)
def fetch_daily_updates():
    updates = "Today's market is bullish. Tech stocks are up by 5%. Stock ratings for major companies: Apple is rated A+, Google is rated A, and Amazon is rated A-."
    speak(updates, supported_languages[user_language])

# Function to summarize daily financial activity (stub)
def daily_summary():
    summary = "You spent ₹500 today via UPI. Your remaining balance is ₹4500."
    speak(summary, supported_languages[user_language])

# Function to initiate UPI transaction
def initiate_upi_transaction(details):
    url = "https://your-backend-server.com/api/initiate_upi_transaction"
    data = {"transaction_details": details}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                speak("The UPI transaction was successful.", supported_languages[user_language])
            else:
                speak("The UPI transaction failed. Please try again.", supported_languages[user_language])
        else:
            speak("Failed to connect to the UPI service. Please try again later.", supported_languages[user_language])
    except Exception as e:
        speak(f"An error occurred: {e}", supported_languages[user_language])

# Function to set user language
def set_language():
    global user_language
    speak("Please choose your preferred language: English, Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, or Punjabi.", 'en')
    language_query = take_command()
    for lang, code in supported_languages.items():
        if lang in language_query:
            user_language = lang
            speak(f"Language set to {lang}", supported_languages[lang])
            return
    speak("Sorry, I don't support that language yet. Setting language to English by default.", 'en')

# Main function to run the voice assistant
def main():
    set_language()
    speak("Language has been set successfully.", supported_languages[user_language])
    wish_me()
    fetch_daily_updates()
    daily_summary()
    
    while True:
        query = take_command()
        
        if 'time' in query:
            get_time()
        elif 'date' in query:
            get_date()
        elif 'thank you' in query or 'thanks' in query:
            speak("You're welcome!", supported_languages[user_language])
        elif 'wikipedia' in query:
            speak("Searching for you...", supported_languages[user_language])
            query = query.replace("wikipedia", "")
            result = wikipedia.summary(query, sentences=2)
            print(result)
            speak(result, supported_languages[user_language])
        elif 'search in chrome' in query:
            speak("What should I search?", supported_languages[user_language])
            search = take_command().lower()
            url = f"https://www.google.com/search?q={search}"
            wb.open_new_tab(url)
        elif 'transaction' in query:
            speak("Please speak your UPI transaction details.", supported_languages[user_language])
            transaction_details = recognize_speech()
            if transaction_details:
                detect_fraud(transaction_details)
                initiate_upi_transaction(transaction_details)
        elif 'financial advice' in query:
            provide_financial_advice(query)
        elif 'advice on my spending habits' in query:
            provide_financial_advice('spending habit')
        elif 'what should I invest in' in query:
            provide_financial_advice('investment')
        elif 'stock market update' in query or 'market updates' in query:
            fetch_daily_updates()
        elif 'set language' in query:
            set_language()
        elif 'exit' in query or 'bye' in query:
            speak("Goodbye!", supported_languages[user_language])
            break

if __name__ == "__main__":
    main()
