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

import sample.server.comdresult as ComdResult
import sample.server.student_comd.student_comd as student_comd
import sample.server.instructor_comd.instructor_comd as instructor_comd

# Server info
HEADER = 1024
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'

# Headers to differentiate commands from different clients
END_MSG = "!END"
STUDENT_MSG = "!STU"
INST_MSG = "!INS"

# Binding server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Global vars
list_of_streams = []

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'

MSG_LEN = 2048000

# Handle result that changes global vars from requests
def handle_result(comdres, conn, addr):
    comd = comdres.comd
    res = comdres.res
    res1 = comdres.res1
    res2 = comdres.res2
    if comd == "SSTREAM":
        list_of_streams.append(res)
    elif comd == "GET_QUIZ":
        #send quiz to students
        print("sending student the quiz")
        d = os.getcwd()
        d1 = os.path.join(d, "server_files")
        d2 = os.path.join(d1, "quiz_file")
        fname_quiz = os.path.join(d2, f"quiz.txt")

        quiz_file = " "
        try:
            with open(fname_quiz, 'rt') as file:
                for lines in file:
                    quiz_file = quiz_file + lines
        except FileNotFoundError:
            print(f"{ERROR_TAG}, quiz file not found in directory...")
        quiz_file = quiz_file.encode()
        conn.send(quiz_file)

    elif comd == "PUSH_ANSWER":
        #save answer script in receive folder
        print("saving students answer scripts")

        d = os.getcwd()
        d1 = os.path.join(d, "server_files")
        d2 = os.path.join(d1, "student_answer_scripts")
        fname_ans = os.path.join(d2, f"{addr}_answer.txt")
        fname_logs = os.path.join(d2, f"{addr}_logs.txt")
        fname_json = os.path.join(d2, f"{addr}_json.txt")

        f = open(fname_ans, 'w')
        f1 = open(fname_logs, 'w')
        f2 = open(fname_json, 'w')

        f.write(res)
        f1.write(res1)
        f2.write(res2)

        f.close()
        f1.close()
        f2.close()

        conn.send(b' ')

    elif comd == "PUSH_QUIZ":
        #send quiz to server
        print("saving quiz to server")
        d = os.getcwd()
        d1 = os.path.join(d, "server_files")
        d2 = os.path.join(d1, "quiz_file")
        fname_quiz = os.path.join(d2, f"quiz.txt")

        f= open(fname_quiz, 'w')

        f.write(res)

        f.close()
        conn.send(b' ')
    else:
        print("{} Error in command".format(ERROR_TAG))
    print(list_of_streams)


# Handle requests from clients
def handle_client(conn, addr):
    print("{} New connection from {}".format(INFO_TAG, addr))

    connected = True
    while connected:
        try:
            msg = conn.recv(MSG_LEN).decode()  #wait to receive message
            header, msg_len = str(msg).split('|')
            conn.send(b' ')
            # From here onwards handle requests from clients
            if header == END_MSG:
                print("{} Ending connection with {}".format(INFO_TAG, addr))
                print(header)
                connected = False
            elif header == STUDENT_MSG:
                # Student side
                data = conn.recv(MSG_LEN).decode()  #wait to receive message

                handle_result(student_comd.handle_command(addr, data), conn, addr)
            elif header == INST_MSG:
                # Instructor side
                data = conn.recv(MSG_LEN).decode()  #wait to receive message
                conn.send(b' ')
                handle_result(instructor_comd.handle_command(addr, data), conn, addr)
            else:
                print("{} Invalid header".format(ERROR_TAG))

        except (socket.error, KeyboardInterrupt):
            print("client disconnected...")
            connected = False
            conn.close()

        time.sleep(0.01)

    conn.close()

# Start listening for clients
def start_server():
    server.listen()
    print("{} Listening on {}".format(INFO_TAG, ADDR))

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("{} Active connections: {}".format(INFO_TAG, threading.activeCount() - 1))
        time.sleep(0.01)

def main():
    print("{} Server starting...".format(INFO_TAG))
    start_server()


if __name__ == "__main__":
    main()
