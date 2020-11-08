import base64
import math
import os
import random
import socket
import sys
import threading
import time
import json
from datetime import datetime
from multiprocessing import Process

import sample.student.webcam.webcam as webcam

# Server info
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname(
))  #'35.198.237.249'  # socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

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


def quiz_platform(student_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket

    s.connect(ADDR)
    print("connected to server")
    # start stream
    header = (f"!STU|{MSG_LEN}").encode()
    s.send(header)
    message = s.recv(MSG_LEN).decode()
    msg = webcam.start_stream(student_id).encode()
    s.send(msg)
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
            # end stream
            msg = webcam.end_stream(student_id).encode()
            header = (f"!STU|{len(msg)}").encode()
            s.send(header)
            message = s.recv(MSG_LEN).decode()
            s.send(msg)
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
                answer_script = input(
                    'key in the name of your answer script->')
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
                    print(
                        f"{ERROR_TAG}, {answer_script} not found in current directory..."
                    )
                    continue

                try:
                    fname_logs = os.path.join(d1, f"studentId.log")
                    with open(fname_logs, 'rt') as file1:
                        for lines1 in file1:
                            log_file = log_file + lines1
                    file1.close()
                except FileNotFoundError:
                    print(
                        f"{ERROR_TAG}, logs file not found in current directory..."
                    )
                    continue

                try:
                    fname_json = os.path.join(d1, f"restricted_app.json")
                    with open(fname_json, 'rt') as file2:
                        json_list = json.load(file2)
                        for lines2 in json_list['restricted_app']:
                            json_file = json_file + (f"{lines2} ")
                except FileNotFoundError:
                    print(
                        f"{ERROR_TAG}, restricted_app json file not found in current directory..."
                    )
                    continue

                Header = (f"!STU|{MSG_LEN}").encode()
                s.send(Header)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                data = (
                    f"PUSH|{student_id}|{answer_file}|{log_file}|{json_file}"
                ).encode()
                s.send(data)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                print(
                    f"{INFO_TAG} successfully submitted answer and logs to server"
                )

            else:
                print("please enter a valid number...")

        time.sleep(0.01)

    print("closing client program")
    s.close()


def port_flagging(n):
    # replace with your own code
    for i in range(n):
        #print("func2 {}".format(i))
        None


def webcam_streaming(student_id, student_webcam):
    #print("webcam = {}".format(webcam))
    print("{} Streaming webcam...".format(INFO_TAG))
    #webcam.stream_webcam(student_id, student_webcam, SERVER)


def run_in_parallel(funcs, args):
    proc = []
    for i in range(len(funcs)):
        p = Process(target=funcs[i], args=args[i])
        p.start()
        proc.append(p)
    quiz_platform()
    for p in proc:
        p.join()


def client_program():
    student_id = input("Input student ID -> ")
    webcam_list = webcam.get_webcam_list()
    student_webcam = None
    while student_webcam is None:
        while student_webcam is None:
            print("Webcams available:")
            for i in range(len(webcam_list)):
                print("{}. {}".format(i + 1, webcam_list[i]))
            choice = input("Choose a webcam -> ")
            try:
                student_webcam = webcam_list[int(choice) - 1]
            except ValueError:
                print("{} Invalid input".format(ERROR_TAG))
            except IndexError:
                print("{} Invalid input".format(ERROR_TAG))
        isWorking = webcam.test_webcam(student_webcam)
        if not isWorking:
            student_webcam = None

    funcs = [port_flagging, webcam_streaming]
    args = [(100, ), (
        student_id,
        student_webcam,
    )]

    proc = []
    for i in range(len(funcs)):
        p = Process(target=funcs[i], args=args[i])
        p.start()
        proc.append(p)
    quiz_platform(student_id)
    for p in proc:
        p.join()
    #run_in_parallel(funcs, args)


def main():
    # Client script for testing
    #client_thread = threading.Thread(target=client_program, args=())
    print("starting client thread...")
    client_program()
    #client_thread.start()
    #client_thread.join()

    print("done!!")


if __name__ == "__main__":
    main()
