import json
import os
import socket
import sys
import threading
import time
from os import listdir
from os.path import getsize, isfile, join
from subprocess import run

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
recordings_path = '/var/www/html/recordings'
submissions_path = './server_files/student_answer_scripts'
list_of_streams = {}

MSG_LEN = 4096


def receive_file(s, path, filesize):
    bytes_received = 0
    with open(path, "wb") as f:
        while bytes_received < filesize:
            bytes_read = s.recv(4096)
            f.write(bytes_read)
            bytes_received += len(bytes_read)
    print("{} {} received.".format(INFO_TAG, path))


def send_file(s, path, filesize):
    with open(path, "rb") as f:
        bytes_read = f.read(4096)
        while bytes_read:
            s.send(bytes_read)
            bytes_read = f.read(4096)
    print("{} {} sent.".format(INFO_TAG, path))


# Handle result that changes global vars from requests
def handle_result(comdres, conn, addr):
    comd = comdres.comd
    if comd == "SSTREAM":
        # student start streaming to server
        list_of_streams[comdres.res] = comdres.res1
    elif comd == "ESTREAM":
        # student end streaming to server
        del list_of_streams[comdres.res]
    elif comd == "GETSTREAM":
        # send list of streams to instructor
        data = json.dumps(list_of_streams).encode(FORMAT)
        conn.send(data)
    elif comd == "GETRECORD":
        # send list of recordings to instructor
        files = str([
            f for f in listdir(recordings_path)
            if isfile(join(recordings_path, f))
        ]).encode()
        conn.send(files)
    elif comd == "DLRECORD":
        # send stream to instructor
        files = [
            f for f in listdir(recordings_path)
            if isfile(join(recordings_path, f))
        ]
        filename = "{}/{}".format(recordings_path, files[int(comdres.res) - 1])
        filesize = getsize(filename)
        msg = "{}|{}".format(filename, filesize).encode(FORMAT)
        conn.send(msg)
        send_file(conn, filename, filesize)
    elif comd == "GET_QUIZ":
        # send quiz to students
        print("{} Sending student the quiz.".format(INFO_TAG))
        d = os.getcwd()
        d1 = os.path.join(d, "server_files")
        d2 = os.path.join(d1, "quiz_file")
        fname_quiz = os.path.join(d2, f"quiz.txt")
        filesize = getsize(fname_quiz)
        msg = "{}|{}".format(fname_quiz.split('/')[-1],
                             filesize).encode(FORMAT)
        conn.send(msg)
        send_file(conn, fname_quiz, filesize)
    elif comd == "PUSH_ANSWER":
        # save answer script in receive folder
        print("{} Saving students answer scripts.".format(INFO_TAG))
        student_id = comdres.res
        d = os.getcwd()
        d1 = os.path.join(d, "server_files")
        d2 = os.path.join(d1, "student_answer_scripts")
        fname_ans = os.path.join(d2, f"{student_id}_answer.txt")
        fname_logs = os.path.join(d2, f"{student_id}_logs.txt")
        fname_json = os.path.join(d2, f"{student_id}_json.txt")
        conn.send(b' ')
        receive_file(conn, fname_ans, int(comdres.res1))
        conn.send(b' ')
        receive_file(conn, fname_logs, int(comdres.res2))
        conn.send(b' ')
        receive_file(conn, fname_json, int(comdres.res3))
        conn.send(b' ')
    elif comd == "PUSH_QUIZ":
        # send quiz to server
        print("{} Saving quiz to server.".format(INFO_TAG))
        conn.send(b' ')
        d = os.getcwd()
        d1 = os.path.join(d, "server_files")
        d2 = os.path.join(d1, "quiz_file")
        fname_quiz = os.path.join(d2, f"quiz.txt")
        filesize = comdres.res
        receive_file(conn, fname_quiz, int(filesize))
        conn.send(b' ')
    elif comd == "GETSUB":
        # get students' submissions
        files = [
            f for f in listdir(submissions_path)
            if isfile(join(submissions_path, f))
        ]
        msg = "{}".format(len(files)).encode(FORMAT)
        conn.send(msg)
        conn.recv(MSG_LEN)
        for f in files:
            filename = "{}/{}".format(submissions_path, f)
            filesize = getsize(filename)
            msg = "{}|{}".format(f, filesize).encode(FORMAT)
            conn.send(msg)
            send_file(conn, filename, filesize)
            conn.recv(MSG_LEN)
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
                data = conn.recv(
                    int(msg_len)).decode()  #wait to receive message

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
