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
import json

# Server info
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'

choices = """choices (enter the number):
1. Download the quiz
2. Submit quiz and log files
3. SSTREAM
4. Exit
"""

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'

MSG_LEN = 2048000

def client_program():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket

    s.connect(ADDR)
    print("connected to server")
    connected = True
    while connected:
        print(choices)
        readstr = input('->')
        try:
            read = int(readstr)
        except ValueError:
            print(f"{ERROR_TAG}, invalid format")
            continue
        if read == 4:
            #send exit command to server
            Header = (f"!END|{MSG_LEN}").encode()
            s.send(Header)
            connected = False

        elif read == 1 or read == 2:
            if read == 1:
                #get the test script from server
                print("getting the quiz from server")
                Header = (f"!STU|{MSG_LEN}").encode()
                s.send(Header)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                data = (f"GET| | | ").encode()
                s.send(data)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                # print(message)  #this should be the test script
                try:
                    d = os.getcwd()
                    d1 = os.path.join(d, "student_files")
                    fname_quiz = os.path.join(d1, "quiz.txt")
                    file = open(fname_quiz, 'w')
                    file.write(message)
                    file.close()
                except:
                    print(f"{ERROR_TAG}, cannot write to file...")
                print(f"{INFO_TAG} received quiz successfully")

            elif read == 2:
                # push your answer to server,
                print("submitting answer script and logs file")
                answer_script = input('key in the name of your answer script->')
                answer_file = " "
                log_file = " "
                json_file = " "

                d = os.getcwd()
                d1 = os.path.join(d, "student_files")

                try:
                    fname_ans = os.path.join(d1, f"{answer_script}.txt")
                    with open(fname_ans, 'rt') as file:
                        for lines in file:
                            answer_file = answer_file + lines
                    file.close()
                except FileNotFoundError:
                    print(f"{ERROR_TAG}, {answer_script} not found in current directory...")
                    continue

                try:
                    fname_logs = os.path.join(d1, f"studentId.log")
                    with open(fname_logs, 'rt') as file1:
                        for lines1 in file1:
                            log_file = log_file + lines1
                    file1.close()
                except FileNotFoundError:
                    print(f"{ERROR_TAG}, logs file not found in current directory...")
                    continue

                try:
                    fname_json = os.path.join(d1, f"restricted_app.json")
                    with open(fname_json, 'rt') as file2:
                        json_list = json.load(file2)
                        for lines2 in json_list['restricted_app']:
                            json_file = json_file + (f"{lines2} ")
                except FileNotFoundError:
                    print(f"{ERROR_TAG}, restricted_app json file not found in current directory...")
                    continue

                Header = (f"!STU|{MSG_LEN}").encode()
                s.send(Header)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                data = (f"PUSH|{answer_file}|{log_file}|{json_file}").encode()
                s.send(data)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                print(f"{INFO_TAG} successfully submitted answer and logs to server")

            else:
                print("please enter a valid number...")

        time.sleep(0.01)
    print("closing client program")
    s.close()

def main():
    client_program()

    print("done!!")

if __name__ == "__main__":
    main()
