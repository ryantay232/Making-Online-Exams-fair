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

# Server info
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
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

def client_program():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket

    s.connect(ADDR)
    print("connected to server")
    connected = True
    while connected:
        try:
            print(choices)
            readstr = input('->')
            try:
                read = int(readstr)
            except ValueError:
                print(f"{ERROR_TAG}, invalid format")
            if read == 4:
                #send exit command to server
                Header = (f"!END|{MSG_LEN}")
                send_data(s, SECRET_KEY, Header)
                connected = False

            elif read == 1 or read == 2:
                Header = (f"!STU|{MSG_LEN}")
                send_data(s, SECRET_KEY, Header)
                message = recv_data(s, SECRET_KEY)

                if read == 1:
                    #get the test script from server
                    print("getting the test script from server...")
                    data = (f"{GET}| |")
                    send_data(s, SECRET_KEY, data)
                    message = recv_data(s, SECRET_KEY, int(MSG_LEN))
                    print(message)  #this should be the test script

                elif read == 2:
                    # push your answer to server,
                    print("submitting answer script and logs file")
                    answer_script = input('key in the name of your answer script->')
                    answer_file = " "
                    log_file = " "

                    try:
                        with open(f'{answer_script}.txt', 'rt') as file:
                            for lines in file:
                                answer_file = answer_file + lines
                        file.close()
                    except FileNotFoundError:
                        print(f"{ERROR_TAG}, {answer_script} not found in current directory...")

                    try:
                        with open('studentId.log', 'rt') as file1:
                            for lines1 in file1:
                                log_file = log_file + lines1
                        file1.close()
                    except FileNotFoundError:
                        print(f"{ERROR_TAG}, logs file not found in current directory...")

                    data = (f"{PUSH}|{answer_file}|{log_file}")
                    send_data(s, SECRET_KEY, data)
                    print("submitting your answer and logs to server...")

            else:
                print("please enter a valid number...")

        except (socket.error, KeyboardInterrupt, Exception):
            #reconnect to server
            connected = False
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
            while not connected:
                try:
                    print(f"{ERROR_TAG}, connection lost, attempting to reconnect to server...")
                    s.connect((host, port))  # connect to the server
                    connected = True
                    print("reconnection successful")
                except socket.error:
                    time.sleep(1)
                time.sleep(0.1)
        time.sleep(0.01)
    print("closing client program")
    s.close()

#padding to make the message in multiples of 16
def padding(message):
    length = 16 - (len(message) % 16)
    message = message.encode()
    message += bytes([length])*length
    print(f"padding: {message}")
    return message

#decrypt the message
def decrypt_message(message,key):
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
    print(f"sending encrypted data: {encoded}")
    return encoded

#pad the data, encrypt and send
def send_data(socket, secret_key, data):
    data = padding(data)
    data = encrypt_data(data,secret_key)
    socket.send(data)
    print("sent data\n")

#receive message from client decrypt, unpad and decode
def recv_data(socket, secret_key, len):
    message = socket.recv(len).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode(FORMAT)    #to remove b' '
    return message

#receive message from client decrypt, unpad and decode
def recv_data(s, secret_key, len):
    message = s.recv(len).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode(FORMAT)    #to remove b'1|rocketman|'
    return message

def main():
    # Client script for testing
    client_thread = threading.Thread(target=client_program, args=())
    print("starting client thread...")
    client_thread.start()
    client_thread.join()

    print("done!!")

if __name__ == "__main__":
    main()
