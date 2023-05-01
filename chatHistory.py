from datetime import datetime

def write(session_id, filename, msgfrom, message):
    with open(filename, 'a') as file:
        file.write("<" + session_id + "> ")             # NEEDS UNIQUE SESSION-ID
        file.write(msgfrom + ": ")
        file.write(message)
        file.write('\n')

def readhistory(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines