import socket
import threading
import json
import time
import base64
import random

from Crypto import Random
from Crypto.Cipher import AES

import sample.server.comdresult as ComdResult
import sample.server.student_comd.student_comd as student_comd
import sample.server.instructor_comd.instructor_comd as instructor_comd

# Server info
HEADER = 4
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

answer_scripts = {}

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'


# Handle result that changes global vars or send replies from requests
def handle_result(s, comdres):
    comd = comdres.comd
    res = comdres.res
    if comd == "SSTREAM":
        list_of_streams[res[0]] = res[1]
    elif comd == "ESTREAM":
        del list_of_streams[res]
    elif comd == "GETSTREAM":
        s.send(json.dumps(list_of_streams).encode(FORMAT))
    elif comd == "GET":
        #get the test script
        print("test")
    elif comd == "PUSH":
        #submit test script
        print("test")
    else:
        print("{} Error in command".format(ERROR_TAG))


# Handle requests from clients
def handle_client(conn, addr):
    print("{} New connection from {}".format(INFO_TAG, addr))

    connected = True
    while connected:
        '''
        msg = conn.recv(HEADER).decode(FORMAT)
        # From here onwards handle requests from clients
        if msg == END_MSG:
            print("{} Ending connection with {}".format(INFO_TAG, addr))
            connected = False
        elif msg == STUDENT_MSG:
            # Student side
            msg_len = conn.recv(10).decode(FORMAT)
            data = conn.recv(int(msg_len[1:9])).decode(FORMAT)
            handle_result(conn, student_comd.handle_command(addr, data))
        elif msg == INST_MSG:
            # Instructor side
            msg_len = conn.recv(10).decode(FORMAT)
            data = conn.recv(int(msg_len[1:9])).decode(FORMAT)
            handle_result(conn, instructor_comd.handle_command(addr, data))
        else:
            print("{} Invalid header".format(ERROR_TAG))
        '''
        try:
            # msg = conn.recv(HEADER).decode(FORMAT)
            msg = recv_data(conn, SECRET_KEY, HEADER)
            header, msg_len = str(msg).split('|')
            send_data(conn, SECRET_KEY, ' ')
            # From here onwards handle requests from clients
            if header == END_MSG:
                print("{} Ending connection with {}".format(INFO_TAG, addr))
                connected = False
            elif header == STUDENT_MSG:
                # Student side
                data = recv_data(conn, SECRET_KEY, int(msg_len))
                handle_result(student_comd.handle_command(addr, data))
            elif header == INST_MSG:
                # Instructor side
                data = recv_data(conn, SECRET_KEY, int(msg_len))
                handle_result(instructor_comd.handle_command(addr, data))
            else:
                print("{} Invalid header".format(ERROR_TAG))

        except (socket.error, KeyboardInterrupt):
            #reconnecting to client
            print(f"error, connection lost for thread {threading.get_ident()}")
            conn.close()
            time.sleep(1)
            server_socket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)  # get instance
            try:
                server_socket.bind(ADDR)  # bind host address and port together
            except socket.error as e:
                print(str(e))
            print(
                f"attempting to reconnect on thread {threading.get_ident()}..."
            )
            print(f"listening...")
            # configure server into listen mode
            server_socket.listen(1)

            conn, address = server_socket.accept()  # accept new connection
            print(
                f"successfully reconnected for thread {threading.get_ident()}!!"
            )
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
        print("{} Active connections: {}".format(INFO_TAG,
                                                 threading.activeCount() - 1))
        time.sleep(0.01)


#padding to make the message in multiples of 16
def padding(message):
    length = 16 - (len(message) % 16)
    message = message.encode()
    message += bytes([length]) * length
    print(f"padding: {message}")
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
    print(f"sending encrypted data: {encoded}")
    return encoded


#pad the data, encrypt and send
def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_data(data, secret_key)
    conn.send(data)
    print("sent data\n")


#receive message from client decrypt, unpad and decode
def recv_data(s, secret_key, len):
    message = s.recv(len).decode()  #wait to receive message
    message = decrypt_message(message, secret_key)
    message = message[:-message[-1]]  #remove padding
    message = message.decode(FORMAT)  #to remove b'1|rocketman|'
    return message


def main():
    print("{} Server starting...".format(INFO_TAG))
    start_server()


if __name__ == "__main__":
    main()
