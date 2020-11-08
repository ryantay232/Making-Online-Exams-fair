import os
import sys
import random
import time
import socket
import threading
from datetime import datetime
import base64
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import math

# Server info
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'

# Temporary menu, will change if needed
menu = """
1. Upload quiz
2. Check flagged students
3. Print list of students' streams
4. Download student's stream
5. Exit
"""

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'

MSG_LEN = 2048000

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    s.connect(ADDR)
    print("connected to server")

    quiz_script = " "
    quiz_file = " "
    choice = 0
    while choice != 5:
        print(menu)
        choicestr = input("Input: ")
        try:
            choice = int(choicestr)
        except ValueError:
            print(f"{ERROR_TAG}, invalid format")
            continue
        if choice < 5:
            if choice == 1:
                # replace with your own code
                print("Uploading quiz, Choose default quiz")
                quiz_script = input('key in the name of the quiz->')

                try:
                    d = os.getcwd()
                    d1 = os.path.join(d, "instructor_files")
                    fname_quiz = os.path.join(d1, f"{quiz_script}.txt")
                    with open(fname_quiz, 'rt') as file:
                        for lines in file:
                            quiz_file = quiz_file + lines
                    print(f"{INFO_TAG} successfully chosen {quiz_script}.txt")
                except FileNotFoundError:
                    print(f"{ERROR_TAG} enter a valid filename...")
                    continue
                Header = (f"!INS|{MSG_LEN}").encode()
                s.send(Header)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                data = (f"PUSH|{quiz_file}").encode()
                s.send(data)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                print(f"{INFO_TAG} successfully uploaded quiz")

            elif choice == 2:
                # replace with your own code
                print("Check flagged students")
            elif choice == 3:
                # replace with your own code
                print("Print list of students' streams")
            elif choice == 4:
                # replace with your own code
                print("Download student's stream")

        elif choice == 5:
            print("Exiting...")
            #send exit command to server
            Header = (f"!END|{MSG_LEN}").encode()
            s.send(Header)

        else:
            print("{} Invalid input".format(ERROR_TAG))

    print("closing instructor program")
    s.close()

if __name__ == "__main__":
    main()
