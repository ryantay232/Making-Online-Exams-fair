import base64
import math
import os
import random
import socket
import sys
import threading
import time
from datetime import datetime
from multiprocessing import Process

import numpy as np
import pandas as pd
from Crypto import Random
from Crypto.Cipher import AES

import sample.student.webcam.webcam as webcam

# Server info
PORT = 5050
SERVER = '35.198.237.249'  # socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'

choices = """choices (enter the number):
1) GET
2) PUSH
3) SSTREAM
4) END
"""

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'

MSG_LEN = 2048000


def quiz_platform(student_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    s.connect(ADDR)
    print("{} Connected to server.".format(INFO_TAG))
    connected = True
    #msg = webcam.start_stream(student_id)
    #send_data(s, SECRET_KEY, msg)

    while connected:
        #try:
        print(choices)
        readstr = input('->')
        try:
            read = int(readstr)
        except ValueError:
            print(f"{ERROR_TAG}, Invalid input.")
        if read == 4:
            #send exit command to server
            msg = webcam.end_stream(student_id)
            Header = (f"!END|{MSG_LEN}")
            send_data(s, SECRET_KEY, Header)
            connected = False

        elif read == 1 or read == 2:
            Header = (f"!STU|{MSG_LEN}")
            send_data(s, SECRET_KEY, Header)
            message = recv_data(s, SECRET_KEY, int(MSG_LEN))

            if read == 1:
                #get the test script from server
                print("getting the quiz from server")
                data = (f"GET| | ")
                send_data(s, SECRET_KEY, data)
                message = recv_data(s, SECRET_KEY, int(MSG_LEN))
                # print(message)  #this should be the test script
                try:
                    d = os.getcwd()
                    d1 = os.path.join(d, "files_to_submit")
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

                d = os.getcwd()
                d1 = os.path.join(d, "files_to_submit")
                fname_ans = os.path.join(d1, f"{answer_script}.txt")
                fname_logs = os.path.join(d1, f"studentId.log")

                try:
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
                    with open(fname_logs, 'rt') as file1:
                        for lines1 in file1:
                            log_file = log_file + lines1
                    file1.close()
                except FileNotFoundError:
                    print(
                        f"{ERROR_TAG}, logs file not found in current directory..."
                    )
                    continue

                data = (f"PUSH|{answer_file}|{log_file}")
                send_data(s, SECRET_KEY, data)
                message = recv_data(s, SECRET_KEY, int(MSG_LEN))
                print(
                    f"{INFO_TAG} successfully submitted answer and logs to server"
                )

        else:
            print("{} Please enter a valid number...".format(ERROR_TAG))
        '''
        except (socket.error, KeyboardInterrupt, Exception):
            #reconnect to server
            connected = False
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
            count = 0
            while not connected:
                try:
                    print(
                        f"{ERROR_TAG}, connection lost, attempting to reconnect to server..."
                    )
                    #count += 1
                    s.connect(ADDR)  # connect to the server
                    connected = True
                    print("reconnection successful")
                except socket.error:
                    time.sleep(1)
                time.sleep(0.1)
        '''
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
    webcam.stream_webcam(student_id, student_webcam, SERVER)


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
    


#padding to make the message in multiples of 16
def padding(message):
    length = 16 - (len(message) % 16)
    message = message.encode()
    message += bytes([length]) * length
    #print(f"padding: {message}")
    return message


#decrypt the message
def decrypt_message(message, key):
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
    #print(f"sending encrypted data: {encoded}")
    return encoded


#pad the data, encrypt and send
def send_data(socket, secret_key, data):
    data = padding(data)
    data = encrypt_data(data, secret_key)
    socket.send(data)
    # print("sent data\n")


#receive message from client decrypt, unpad and decode
def recv_data(socket, secret_key, len):
    message = socket.recv(len).decode()  #wait to receive message
    message = decrypt_message(message, secret_key)
    message = message[:-message[-1]]  #remove padding
    message = message.decode(FORMAT)  #to remove b' '
    return message


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
