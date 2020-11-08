import base64
import json
import math
import os
import random
import socket
import sys
import threading
import time
from os import listdir
from os.path import isfile, join, getsize
from datetime import datetime

import sample.server.comdresult as ComdResult
import sample.server.instructor_comd.instructor_comd as instructor_comd
import sample.server.student_comd.student_comd as student_comd

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
list_of_streams = {}

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'

MSG_LEN = 2048000


# Handle result that changes global vars from requests
def handle_result(comdres, conn, addr):
    comd = comdres.comd
    res = comdres.res
    res1 = comdres.res1
    res2 = comdres.res2
    res3 = comdres.res3
    if comd == "SSTREAM":
        student_id = res[0]
        list_of_streams[res[0]] = res[1]
    elif comd == "ESTREAM":
        del list_of_streams[res]
    elif comd == "GETSTREAM":
        data = json.dumps(list_of_streams).encode(FORMAT)
        conn.send(data)
    elif comd == "GETRECORD":
        recordings_path = '/var/www/html/recordings'
        files = str([
            f for f in listdir(recordings_path)
            if isfile(join(recordings_path, f))
        ]).encode()
        conn.send(files)
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
        print("student_id: {}".format(res))
        d = os.getcwd()
        d1 = os.path.join(d, "server_files")
        d2 = os.path.join(d1, "student_answer_scripts")
        fname_ans = os.path.join(d2, f"{res}_answer.txt")
        fname_logs = os.path.join(d2, f"{res}_logs.txt")
        fname_json = os.path.join(d2, f"{res}_json.txt")

        f = open(fname_ans, 'w')
        f1 = open(fname_logs, 'w')
        f2 = open(fname_json, 'w')

        f.write(res1)
        f1.write(res2)
        f2.write(res3)

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

        f = open(fname_quiz, 'w')

        f.write(res)

        f.close()
        conn.send(b' ')
    else:
        print("{} Error in command".format(ERROR_TAG))


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
                connected = False
            elif header == STUDENT_MSG:
                # Student side
                data = conn.recv(
                    int(msg_len)).decode()  #wait to receive message

                handle_result(student_comd.handle_command(addr, data), conn,
                              addr)
            elif header == INST_MSG:
                # Instructor side
                data = conn.recv(MSG_LEN).decode()  #wait to receive message
                #conn.send(b' ')
                handle_result(instructor_comd.handle_command(addr, data), conn,
                              addr)
            else:
                print("{} Invalid header".format(ERROR_TAG))

        except (socket.error, KeyboardInterrupt):
            print("{} Client disconnected...".format(ERROR_TAG))
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
        print("{} Active connections: {}".format(INFO_TAG,
                                                 threading.activeCount() - 1))
        time.sleep(0.01)


def main():
    print("{} Server starting...".format(INFO_TAG))
    start_server()


if __name__ == "__main__":
    main()
