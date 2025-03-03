import speech_recognition as sr
import webbrowser
import pyttsx3
import wikipedia
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from openai import OpenAI

recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 150)  
engine.setProperty('volume', 1.0)  

client = OpenAI(
    api_key="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"  # Replace with your OpenAI API key
)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="72a92cefecaa4a11b52c5f26c611d70a",
    client_secret="2140e50832454737a3c465dac513c78c",
    redirect_uri="http://localhost:8888/callback",
    scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"
))

def speak(text):
    engine.say(text)
    engine.runAndWait()

def chat_with_ai(prompt):
    """Sends a prompt to OpenAI and returns the response."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Sorry, I encountered an error while processing your request."

def play_spotify_song(song_name):
    """Searches for a song on Spotify and plays it."""
    results = sp.search(q=song_name, limit=1)
    if results['tracks']['items']:
        song_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[song_uri])
        speak(f"Playing {song_name} on Spotify")
    else:
        speak("I couldn't find that song on Spotify.")

def spotify_control(command):
    """Handles Spotify playback control."""
    if "pause" in command:
        sp.pause_playback()
        speak("Paused Spotify playback")
    elif "resume" in command or "play" in command:
        sp.start_playback()
        speak("Resumed Spotify playback")
    elif "next" in command or "skip" in command:
        sp.next_track()
        speak("Skipped to the next song")
    elif "previous" in command or "back" in command:
        sp.previous_track()
        speak("Playing the previous song")
    
def set_spotify_volume(level):
    """Sets the volume of Spotify playback."""
    try:
        level = int(level)
        if 0 <= level <= 100:
            sp.volume(level)
            speak(f"Setting volume to {level} percent")
        else:
            speak("Please specify a volume level between 0 and 100.")
    except ValueError:
        speak("I couldn't understand the volume level. Please try again.")

def processCommand(c):
    c = c.lower()
    
    if "open google" in c:
        webbrowser.open("https://google.com")
        speak("Opening Google")

    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")

    elif "open instagram" in c:
        webbrowser.open("https://instagram.com")
        speak("Opening Instagram")

    elif "open amazon" in c:
        webbrowser.open("https://amazon.in")
        speak("Opening Amazon")

    elif "open flipkart" in c:
        webbrowser.open("https://flipkart.com")
        speak("Opening Flipkart")

    elif "wikipedia" in c:
        query = c.replace("wikipedia", "").strip()
        if query:
            try:
                summary = wikipedia.summary(query, sentences=2)
                speak(f"According to Wikipedia, {summary}")
            except wikipedia.exceptions.DisambiguationError:
                speak("There are multiple results for this search. Please be more specific.")
            except wikipedia.exceptions.PageError:
                speak("Sorry, I couldn't find any information on Wikipedia for that query.")
        else:
            speak("Please specify what you want to search on Wikipedia.")

    elif "sleep" in c:
        speak("Putting the computer to sleep")
        os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")

    elif "shutdown" in c:
        speak("Shutting down the computer")
        os.system("shutdown /s /t 5")

    elif "play" in c and "spotify" in c:
        song_name = c.replace("play", "").replace("on spotify", "").strip()
        if song_name:
            play_spotify_song(song_name)
        else:
            speak("Please specify a song name")

    elif "pause spotify" in c or "pause music" in c:
        spotify_control("pause")

    elif "resume spotify" in c or "play music" in c:
        spotify_control("play")

    elif "next song" in c or "skip song" in c:
        spotify_control("next")

    elif "previous song" in c or "back song" in c:
        spotify_control("previous")

    elif "volume" in c:
        if "increase" in c:
            current_volume = sp.current_playback()["device"]["volume_percent"]
            new_volume = min(current_volume + 10, 100)
            set_spotify_volume(new_volume)
        elif "decrease" in c:
            current_volume = sp.current_playback()["device"]["volume_percent"]
            new_volume = max(current_volume - 10, 0)
            set_spotify_volume(new_volume)
        else:
            level = ''.join(filter(str.isdigit, c))
            if level:
                set_spotify_volume(level)
            else:
                speak("Please specify a volume level.")

    elif "mute" in c:
        set_spotify_volume(0)

    elif "unmute" in c or "restore volume" in c:
        set_spotify_volume(50)

    # **Fix: Move this else to align with the if-elif chain**
    else:
        response = chat_with_ai(c)
        speak(response)

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            print("Recognizing...")
            word = recognizer.recognize_google(audio).lower()
            
            if word == "jarvis" or "hey jarvis" or "yo jarvis" or "oye jarvis" or "abey jarvis":
                speak("Yes?")
                with sr.Microphone() as source:
                    print("Jarvis Active...")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)
            else:
                print(f"You said: {word}")
                return word

        except sr.WaitTimeoutError:
            print("Listening timed out. Try again.")
            return ""
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand.")
            return ""
        except sr.RequestError:
            print("Network error.")
            return ""

if __name__ == "__main__":
    speak("Initializing Jarvis...")

    while True:
        user_command = listen()