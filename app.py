import sys
import json
import wave
import winsound
import pyaudio
import openai
import time
import keyboard

from scripts.translate import *
from scripts.tts import *
from scripts.subtitles import *
from scripts.prompter import *
from scripts.voicevoxDependencies import *

# Cod folosit pentru a scrie caractere unicode in terminal
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

# Se deschide fisierul .env si se face load la setarile din el
with open('.env') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split('=', 1)
        os.environ[key] = value

# Setam API-ul pentru OpenAI
if os.environ.get("OPENAI_KEY") is None:
    print(Fore.RED + Style.BRIGHT + "You didn't provide an OpenAI API Key!" + Style.RESET_ALL + " Things will not work.")
else:
    openai.api_key = os.environ.get("OPENAI_KEY")

# openai.api_key =

dialogue = []

messageHistory = {"history": dialogue}

tCharacters = 0
mode = 0
chat = ""
chatPrev = ""
chatNow = ""
isSpeaking = False
master = "Edison Senpai"
voice = "voicevox"

# Functie pentru a prelua input-ul audo de la user
def audioRecord():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_INPUT_FILENAME = "input.wav"
    CHUNK = 1024

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []

    print("Your mic is now recording...")

    while keyboard.is_pressed('LEFT_ALT'):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording is stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_INPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    audioTranscr("input.wav")

# Functie pentru a transcrie input-ul audio
def audioTranscr(input):
    global chatNow

    try:
        audioFile = open(input, 'rb')

        # Traducere audio in limba detectata
        transcript = openai.Audio.transcribe("whisper-1", audioFile) 
        chatNow = transcript.text

        print("Question: " + chatNow)
    except Exception as e:
        print("Error when trancribing audio file: {0}".format(e))
        return
    
    result = master + " said " + chatNow
    dialogue.append({'role': 'user', 'content': result})
    openaiAnswer()

# Functie pentru a primi raspuns de la OpenAI
def openaiAnswer():
    global tCharacters
    global dialogue

    tCharacters = sum(len(d['content']) for d in dialogue)

    while tCharacters > 4096:
        try:
            dialogue.pop(2)
            tCharacters = sum(len(d['content']) for d in dialogue)
        except Exception as e:
            print("Error when trying to remove old messages: {0}".format(e))

    with open("dialogue.json", "w", encoding="utf-8") as file:
        json.dump(messageHistory, file, indent=4) # Aici se scrie mesajul in format JSON

    prompt = getPrompt()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=128,
        temperature=1,
        top_p=0.9
    )

    message = response['choices'][0]['message']['content']
    dialogue.append({'role': 'assistant', 'content': message})

    textTranslate(message)

# Functie pentru a traduce textul, il parseaza intr-un TTS si genereaza subtitrare pentru OBS
def textTranslate(text):
    global isSpeaking

    detect = googleDetect(text)
    tts = googleTranslate(text, f"{detect}", "JA")
    ttsEN = googleTranslate(text, f"{detect}", "EN")

    try:
        print("JP: " +  tts)
        print("EN: " + ttsEN)
    except Exception as e:
        print("Error when printing text: {0}".format(e))
        return
    
    # Se pot folosi 2 tipuri de engine in aceasta aplicatie, Silero TTS si VoiceVox TTS.
    # Voi folosi Silero TTS sau VoiceVox TTS pentru a genera text in Engleza ca si subtitrare.
    # Pentru a folosi VoiceVox TTS, se urmeaza pasii descrisi in utils/tts.py la functia voicevoxTTS()

    voicevoxTTS(tts)
    # sileroTTS(ttsEN, "en", "v3_en", "en_21")

    generateSubtitle(chatNow, text)

    time.sleep(1)

    isSpeaking = True
    winsound.PlaySound("output.wav", winsound.SND_FILENAME)
    isSpeaking = False

    time.sleep(1)

    # Dupa ce a terminat de vorbit, sterg fisierele text create
    with open("output.txt", "w") as file:
        file.truncate(0)
    with open("chat.txt", "w") as file:
        file.truncate(0)

def printIntroScreen():
  """Prints an introduction screen with a Hatsune Miku Chibi art and a short program description."""
  print(r"""
                 
         ╔════════════════════════════════════════════════════════════════════════════════╗
         ║                                                                                ║
         ║                                  AI Girlfriend                                 ║
         ║                                 ~ version: 1.0 ~                               ║
         ║                                                                                ║
         ║                                                                                ║
         ║                                                                                ║
         ║                                                                                ║
         ║                  ⣀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                   ║   
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⠶⠚⠉⢉⣩⠽⠟⠛⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀       ║     
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠉⠀⢀⣠⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        ║
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠁⠀⠀⣰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀       ║
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⡤⠤⠄⢤⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀     ║ 
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠴⠒⠋⠉⠀⠀⠀⣀⣤⠴⠒⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀     ║
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⡄⠀⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⢳⡄⢀⡴⠚⠉⠀⠀⠀⠀⠀⣠⠴⠚⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀     ║
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⡀⠘⣧⠀⠀⠀⠀⠀⠀⠀⠀⣰⠃⠀⠀⠹⡏⠀⠀⠀⠀⠀⣀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀     ║
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠳⢬⣳⣄⣠⠤⠤⠶⠶⠒⠋⠀⠀⠀⠀⠹⡀⠀⠀⠀⠀⠈⠉⠛⠲⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ║ 
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠤⠖⠋⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢳⠦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀     ║
         ║       ⠀⠀⠀⠀⠀⠀⠀⠀⣠⠖⠋⠀⠀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⢃⠈⠙⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀     ║
         ║       ⠀⠀⠀⠀⠀⠀⢠⠞⠁⠀⠀⠀⢀⢾⠃⠀⠀⠀⠀⠀⠀⠀⠀⢢⠀⠀⠀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠮⣄⠀⠀⠀⠙⢦⡀⠀⠀⠀⠀⠀     ║
         ║       ⠀⠀⠀⠀⠀⣰⠋⠀⠀⢀⡤⡴⠃⠈⠦⣀⠀⠀⠀⠀⠀⠀⢀⣷⢸⠀⠀⠀⠀⢀⣀⠘⡄⠤⠤⢤⠔⠒⠂⠉⠁⠀⠀⠀⠑⢄⡀⠀⠀⠙⢦⡀⠀⠀⠀  ║
         ║       ⠀⠀⠀⠀⣼⠃⠀⠀⢠⣞⠟⠀⠀⠀⡄⠀⠉⠒⠢⣤⣤⠄⣼⢻⠸⠀⠀⠀⠀⠉⢤⠀⢿⡖⠒⠊⢦⠤⠤⣀⣀⡀⠀⠀⠀⠈⠻⡝⠲⢤⣀⠙⢦⠀⠀ ║
         ║       ⠀⠀⠀⢰⠃⠀⠀⣴⣿⠎⠀⠀⢀⣜⠤⠄⢲⠎⠉⠀⠀⡼⠸⠘⡄⡇⠀⠀⠀⠀⢸⠀⢸⠘⢆⠀⠘⡄⠀⠀⠀⢢⠉⠉⠀⠒⠒⠽⡄⠀⠈⠙⠮⣷⡀ ║
         ║       ⠀⠀⠀⡟⠀⠀⣼⢻⠧⠐⠂⠉⡜⠀⠀⡰⡟⠀⠀⠀⡰⠁⡇⠀⡇⡇⠀⠀⠀⠀⢺⠇⠀⣆⡨⢆⠀⢽⠀⠀⠀⠈⡷⡄⠀⠀⠀⠀⠹⡄⠀⠀⠀⠈⠁   ║ 
         ║       ⠀⠀⢸⠃⠀⠀⢃⠎⠀⠀⠀⣴⠃⠀⡜⠹⠁⠀⠀⡰⠁⢠⠁⠀⢸⢸⠀⠀⠀⢠⡸⢣⠔⡏⠀⠈⢆⠀⣇⠀⠀⠀⢸⠘⢆⠀⠀⠀⠀⢳⠀⠀⠀⠀⠀   ║
         ║       ⠀⠀⢸⠀⠀⠀⡜⠀⠀⢀⡜⡞⠀⡜⠈⠏⠀⠈⡹⠑⠒⠼⡀⠀⠀⢿⠀⠀⠀⢀⡇⠀⢇⢁⠀⠀⠈⢆⢰⠀⠀⠀⠈⡄⠈⢢⠀⠀⠀⠈⣇⠀⠀⠀⠀  ║
         ║       ⠀⠀⢸⡀⠀⢰⠁⠀⢀⢮⠀⠇⡜⠀⠘⠀⠀⢰⠃⠀⠀⡇⠈⠁⠀⢘⡄⠀⠀⢸⠀⠀⣘⣼⠤⠤⠤⣈⡞⡀⠀⠀⠀⡇⠰⡄⢣⡀⠀⠀⢻⠀⠀⠀⠀  ║
         ║       ⠀⠀⠈⡇⠀⡜⠀⢀⠎⢸⢸⢰⠁⠀⠄⠀⢠⠃⠀⠀⢸⠀⠀⠀⠀⠀⡇⠀⠀⡆⠀⠀⣶⣿⡿⠿⡛⢻⡟⡇⠀⠀⠀⡇⠀⣿⣆⢡⠀⠀⢸⡇⠀⠀⠀  ║
         ║       ⠀⠀⢠⡏⠀⠉⢢⡎⠀⡇⣿⠊⠀⠀⠀⢠⡏⠀⠀⠀⠎⠀⠀⠀⠀⠀⡇⠀⡸⠀⠀⠀⡇⠀⢰⡆⡇⢸⢠⢹⠀⠀⠀⡇⠀⢹⠈⢧⣣⠀⠘⡇⠀⠀⠀  ║ 
         ║       ⠀⠀⢸⡇⠀⠀⠀⡇⠀⡇⢹⠀⠀⠀⢀⡾⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢠⠃⠀⠀⠠⠟⡯⣻⣇⢃⠇⢠⠏⡇⠀⢸⡆⠀⢸⠀⠈⢳⡀⠀⡇⠀⠀⠀  ║
         ║       ⠀⠀⠀⣇⠀⡔⠋⡇⠀⢱⢼⠀⠀⡂⣼⡇⢹⣶⣶⣶⣤⣤⣀⠀⠀⠀⣇⠇⠀⠀⠀⠀⣶⡭⢃⣏⡘⠀⡎⠀⠇⠀⡾⣷⠀⣼⠀⠀⠀⢻⡄⡇⠀⠀⠀  ║
         ║       ⠀⠀⠀⣹⠜⠋⠉⠓⢄⡏⢸⠀⠀⢳⡏⢸⠹⢀⣉⢭⣻⡽⠿⠛⠓⠀⠋⠀⠀⠀⠀⠀⠘⠛⠛⠓⠀⡄⡇⠀⢸⢰⡇⢸⡄⡟⠀⠀⠀⠀⢳⡇⠀⠀⠀ ║
         ║       ⠀⣠⠞⠁⠀⠀⠀⠀⠀⢙⠌⡇⠀⣿⠁⠀⡇⡗⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠀⠀⠀⠀⠀⠀⠁⠁⠀⢸⣼⠀⠈⣇⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀    ║
         ║       ⢸⠁⠀⠀⢀⡠⠔⠚⠉⠉⢱⣇⢸⢧⠀⠀⠸⣱⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡤⠦⡔⠀⠀⠀⠀⠀⢀⡼⠀⠀⣼⡏⠀⠀⢹⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀   ║
         ║       ⢸⠀⠀⠀⠋⠀⠀⠀⢀⡠⠤⣿⣾⣇⣧⠀⠀⢫⡆⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⣠⠇⠀⠀⢀⡠⣶⠋⠀⠀⡸⣾⠁⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀   ║
         ║       ⢸⡄⠀⠀⠀⠀⠠⠊⠁⠀⠀⢸⢃⠘⡜⡵⡀⠈⢿⡱⢲⡤⠤⢀⣀⣀⡀⠉⠉⣀⡠⡴⠚⠉⣸⢸⠀⠀⢠⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ║
         ║       ⠀⢧⠀⠀⠀⠀⠀⠀⠀⣀⠤⠚⠚⣤⣵⡰⡑⡄⠀⢣⡈⠳⡀⠀⠀⠀⢨⡋⠙⣆⢸⠀⠀⣰⢻⡎⠀⠀⡎⡇⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ║
         ║       ⠀⠈⢷⡀⠀⠀⠀⠀⠀⠁⠀⠀⠀⡸⢌⣳⣵⡈⢦⡀⠳⡀⠈⢦⡀⠀⠘⠏⠲⣌⠙⢒⠴⡧⣸⡇⠀⡸⢸⠇⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ║
         ║       ⠀⠀⢠⣿⠢⡀⠀⠀⠀⠠⠄⡖⠋⠀⠀⠙⢿⣳⡀⠑⢄⠹⣄⡀⠙⢄⡠⠤⠒⠚⡖⡇⠀⠘⣽⡇⢠⠃⢸⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ║
         ║       ⠀⠀⣾⠃⠀⠀⠀⠀⠀⢀⡼⣄⠀⠀⠀⠀⠀⠑⣽⣆⠀⠑⢝⡍⠒⠬⢧⣀⡠⠊⠀⠸⡀⠀⢹⡇⡎⠀⡿⢸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ║
         ║       ⠀⡼⠁⠀⠀⠀⠀⠀⠀⢀⠻⣺⣧⠀⠀⠀⠰⢢⠈⢪⡷⡀⠀⠙⡄⠀⠀⠱⡄⠀⠀⠀⢧⠀⢸⡻⠀⢠⡇⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ║
         ║       ⢰⠇⠀⠀⠀⠀⠀⠀⠀⢸⠀⡏⣿⠀⠀⠀⠀⢣⢇⠀⠑⣄⠀⠀⠸⡄⠀⠀⠘⡄⠀⠀⠸⡀⢸⠁⠀⡾⢰⡏⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ║
         ║       ⢸⠀⠀⠀⠀⠀⠀⠀⠀⠈⡄⡇⡇⢸⠀⠀⠀⠈⡇⠀⠀⠈⢦⡀⠀⠈⢦⡀⠀⠀⠙⢄⡠⠚⠋⠀⠀⡇⢸⡇⠈⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀     ║
         ║                                                                                 ║
         ║       ~ Welcome to your AI Girlfriend Program!^^                                ║   
         ║                                                                                 ║ 
         ║       This program simulates a virtual girlfriend experience,                   ║
         ║       allowing you to have engaging conversations through text or voice input^^ ║
         ║                                                                                 ║
         ║      ╔                                                    ╗                     ║
         ║      ║ Created by: Eduard Donea (333AA) aka エディソン先輩 ║                     ║
         ║      ╚                                                    ╝                     ║ 
         ╚═════════════════════════════════════════════════════════════════════════════════╝
  """)

if __name__ == "__main__":
    try:
        printIntroScreen()
        
        print("WARNING! If you want to use VoiceVox TTS, uncomment the line 140 from \"textTranslate\" function and please start the VoiceVox through Docker using this command line (after you used the pull comand described in \"tts.py\": docker pull voicevox/voicevox_engine:nvidia-ubuntu20.04-latest [for GPU] or docker pull voicevox/voicevox_engine:cpu-ubuntu20.04-latest [for CPU]]):\n ~Using GPU: docker run --rm --gpus all -p 50021:50021 voicevox/voicevox_engine:nvidia-ubuntu20.04-latest\n ~Using CPU: docker run --rm -it -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest")
        mode = input("Enter mode (1 - Mic (STS), 2 - Text (TTS))): ")
        
        # Se comenteaza liniile 184-188 daca nu se foloseste VoiceVox local
        # start_check(voice)

        # if voice == "voicevox":
        #    import scripts.voicevox
        #    scripts.voicevox.run_async()

        if mode == "1":
            print("You are now in microphone input mode.\n")
            print("Press and hold LALT or RALT to record audio.")

            while True:
                if keyboard.is_pressed('LEFT_ALT'):
                    audioRecord()

        elif mode == "2":
            print("You are now in text input mode.\n")
            print("Type your question or message, and press Enter to send.")
            
            while True:
                chat = input("You: ")
                dialogue.append({'role': 'user', 'content': chat})
                chatNow = chat
                openaiAnswer()
    except KeyboardInterrupt:
        print("Stopped by user.")
