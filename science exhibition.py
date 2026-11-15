# ==========================================
# N.E.X.U.S.
# NEURAL EXPLORATION AND UNDERSTANDING SYSTEM
# ==========================================

import os
import time
import random
import asyncio
import tempfile

import pygame
import edge_tts
import speech_recognition as sr

from dotenv import load_dotenv
from google import genai
from google.genai import types
from deep_translator import GoogleTranslator


# PART 1: GEMINI API SETUP

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = None

MODEL_NAME = "gemini-3.8-flash"

if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as error:
        print("Gemini setup error:", error)
else:
    print("Gemini API key not found!")


# PART 2: LANGUAGE SELECTION

print("\n================================")
print("             N.E.X.U.S.")
print("================================")

print("\nSelect your language:")
print("1. English")
print("2. Hindi")
print("3. Gujarati")

language = input("Enter choice: ").strip()

if language == "2":
    lang = "hi"
    language_name = "Hindi"
    voice_culture = "hi-IN"

elif language == "3":
    lang = "gu"
    language_name = "Gujarati"
    voice_culture = "gu-IN"

else:
    lang = "en"
    language_name = "English"
    voice_culture = "en-IN"


# PART 3: MALE NEURAL VOICES

voice_options = {
    "en": "en-IN-PrabhatNeural",
    "hi": "hi-IN-MadhurNeural",
    "gu": "gu-IN-NiranjanNeural"
}

selected_voice = voice_options[lang]


# PART 4: IMPROVED TRANSLATION SYSTEM

translation_cache = {}

last_translation_time = 0


def contains_selected_script(text):

    if lang == "gu":

        return any(
            "\u0A80" <= char <= "\u0AFF"
            for char in text
        )

    elif lang == "hi":

        return any(
            "\u0900" <= char <= "\u097F"
            for char in text
        )

    return True


def gemini_translate(text, target):

    if client is None:
        return None

    target_languages = {
        "gu": "Gujarati",
        "hi": "Hindi",
        "en": "English"
    }

    target_name = target_languages[target]

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=(
                "Translate the following text into "
                + target_name
                + ". Use the correct native script. "
                "Return ONLY the translated text. "
                "Do not explain anything.\n\n"
                + text
            ),

            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=0.2
            )
        )

        if response.text:
            return response.text.strip()

    except Exception as error:

        print("Gemini translation error:", error)

    return None


def translate_to(text, target):

    global last_translation_time

    if target == "en" and lang == "en":
        return text

    if target == lang and contains_selected_script(text):
        return text

    cache_key = (target, text)

    if cache_key in translation_cache:
        return translation_cache[cache_key]

    result = None

    try:

        # Wait before sending another request

        current_time = time.time()

        wait_time = 1.0 - (
            current_time - last_translation_time
        )

        if wait_time > 0:
            time.sleep(wait_time)

        # Update time even if the request fails

        last_translation_time = time.time()

        result = GoogleTranslator(
            source="auto",
            target=target
        ).translate(text)

        if not result:
            raise Exception("Empty translation result")

    except Exception as error:

        print("\nGoogle Translate temporarily unavailable.")

        print("Trying Gemini translation instead...")

        result = gemini_translate(text, target)

    # Save successful translations

    if result:

        translation_cache[cache_key] = result

        return result

    # Do not stop the complete program

    return text


def translate(text):

    if lang == "en":
        return text

    return translate_to(text, lang)


def answer_in_english(text):

    return translate_to(text, "en")


# PART 5: NEURAL TEXT-TO-SPEECH SYSTEM

async def generate_voice(text, filename):

    communicate = edge_tts.Communicate(
        text,
        selected_voice,
        rate="-5%",
        pitch="-5Hz"
    )

    await communicate.save(filename)


def play_voice(text):

    filename = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as temp:

            filename = temp.name

        asyncio.run(
            generate_voice(text, filename)
        )

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():

            pygame.time.Clock().tick(10)

    except Exception as error:

        print("NEXUS voice error:", error)

    finally:

        if filename:

            try:

                if pygame.mixer.get_init():

                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()

                if os.path.exists(filename):
                    os.remove(filename)

            except Exception:
                pass


def speak(text, translate_text=True):

    spoken_text = text

    if translate_text:

        spoken_text = translate(text)

    print("\nNEXUS:", spoken_text)

    play_voice(spoken_text)


# PART 6: DISPLAY SYSTEM

def show(text):

    displayed_text = translate(text)

    print(displayed_text)


# PART 7: GEMINI ANSWER SPEAKING

def speak_ai_answer(answer):

    if lang == "en":

        speak(answer, False)
        return

    if contains_selected_script(answer):

        speak(answer, False)

    else:

        speak(answer, True)


# PART 8: MICROPHONE SYSTEM

recognizer = sr.Recognizer()


def listen_to_user():

    try:

        with sr.Microphone() as source:

            show("\nNEXUS is listening...")
            show("Speak clearly!")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.7
            )

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=15
            )

        show("NEXUS is understanding your voice...")

        spoken_words = recognizer.recognize_google(
            audio,
            language=voice_culture
        )

        print("\nYou said:", spoken_words)

        return spoken_words

    except sr.WaitTimeoutError:

        show("No voice detected.")

    except sr.UnknownValueError:

        show("Sorry, I could not understand.")

    except sr.RequestError:

        show("Voice recognition internet error.")

    except Exception as error:

        print("Microphone error:", error)

    return ""


# PART 9: INPUT SYSTEM

def get_input(message):

    show(message)

    return input().strip()


# PART 10: CHOICE CONVERSION

def normal_choice(answer):

    answer = answer.lower().strip()

    numbers = {

        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",

        "एक": "1",
        "दो": "2",
        "तीन": "3",
        "चार": "4",

        "એક": "1",
        "બે": "2",
        "ત્રણ": "3",
        "ચાર": "4"

    }

    return numbers.get(answer, answer)


# PART 11: QUIZ QUESTION BANK

questions = {

    "General Knowledge": {

        "Easy": [
            {"q": "Which planet is called the Red Planet?",
             "a": "mars"},

            {"q": "What is the capital of Japan?",
             "a": "tokyo"},

            {"q": "How many days are in a week?",
             "a": "7"}
        ],

        "Medium": [
            {"q": "Which is the smallest continent?",
             "a": "australia"},

            {"q": "What is the currency of Japan?",
             "a": "yen"},

            {"q": "Who invented the telephone?",
             "a": "alexander graham bell"}
        ],

        "Hard": [
            {"q": "Which country has the largest population?",
             "a": "india"},

            {"q": "What is the chemical symbol for gold?",
             "a": "au"},

            {"q": "Which is the largest ocean?",
             "a": "pacific"}
        ]
    },

    "Maths": {

        "Easy": [
            {"q": "What is 12 multiplied by 5?", "a": "60"},
            {"q": "What is 100 divided by 4?", "a": "25"},
            {"q": "What is 15 plus 27?", "a": "42"}
        ],

        "Medium": [
            {"q": "What is the square root of 144?", "a": "12"},
            {"q": "What is 15 percent of 200?", "a": "30"},
            {"q": "What is 12 squared?", "a": "144"}
        ],

        "Hard": [
            {"q": "What is 7 factorial?", "a": "5040"},
            {"q": "What is the square root of 625?", "a": "25"},
            {"q": "What is 2 to the power of 10?", "a": "1024"}
        ]
    },

    "Science": {

        "Easy": [
            {"q": "Which gas do humans need to breathe?",
             "a": "oxygen"},

            {"q": "What is the centre of an atom called?",
             "a": "nucleus"},

            {"q": "Which organ pumps blood?",
             "a": "heart"}
        ],

        "Medium": [
            {"q": "What is the chemical formula of water?",
             "a": "h2o"},

            {"q": "Which planet is the largest?",
             "a": "jupiter"},

            {"q": "Which organelle produces energy in cells?",
             "a": "mitochondria"}
        ],

        "Hard": [
            {"q": "What is the atomic number of gold?",
             "a": "79"},

            {"q": "What is the formula of sulfuric acid?",
             "a": "h2so4"},

            {"q": "What is the SI unit of electric current?",
             "a": "ampere"}
        ]
    },

    "Computer": {

        "Easy": [
            {"q": "What does CPU stand for?",
             "a": "central processing unit"},

            {"q": "Which programming language is used in this project?",
             "a": "python"},

            {"q": "What does RAM stand for?",
             "a": "random access memory"}
        ],

        "Medium": [
            {"q": "Who created Python?",
             "a": "guido van rossum"},

            {"q": "What does HTML stand for?",
             "a": "hypertext markup language"},

            {"q": "What is the brain of a computer?",
             "a": "cpu"}
        ],

        "Hard": [
            {"q": "What does URL stand for?",
             "a": "uniform resource locator"},

            {"q": "What does SQL stand for?",
             "a": "structured query language"},

            {"q": "What is the binary form of decimal 5?",
             "a": "101"}
        ]
    },

    "Space": {

        "Easy": [
            {"q": "Which star is closest to Earth?",
             "a": "sun"},

            {"q": "How many planets are in our solar system?",
             "a": "8"},

            {"q": "Which planet do we live on?",
             "a": "earth"}
        ],

        "Medium": [
            {"q": "Which planet is famous for its rings?",
             "a": "saturn"},

            {"q": "What is the name of our galaxy?",
             "a": "milky way"},

            {"q": "Who was the first person on the Moon?",
             "a": "neil armstrong"}
        ],

        "Hard": [
            {"q": "What was the first artificial satellite?",
             "a": "sputnik 1"},

            {"q": "Which planet has the shortest day?",
             "a": "jupiter"},

            {"q": "What is the nearest large galaxy to the Milky Way?",
             "a": "andromeda"}
        ]
    },

    "Bollywood Movies": {

        "Easy": [
            {"q": "Which actor played Rancho in 3 Idiots?",
             "a": "aamir khan"},

            {"q": "Which actress starred opposite Shah Rukh Khan in DDLJ?",
             "a": "kajol"},

            {"q": "Which movie features Mogambo khush hua?",
             "a": "mr india"}
        ],

        "Medium": [
            {"q": "Who directed Lagaan?",
             "a": "ashutosh gowariker"},

            {"q": "Which movie features the phrase All is well?",
             "a": "3 idiots"},

            {"q": "Who played Bajirao in Bajirao Mastani?",
             "a": "ranveer singh"}
        ],

        "Hard": [
            {"q": "Who directed Piku?",
             "a": "shoojit sircar"},

            {"q": "Which actress played Geeta Phogat in Dangal?",
             "a": "fatima sana shaikh"},

            {"q": "Who directed Mughal-e-Azam?",
             "a": "k asif"}
        ]
    },

    "Bollywood Songs": {

        "Easy": [
            {"q": "Who sang Tum Hi Ho?",
             "a": "arijit singh"},

            {"q": "Chaiyya Chaiyya is from which movie?",
             "a": "dil se"},

            {"q": "Kesariya is from which movie?",
             "a": "brahmastra"}
        ],

        "Medium": [
            {"q": "Who composed Maa Tujhe Salaam?",
             "a": "a r rahman"},

            {"q": "Who sang the title song of Kal Ho Naa Ho?",
             "a": "sonu nigam"},

            {"q": "Who sang Tujh Mein Rab Dikhta Hai?",
             "a": "roop kumar rathod"}
        ],

        "Hard": [
            {"q": "Which two singers performed Agar Tum Saath Ho?",
             "a": "arijit singh and alka yagnik"},

            {"q": "Who composed Jai Ho?",
             "a": "a r rahman"},

            {"q": "Who sang Kabira with Rekha Bhardwaj?",
             "a": "tochi raina"}
        ]
    }

}


# PART 12: QUIZ ARENA

def quiz_battle():

    show("\n===== QUIZ ARENA =====")

    subjects = {

        "1": "General Knowledge",
        "2": "Maths",
        "3": "Science",
        "4": "Computer",
        "5": "Space",
        "6": "Bollywood Movies",
        "7": "Bollywood Songs"

    }

    for number, subject in subjects.items():

        show(number + ". " + subject)

    show("8. Mixed Subjects")

    choice = normal_choice(
        get_input("Choose your subject: ")
    )

    if choice not in subjects and choice != "8":

        speak("Invalid subject!")
        return

    show("\n===== SELECT DIFFICULTY =====")

    show("1. Easy")
    show("2. Medium")
    show("3. Hard")

    level = normal_choice(
        get_input("Choose difficulty: ")
    )

    levels = {

        "1": "Easy",
        "2": "Medium",
        "3": "Hard"

    }

    if level not in levels:

        speak("Invalid difficulty!")
        return

    difficulty = levels[level]

    if choice == "8":

        selected_questions = []

        for subject in questions:

            selected_questions += questions[subject][difficulty]

    else:

        selected_questions = questions[
            subjects[choice]
        ][difficulty][:]

    random.shuffle(selected_questions)

    human_score = 0
    nexus_score = 0

    speak("Quiz arena activated!")
    speak("Let the battle begin!")

    for i, question in enumerate(selected_questions, 1):

        show("\n===== ROUND " + str(i) + " =====")

        speak(question["q"])

        user_answer = get_input("Your answer: ")

        if user_answer == "":
            continue

        user_answer = answer_in_english(user_answer)

        if user_answer.strip().lower() == question["a"]:

            human_score += 1

            speak("Correct! Great job!")

        else:

            nexus_score += 1

            speak("Not quite! NEXUS gets one point.")

            speak(
                "The correct answer is " + question["a"]
            )

        show("Your score: " + str(human_score))
        show("NEXUS score: " + str(nexus_score))

    show("\n===== FINAL RESULTS =====")

    show("Your score: " + str(human_score))
    show("NEXUS score: " + str(nexus_score))

    if human_score > nexus_score:

        speak("Amazing! You defeated NEXUS!")

    elif human_score == nexus_score:

        speak("The battle ended in a tie!")

    else:

        speak("NEXUS wins this time!")


# PART 13: SMART AI CHATBOT

def smart_chat():

    if client is None:

        speak(
            "My artificial intelligence connection is unavailable."
        )

        return

    if lang == "gu":

        speak(
            "નમસ્તે! હું NEXUS છું. "
            "તમે મને કોઈપણ પ્રશ્ન પૂછી શકો છો.",
            False
        )

    elif lang == "hi":

        speak(
            "नमस्ते! मैं NEXUS हूँ। "
            "आप मुझसे कोई भी सवाल पूछ सकते हैं।",
            False
        )

    else:

        speak(
            "Hello! I am NEXUS. You can ask me anything.",
            False
        )

    show("Say BACK to return to the main menu.")

    chat_history = []

    while True:

        message = listen_to_user()

        if message == "":

            show("You can type your question instead.")

            message = input("Your question: ").strip()

            if message == "":
                continue

        exit_words = [

            "back",
            "go back",
            "exit",
            "quit",
            "પાછા જાઓ",
            "બહાર નીકળો",
            "वापस जाओ",
            "बाहर निकलो"

        ]

        if message.lower().strip() in exit_words:

            speak("Returning to the main menu.")
            break

        chat_history.append("User: " + message)

        prompt = "\n".join(chat_history[-8:])

        show("NEXUS is thinking...")

        for attempt in range(4):

            try:

                response = client.models.generate_content(

                    model=MODEL_NAME,

                    contents=prompt,

                    config=types.GenerateContentConfig(

                        system_instruction=(

                            "You are NEXUS, a friendly and intelligent "
                            "AI assistant. The selected language is "
                            + language_name
                            + ". Always answer completely in "
                            + language_name
                            + ". If Gujarati is selected, use natural "
                            "Gujarati language and Gujarati script. "
                            "Never write Gujarati using English letters. "
                            "Never answer in Hindi when Gujarati is "
                            "selected. If Hindi is selected, use natural "
                            "Devanagari script. If English is selected, "
                            "use English. Give clear and helpful answers."

                        ),

                        max_output_tokens=300,
                        temperature=0.7

                    )
                )

                answer = response.text

                if answer:

                    chat_history.append("NEXUS: " + answer)

                    speak_ai_answer(answer)

                else:

                    speak(
                        "Sorry, I could not generate an answer."
                    )

                break

            except Exception as error:

                error_text = str(error).upper()

                temporary_error = any(

                    code in error_text

                    for code in [

                        "503",
                        "UNAVAILABLE",
                        "429",
                        "RESOURCE_EXHAUSTED",
                        "500",
                        "502",
                        "504",
                        "INTERNAL"

                    ]
                )

                if temporary_error:

                    if attempt < 3:

                        wait_time = 2 ** (attempt + 1)

                        print(
                            "\nGemini is busy. Retrying in",
                            wait_time,
                            "seconds..."
                        )

                        time.sleep(wait_time)

                    else:

                        speak(
                            "Gemini is currently busy. "
                            "Please try again later."
                        )

                else:

                    print("\nAI connection error:", error)

                    speak(
                        "Sorry, my AI system is temporarily unavailable."
                    )

                    break


# PART 14: CAREER INTELLIGENCE

careers = {

    "1": [
        "Software Developer",
        "AI Engineer",
        "Robotics Engineer",
        "Cybersecurity Analyst"
    ],

    "2": [
        "Scientist",
        "Astronomer",
        "Researcher",
        "Aerospace Engineer"
    ],

    "3": [
        "Mathematician",
        "Data Analyst",
        "Accountant",
        "Financial Analyst"
    ],

    "4": [
        "Entrepreneur",
        "Business Manager",
        "Economist",
        "Marketing Manager"
    ],

    "5": [
        "Graphic Designer",
        "Animator",
        "Architect",
        "Filmmaker"
    ],

    "6": [
        "Professional Athlete",
        "Sports Coach",
        "Sports Analyst",
        "Sports Physiotherapist"
    ]

}


def career_advisor():

    show("\n===== CAREER INTELLIGENCE =====")

    show("1. Technology")
    show("2. Science and Space")
    show("3. Maths and Finance")
    show("4. Business")
    show("5. Creative Arts")
    show("6. Sports")

    choice = normal_choice(
        get_input("Choose your interest: ")
    )

    if choice in careers:

        speak(
            "Here are some careers based on your interest."
        )

        for career in careers[choice]:

            speak(career)

        speak(
            "Explore these careers and discover your future!"
        )

    else:

        speak("Invalid career choice!")


# PART 15: MAIN PROGRAM

try:

    # NEXUS INTRODUCTION

    if lang == "gu":

        speak(
            "નમસ્તે! હું NEXUS છું. "
            "મારું પૂરું નામ ન્યુરલ એક્સપ્લોરેશન "
            "એન્ડ અન્ડરસ્ટેન્ડિંગ સિસ્ટમ છે. "
            "મારી કૃત્રિમ બુદ્ધિ પ્રણાલી તૈયાર છે!",
            False
        )

    elif lang == "hi":

        speak(
            "नमस्ते! मैं NEXUS हूँ। "
            "मेरा पूरा नाम Neural Exploration "
            "and Understanding System है। "
            "मेरा आर्टिफिशियल इंटेलिजेंस सिस्टम तैयार है!",
            False
        )

    else:

        speak(
            "Welcome to NEXUS, your Neural Exploration "
            "and Understanding System! "
            "My artificial intelligence system is ready!",
            False
        )

    while True:

        show("\n================================")
        show("              N.E.X.U.S.")
        show("================================")

        show("1. Quiz Arena")
        show("2. Smart AI Chatbot")
        show("3. Career Intelligence")
        show("4. Exit")

        option = normal_choice(
            get_input("Choose an option: ")
        )

        if option == "1":

            quiz_battle()

        elif option == "2":

            smart_chat()

        elif option == "3":

            career_advisor()

        elif option == "4":

            if lang == "gu":

                speak(
                    "આભાર! NEXUS બંધ થઈ રહ્યું છે. આવજો!",
                    False
                )

            elif lang == "hi":

                speak(
                    "धन्यवाद! NEXUS बंद हो रहा है। अलविदा!",
                    False
                )

            else:

                speak(
                    "Thank you! NEXUS is shutting down. Goodbye!",
                    False
                )

            break

        else:

            speak("Invalid choice! Please try again!")


except KeyboardInterrupt:

    print("\nNEXUS has been stopped.")

finally:

    try:

        if pygame.mixer.get_init():
            pygame.mixer.quit()

    except Exception:
        pass

    print("\nNEXUS system closed.")