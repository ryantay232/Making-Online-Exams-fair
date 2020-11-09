import json
import os
import socket
import sys
import threading
import time
from os.path import getsize
from subprocess import PIPE, Popen

import sample.student.webcam.webcam as webcam
import tqdm

# Server info
PORT = 5050
FORMAT = 'utf-8'

choices = """choices (enter the number):
1. Download the quiz
2. Submit quiz and log files
3. Exit
"""

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'

MSG_LEN = 4096


def receive_file(s, path, filename, filesize):
    progress = tqdm.tqdm(range(filesize),
                         "Receiving {}".format(filename),
                         unit='B',
                         unit_scale=True,
                         unit_divisor=1024)
    bytes_received = 0
    with open(path, "wb") as f:
        for _ in progress:
            if bytes_received >= filesize:
                break
            bytes_read = s.recv(4096)
            f.write(bytes_read)
            bytes_received += len(bytes_read)
            progress.update(len(bytes_read))
    print("{} {} received.".format(INFO_TAG, filename))


def send_file(s, path, filename, filesize):
    progress = tqdm.tqdm(range(filesize),
                         "Sending {}".format(filename),
                         unit='B',
                         unit_scale=True,
                         unit_divisor=1024)
    with open(path, "rb") as f:
        for _ in progress:
            bytes_read = f.read(4096)
            if not bytes_read:
                break
            s.send(bytes_read)
            progress.update(len(bytes_read))
    print("{} {} sent.".format(INFO_TAG, filename))


def quiz_platform(server_ip, student_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    ADDR = (server_ip, PORT)
    s.connect(ADDR)
    print("{} Connected to server".format(INFO_TAG))
    # start stream
    header = (f"!STU|{MSG_LEN}").encode()
    s.send(header)
    message = s.recv(MSG_LEN).decode()
    msg = webcam.start_stream(student_id, server_ip).encode()
    s.send(msg)
    connected = True
    while connected:
        print(choices)
        readstr = input('->')
        try:
            read = int(readstr)
        except ValueError:
            print(f"{ERROR_TAG} Invalid format.")
            continue
        if read == 3:
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
                print("{} Getting the quiz from server.".format(INFO_TAG))
                Header = (f"!STU|{MSG_LEN}").encode()
                s.send(Header)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                data = (f"GET").encode()
                s.send(data)
                msg = s.recv(MSG_LEN).decode(FORMAT)
                filename, filesize = msg.split('|')
                d = os.getcwd()
                d1 = os.path.join(d, "student_files")
                fname_quiz = os.path.join(d1, "quiz.txt")
                receive_file(s, fname_quiz, filename, int(filesize))
                print(f"{INFO_TAG} received quiz successfully")
            elif read == 2:
                # push your answer to server,
                print("{} Submitting answer script and logs file".format(INFO_TAG))
                answer_script = input(
                    'key in the name of your answer script->')
                answer_file = " "
                log_file = " "
                json_file = " "

                d = os.getcwd()
                d1 = os.path.join(d, "student_files")

                try:
                    fname_ans = os.path.join(d1, f"{answer_script}.txt")
                    fsize_ans = getsize(fname_ans)
                except FileNotFoundError:
                    print(
                        f"{ERROR_TAG}, {answer_script} not found in current directory..."
                    )
                    continue

                try:
                    fname_logs = os.path.join(d1, f"studentId.log")
                    fsize_logs = getsize(fname_logs)
                except FileNotFoundError:
                    print(
                        f"{ERROR_TAG}, logs file not found in current directory..."
                    )
                    continue

                try:
                    fname_json = os.path.join(d1, f"studentId_access.json")
                    fsize_json = getsize(fname_json)
                except FileNotFoundError:
                    print(
                        f"{ERROR_TAG}, studentId_access.json file not found in current directory..."
                    )
                    continue
                Header = (f"!STU|{MSG_LEN}").encode()
                s.send(Header)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                data = (
                    f"PUSH|{student_id}|{fsize_ans}|{fsize_logs}|{fsize_json}"
                ).encode()
                s.send(data)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                send_file(s, fname_ans, fname_ans.split('/')[-1], fsize_ans)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                send_file(s, fname_logs, fname_logs.split('/')[-1], fsize_logs)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                send_file(s, fname_json, fname_json.split('/')[-1], fsize_json)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                print(
                    f"{INFO_TAG} successfully submitted answer and logs to server."
                )

            else:
                print("{} Please enter a valid number...".format(ERROR_TAG))

        time.sleep(0.01)

    print("{} Closing client program".format(INFO_TAG))
    s.close()


def port_flagging():
    print("{} Checking opened ports...".format(INFO_TAG))
    return Popen(["python", "-m", "sample.student.port_flagging.script"],
                 stdout=PIPE,
                 stderr=PIPE)

    #portflagging.main()


def webcam_streaming(server_ip, student_id, student_webcam):
    print("{} Streaming webcam...".format(INFO_TAG))
    child_process = webcam.stream_webcam(student_id, student_webcam, server_ip)
    return child_process


def client_program(server_ip):
    # input student ID
    student_id = input("Input student ID -> ")
    # choose webcam
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
    # start processes
    streaming_process = webcam_streaming(server_ip, student_id, student_webcam)
    portflagging_process = port_flagging()
    # run quiz platform
    quiz_platform(server_ip, student_id)
    # terminate processes
    streaming_process.terminate()
    portflagging_process.terminate()


def main(server_ip):
    print("{} Starting client...".format(INFO_TAG))
    client_program(server_ip)


if __name__ == "__main__":
    main('35.198.237.249')
