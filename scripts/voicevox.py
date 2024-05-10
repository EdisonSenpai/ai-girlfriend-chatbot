import os
import subprocess
import atexit
import json
import threading

from colorama import *
import scripts.voicevoxDependencies

# Run voicevox
process = None

@atexit.register
def kill_process():
    global process
    print(Fore.RED + "voicevox terminating" + Fore.RESET, flush=True)
    try:
        process.terminate()
        
    except:
        pass

def handle_output(stream, suffix):
    while True:
        line = stream.readline()
        if not line:
            break
        print(Style.DIM + f"voicevox: {line.decode().rstrip()}" + Style.RESET_ALL)

def start():
    global process

    process = subprocess.Popen(
        scripts.voicevoxDependencies.VOICEVOX_DIR + "/run.exe",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if json.loads(os.environ.get("VOICEVOX_LOG",  "False").lower()):
        tasks = [
            threading.Thread(target=handle_output, args=(process.stdout, "stdout")),
            threading.Thread(target=handle_output, args=(process.stderr, "stderr")),
        ]

        for task in tasks:
            task.start()

        for task in tasks:
            task.join()

    # return process.wait()

EVENT_LOOPS = {}

def run_in_new_thread(function, *args, **kwargs):
    t = threading.Thread(target=function, args=args, kwargs=kwargs)
    t.start()

def run_async():
    run_in_new_thread(start)

    # return await process.wait()
