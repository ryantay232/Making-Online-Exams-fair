import base64
import json
import math
import os
import random
import socket
import sys
import threading
import time
from datetime import datetime

import numpy as np
import pandas as pd
from Crypto import Random
from Crypto.Cipher import AES

# Server info
PORT = 5050
SERVER = '35.198.237.249'  #socket.gethostbyname(socket.gethostname())
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

# Client info
CLIENT_IP = socket.gethostbyname(socket.gethostname())

# Server info
HOST = "35.185.186.41"  # to change to server ip address
PORT = 5050
FORMAT = 'utf-8'

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
                print_streams(s)
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


# Get list of student streams (will move to own file)
def print_streams(s):
    to_send = "!INS|{}".format(MSG_LEN).encode(FORMAT)
    s.send(to_send)
    s.recv(MSG_LEN)
    msg = "GETSTREAM".encode()
    s.send(msg)
    reply = s.recv(MSG_LEN).decode(FORMAT)
    streams_dict = json.loads(reply)
    if len(streams_dict) == 0:
        print("{} No streams running now.".format(INFO_TAG))
    else:
        print("Student Id   Stream Link")
        for key in list(streams_dict.keys()):
            print("{: <13}{}".format(key, streams_dict[key]))


# Get list of recordings
def get_list_of_recordings(s):
    to_send = "!INS|{}".format(MSG_LEN).encode(FORMAT)
    s.send(to_send)
    s.recv(MSG_LEN)
    msg = "GETRECORD".encode()
    s.send(msg)
    reply = s.recv(MSG_LEN).decode(FORMAT)
    recordings_list = list(reply)


# Send file
def receive_file(s):
    path = "instructor_files/streams"


if __name__ == "__main__":
    main()
