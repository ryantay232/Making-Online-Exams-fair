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
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'

# Temporary menu, will change if needed
menu = """
1. Upload quiz
2. Choose default quiz
3. Check flagged students
4. Print list of students' streams
5. Download student's stream
6. Exit
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

#padding to make the message in multiples of 16
def padding(message):
    length = 16 - (len(message) % 16)
    message = message.encode()
    message += bytes([length])*length
    print(f"padding: {message}")
    return message

#decrypt the message
def decrypt_message(message,key):
    #print("decrpyting message")
    decoded_message = base64.b64decode(message)
    iv = decoded_message[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])
    #print(f"{decrypt_message}")
    return decrypted_message

#encrypt the message
def encrypt_data(data, key):
    #print("\t\tencrypting data")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(data))
    print(f"sending encrypted data: {encoded}")
    return encoded

#pad the data, encrypt and send
def send_data(socket, secret_key, data):
    data = padding(data)
    data = encrypt_data(data,secret_key)
    socket.send(data)
    print("sent data\n")

#receive message from client decrypt, unpad and decode
def recv_data(socket, secret_key, len):
    message = socket.recv(len).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode(FORMAT)    #to remove b' '
    return message

# Get list of student streams (will move to own file)
def get_streams():
    s = socket.socket()
    s.connect((HOST, PORT))
    msg = "GETSTREAM"
    to_send = "!INS|{:08d}|{}".format(len(msg), msg)
    s.send(str.encode(to_send))
    reply = s.recv(4096).decode(FORMAT)
    s.send(str.encode("!END"))
    s.close()
    streams_dict = json.loads(reply)
    if len(streams_dict) == 0:
        print("{} No streams running now.".format(INFO_TAG))
    else:
        print("Student Id   Stream Link")
        for key in list(streams_dict.keys()):
            print("{: <13}{}".format(key, streams_dict[key]))


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    s.connect(ADDR)
    print("connected to server")

    quiz_script = " "
    choice = 0
    while choice != 6:
        print(menu)
        choicestr = input("Input: ")
        try:
            choice = int(choicestr)
        except ValueError:
            print("{} Invalid input".format(ERROR_TAG))
        if choice == 1:
            # replace with your own code
            print("Upload quiz")
            quiz_file = " "
            try:
                with open(f'{quiz_script}.txt', 'rt') as file:
                    for lines in file:
                        quiz_file = quiz_file + lines
            except FileNotFoundError:
                print(f"{ERROR_TAG}, enter a valid filename...")

            data = (f"!INS|{quiz_file}")
            send_data(s, SECRET_KEY, quiz_file)
            message = recv_data(s, SECRET_KEY, 2048000)

        elif choice == 2:
            # replace with your own code
            print("Choose default quiz")
            quiz_script = input('key in the name of the quiz->')

        elif choice == 3:
            # replace with your own code
            print("Check flagged students")
        elif choice == 4:
            get_streams()
        elif choice == 5:
            # replace with your own code
            print("Download student's stream")
        elif choice == 6:
            print("Exiting...")
        else:
            print("{} Invalid input".format(ERROR_TAG))

    print("closing instructor program")
    s.close()

if __name__ == "__main__":
    main()
