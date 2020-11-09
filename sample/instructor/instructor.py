import json
import os
import socket
import sys
import threading
from os.path import getsize

import tqdm

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
2. Download students' submissions
3. Print list of students' streams
4. Print list of recordings
5. Download student's stream
6. Exit
"""

# Client info
CLIENT_IP = socket.gethostbyname(socket.gethostname())
recordings_path = "instructor_files/streams"
submissions_path = "instructor_files/submissions"

# Server info
HOST = "35.185.186.41"
PORT = 5050
FORMAT = 'utf-8'

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'

MSG_LEN = 4096


# Download students' submissions
def download_submissions(s):
    to_send = "!INS|{}".format(MSG_LEN).encode(FORMAT)
    s.send(to_send)
    s.recv(MSG_LEN)
    msg = "GETSUB".encode(FORMAT)
    s.send(msg)
    reply = s.recv(MSG_LEN).decode(FORMAT)
    no_of_files = int(reply)
    s.send(b' ')
    for _ in range(no_of_files):
        reply = s.recv(MSG_LEN).decode(FORMAT)
        filename, filesize = reply.split('|')
        path = "{}/{}".format(submissions_path, filename)
        receive_file(s, path, filename, int(filesize))
        s.send(b' ')
    print("{} Submissions downloaded.".format(INFO_TAG))


# Get list of student streams (will move to own file)
def print_streams(s):
    to_send = "!INS|{}".format(MSG_LEN).encode(FORMAT)
    s.send(to_send)
    s.recv(MSG_LEN)
    msg = "GETSTREAM".encode(FORMAT)
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
    recordings_list = reply[1:-1].split(', ')
    if len(recordings_list) == 0:
        print("{} No recordings in server.".format(INFO_TAG))
    else:
        for i in range(len(recordings_list)):
            print("{}. {}".format(i + 1, recordings_list[i][1:-1]))


# Download selected stream
def download_stream(s):
    choice = None
    while choice is None:
        choicestr = input("Recording no.: ")
        try:
            choice = int(choicestr)
        except ValueError:
            print(f"{ERROR_TAG}, invalid format")

    to_send = "!INS|{}".format(MSG_LEN).encode(FORMAT)
    s.send(to_send)
    s.recv(MSG_LEN)
    msg = "DLRECORD|{}".format(choice).encode()
    s.send(msg)
    reply = s.recv(MSG_LEN).decode(FORMAT)
    path, filesize = reply.split('|')
    filename = os.path.basename(path.split("/")[-1])
    filesize = int(filesize)
    dest_filepath = "./{}/{}".format(recordings_path, filename)
    receive_file(s, dest_filepath, filename, filesize)


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


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    s.connect(ADDR)
    print("{} Connected to server".format(INFO_TAG))

    quiz_script = " "
    choice = 0
    while choice != 6:
        print(menu)
        choicestr = input("Input: ")
        try:
            choice = int(choicestr)
        except ValueError:
            print(f"{ERROR_TAG}, invalid format")
            continue
        if choice < 6:
            if choice == 1:
                # replace with your own code
                print("Uploading quiz, Choose default quiz")
                quiz_script = input('Key in the name of the quiz->')
                filepath = None
                try:
                    d = os.getcwd()
                    d1 = os.path.join(d, "instructor_files")
                    filepath = os.path.join(d1, f"{quiz_script}.txt")
                    print(f"{INFO_TAG} Successfully chosen {quiz_script}.txt")
                except FileNotFoundError:
                    print(f"{ERROR_TAG} Enter a valid filename...")
                    continue

                filename = "{}.txt".format(quiz_script)
                filesize = getsize(filepath)
                Header = (f"!INS|{MSG_LEN}").encode()
                s.send(Header)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                data = (f"PUSH|{filesize}").encode()
                s.send(data)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                send_file(s, filepath, filename, filesize)
                message = s.recv(MSG_LEN).decode()  #wait to receive message
                print(f"{INFO_TAG} successfully uploaded quiz")
            elif choice == 2:
                download_submissions(s)
            elif choice == 3:
                print_streams(s)
            elif choice == 4:
                get_list_of_recordings(s)
            elif choice == 5:
                download_stream(s)
        elif choice == 6:
            print("{} Exiting...".format(INFO_TAG))
            #send exit command to server
            Header = (f"!END|{MSG_LEN}").encode()
            s.send(Header)

        else:
            print("{} Invalid input".format(ERROR_TAG))

    print("{} Closing instructor program".format(INFO_TAG))
    s.close()


if __name__ == "__main__":
    main()
