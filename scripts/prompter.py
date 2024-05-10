import sys
import json

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

outputNumber = 30

def getIdentity(path):
    with open(path, 'r', encoding='utf-8') as file:
        context = file.read()
    return {"role": "user", "content": context}

def getPrompt():
    tLen = 0
    prompt = []
    prompt.append(getIdentity("config/Hatsune/identity.txt"))
    prompt.append({"role": "system", "content": f"Below is the conversation's history.\n"})

    with open("dialogue.json", "r") as file:
        data = json.load(file)
    
    history = data["history"]

    for message in history[:-1]:
        prompt.append(message)

    prompt.append(
        {
            "role": "system",
            "content": f"Here is the latest conversation.\nMake sure you'll respond within {outputNumber} characters!\n",
        }
    )

    prompt.append(history[-1])

    tLen = sum(len(d['content']) for d in prompt)

    while tLen > 4096:
        try:
            prompt.pop(2)
            tLen = sum(len(d['content']) for d in prompt)
        except:
            print("Error! Prompt is too long!")

    return prompt

if __name__ == "__main__":
    prompt = getPrompt()
    print(prompt)
    print(len(prompt))
