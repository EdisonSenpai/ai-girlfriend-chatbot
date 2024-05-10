def generateSubtitle(chatNow, rezID):
    # In OBS se va seta subtitrarea si se foloseste output.txt
    with open("output.txt", "w", encoding="utf-8") as out:
        try:
            text = rezID
            words = text.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]

            for line in lines:
                out.write(" ".join(line) + "\n")
        except:
            print("Error while writing to \"output.txt\"")

    # Tot in OBS se va seta intrebarea/chat-ul si se foloseste chat.txt
    with open("chat.txt", "w", encoding="utf-8") as out:
        try:
            words = chatNow.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]

            for line in lines:
                out.write(" ".join(line) + "\n")
        except:
            print("Error while writing to \"chat.txt\"")