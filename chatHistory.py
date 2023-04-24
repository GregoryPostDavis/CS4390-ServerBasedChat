from datetime import datetime

def write(msgfrom, message):
    with open("filename.txt", 'a') as file:
        file.write("<SESSION-ID> ")             # NEEDS UNIQUE SESSION-ID
        file.write(msgfrom + ": ")
        file.write(message)
        file.write('\n')

def readhistory(name):
    with open(name, 'r') as file:
        #content = file.read()
        #print(content)
        lines = file.readlines()
    return lines