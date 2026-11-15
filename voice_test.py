
import pyttsx3

engine = pyttsx3.init('sapi5')

engine.setProperty('rate', 165)
engine.setProperty('volume', 1.0)

message = (
    "Hello! I am NEXUS. "
    "My artificial intelligence system is ready. "
    "I can speak multiple sentences. "
    "Welcome to my world!"
)

engine.say(message)
engine.runAndWait()

print("VOICE TEST COMPLETED!")
