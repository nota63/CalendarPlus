import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Record from microphone
with sr.Microphone() as source:
    print("Say something!")
    audio = recognizer.listen(source)

try:
    # Use Google's free Web Speech API for transcription (online)
    text = recognizer.recognize_google(audio)
    print(f"You said: {text}")

except sr.UnknownValueError:
    print("Sorry, I could not understand your speech")
except sr.RequestError:
    print("Could not request results from Google Speech Recognition service")
