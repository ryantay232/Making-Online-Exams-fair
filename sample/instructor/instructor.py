import json
import os
import socket
import sys
import threading

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
2. Check flagged students
3. Print list of students' streams
4. Print list of recordings
5. Download student's stream
6. Exit
"""

# Client info
CLIENT_IP = socket.gethostbyname(socket.gethostname())
recordings_path = "instructor_files/streams"

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
                print_streams(s)
            elif choice == 4:
                get_list_of_recordings(s)
            elif choice == 5:
                download_stream(s)
        elif choice == 6:
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
    recordings_list = reply[1:-1].split(', ')
    if len(recordings_list) == 0:
        print("{} No recordings in server.".format(INFO_TAG))
    else:
        for i in range(len(recordings_list)):
            print("{}. {}".format(i + 1, recordings_list[i][1:-1]))


# Send file
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
    progress = tqdm.tqdm(range(filesize),
                         "Receiving {}".format(filename),
                         unit='B',
                         unit_scale=True,
                         unit_divisor=1024)
    bytes_received = 0
    recording_filepath = "./{}/{}".format(recordings_path, filename)
    with open(recording_filepath, "wb") as f:
        for _ in progress:
            if bytes_received >= filesize:
                break
            bytes_read = s.recv(4096)
            f.write(bytes_read)
            bytes_received += len(bytes_read)
            progress.update(len(bytes_read))
    print("{} {} downloaded.".format(INFO_TAG, filename))


if __name__ == "__main__":
    main()
