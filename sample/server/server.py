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
        send_data(conn,SECRET_KEY,res)

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
        
        send_data(conn, SECRET_KEY, ' ')

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
        send_data(conn,SECRET_KEY,' ')
    else:
        print("{} Error in command".format(ERROR_TAG))
    print(list_of_streams)


# Handle requests from clients
def handle_client(conn, addr):
    print("{} New connection from {}".format(INFO_TAG, addr))

    connected = True
    while connected:
        try:
            msg = recv_data(conn, SECRET_KEY, HEADER)
            header, msg_len = str(msg).split('|')
            send_data(conn, SECRET_KEY, ' ')
            # From here onwards handle requests from clients
            if header == END_MSG:
                print("{} Ending connection with {}".format(INFO_TAG, addr))
                print(header)
                connected = False
            elif header == STUDENT_MSG:
                # Student side
                data = recv_data(conn, SECRET_KEY, int(msg_len))
                # d1, d2, d3 = str(data).split('|')
                # print(d2)
                # print(d3)
                handle_result(student_comd.handle_command(addr, data), conn, addr)
            elif header == INST_MSG:
                # Instructor side
                data = recv_data(conn, SECRET_KEY, int(msg_len))
                # d1, d2 = str(data).split('|')
                # print(d1)
                # print(d2)
                send_data(conn, SECRET_KEY, ' ')
                handle_result(instructor_comd.handle_command(addr, data), conn, addr)
            else:
                print("{} Invalid header".format(ERROR_TAG))

        except (socket.error, KeyboardInterrupt):
            #reconnecting to client
            print(f"error, connection lost for thread {threading.get_ident()}")
            conn.close()
            time.sleep(1)
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
            try:
                server_socket.bind(ADDR)  # bind host address and port together
            except socket.error as e:
                print(str(e))
            print(f"attempting to reconnect on thread {threading.get_ident()}...")
            print(f"listening...")
            # configure server into listen mode
            server_socket.listen(1)

            conn, address = server_socket.accept()  # accept new connection
            print(f"successfully reconnected for thread {threading.get_ident()}!!")
            # print(f"Connected to: {address[0]} : {str(address[1])} on thread")
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

#padding to make the message in multiples of 16
def padding(message):
    length = 16 - (len(message) % 16)
    message = message.encode()
    message += bytes([length])*length
    # print(f"padding: {message}")
    return message

#decrypt the message
def decrypt_message(message,key):
    #print("decrpyting message")
    decoded_message = base64.b64decode(message)
    iv = decoded_message[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])
    return decrypted_message

#encrypt the message
def encrypt_data(data, key):
    #print("\t\tencrypting data")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(data))
    # print(f"sending encrypted data: {encoded}")
    return encoded

#pad the data, encrypt and send
def send_data(socket, secret_key, data):
    data = padding(data)
    data = encrypt_data(data,secret_key)
    socket.send(data)
    # print("sent data\n")

#receive message from client decrypt, unpad and decode
def recv_data(socket, secret_key, len):
    message = socket.recv(len).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode(FORMAT)    #to remove b' '
    return message

def main():
    print("{} Server starting...".format(INFO_TAG))
    start_server()


if __name__ == "__main__":
    main()
