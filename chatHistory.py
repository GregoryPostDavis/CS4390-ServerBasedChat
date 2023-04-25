from datetime import datetime

def write(filename, msgfrom, message):
    with open(filename, 'a') as file:
        file.write("<SESSION-ID> ")             # NEEDS UNIQUE SESSION-ID
        file.write(msgfrom + ": ")
        file.write(message)
        file.write('\n')

def readhistory(name):
    with open(name, 'r') as file:
        lines = file.readlines()
    return lines