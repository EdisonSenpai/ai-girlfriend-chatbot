import os
import humanize
import requests
import py7zr

from colorama import *

VOICEVOX_DIR = "voicevox"

NODE = "node"

TEMP_FILE = "voicevox.tmp"

VOICEVOX_DIRECT_LINK = "https://github.com/VOICEVOX/voicevox_engine/releases/download/0.14.4/voicevox_engine-windows-nvidia-0.14.4.7z.001"

HARDCODED_VOICEVOX_ARCHIVE_ROOT_FOLDER = "windows-nvidia"

def download(url, temp):
    response = requests.get(url, stream=True)

    total_size = int(response.headers.get('content-length', 0))

    block_size = 1024 * 8
    print(Fore.BLUE + "(" + humanize.naturalsize(total_size) + ") ", end="")
    if os.path.exists(temp) and os.path.getsize(temp) == total_size:
        print("Already exists!")
    else:
        print()
        with open(temp, 'wb') as file:
            downloaded = 0
            for data in response.iter_content(block_size):
                file.write(data)
                downloaded += len(data)
                percent = downloaded * 100 / total_size
                print(Fore.RESET + f"Downloaded {Fore.BLUE}{humanize.naturalsize(downloaded)}/{humanize.naturalsize(total_size)}{Fore.YELLOW} ({percent:.2f}%){Fore.RESET}   ", end='\r')
    
    print(Fore.YELLOW + "Unzipping..." + Fore.RESET, end="", flush=True)

# Checks if voicevox is installed, if not, download and extract it.
def start_check(voice):
    if not os.path.isdir(VOICEVOX_DIR) and voice == "voicevox":

        print(Fore.YELLOW + "Installing voicevox..." + Fore.RESET, end="", flush=True)

        download(VOICEVOX_DIRECT_LINK, TEMP_FILE)
            
        with py7zr.SevenZipFile(TEMP_FILE, 'r') as archive:
            archive.extractall(path="./")
            
        # Clean
        os.rename(HARDCODED_VOICEVOX_ARCHIVE_ROOT_FOLDER, VOICEVOX_DIR)
        os.remove(TEMP_FILE)
