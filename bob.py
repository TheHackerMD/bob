#!/usr/bin/env python3
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# === CONFIGURATION ===
GEMINI_API_KEY = "AIzaSyCRYztGYvcQ9rcW3xeW3JlzwjmzMl7VSR8"
SPOTIPY_CLIENT_ID = "c5c631cd48044f01bee3187796c4d668"
SPOTIPY_CLIENT_SECRET = "1d2916c4b36140028181abb6a0610bbb"
SPOTIPY_REDIRECT_URI = "https://localhost:8888/callback"

# === INIT GEMINI ===
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-pro")

# === INIT TTS ===
engine = pyttsx3.init()

def speak(text):
    print("BOB:", text)
    engine.say(text)
    engine.runAndWait()

# === INIT STT ===
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You:", command)
            return command.lower()
        except sr.UnknownValueError:
            print("😕 Didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Sorry, speech service is down.")
            return ""

# === INIT SPOTIFY ===
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state,app-remote-control,streaming"))

def control_spotify(command):
    if "play" in command:
        query = command.replace("play", "").strip()
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.start_playback(uris=[track_uri])
            speak(f"Playing {query}")
        else:
            speak("I couldn't find that song.")
    elif "pause" in command:
        sp.pause_playback()
        speak("Paused.")
    elif "resume" in command or "continue" in command:
        sp.start_playback()
        speak("Resuming.")
    elif "next" in command:
        sp.next_track()
        speak("Skipping to next.")
    elif "previous" in command:
        sp.previous_track()
        speak("Going back.")
    else:
        speak("I didn't understand the Spotify command.")

# === MAIN LOOP ===
speak("Hey! I'm BOB and I'm online.")

while True:
    user_input = listen()

    if not user_input:
        continue

    if "shutdown" in user_input or "goodbye" in user_input:
        speak("Goodbye friend!")
        break

    elif "spotify" in user_input:
        control_spotify(user_input)

    else:
        response = gemini.generate_content(user_input).text.strip()
        speak(response)
