import socket
import time
import threading
from Crypto.Cipher import AES
import base64
from Crypto import Random
import random

# Server info
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#secret key to encrypt/decrypt eg.
SECRET_KEY = b'0123456789ABCDEF'

def client_program():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    # host = input('your IP address->')
    # port = 5050
    secret_key = input('enter secret key for encrypt/decrypt->') #must be length 16, eg. 0123456789abcdef

    s.connect(ADDR)
    print("connected to server")
    connected = True
    while connected:
        try:
            choices = """choices (enter the number):
            1) GET
            2) PUSH
            3) SSTREAM
            4) END

            """
            print(choices)
            read = input('->')
            if read == "4":
                #send exit command to server
                Header = (f"!END")
                send_data(s, SECRET_KEY, Header)
                connected = False

            elif read == 1 or 2:
                Header = (f"!STU")
                send_data(s, SECRET_KEY, Header)
                message = recv_data(s, SECRET_KEY)
                length = (f":1024")
                send_data(s, SECRET_KEY, length)
                message = recv_data(s, SECRET_KEY)
                #data send would need HEADERS "!STU|GET|<data>" or "!STU|PUSH|<data>"
                if read == 1:
                    #get the test script from server
                    data = (f"{GET}|")
                    send_data(s, SECRET_KEY, data)
                    #receive the file in buffers??
                    message = recv_data(s, SECRET_KEY)
                    print(message)  #this should be the test script

                elif read == 2:
                    # push your answer to server, read from text file??
                    answers = (f"{ }")
                    data = (f"{PUSH}|{answers}")
                    #get the student answers from text or word file and send in buffers??
                    send_data(s, SECRET_KEY, data)

            else:
                print("please enter a valid number...")

        except (socket.error, KeyboardInterrupt, Exception):
            #reconnect to server
            connected = False
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
            while not connected:
                try:
                    print("error, connection lost, attempting to reconnect to server...")
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
def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_data(data,secret_key)
    conn.send(data)
    print("sent data\n")

#receive message from ultra96, decrypt, unpad and decode
def recv_data(s, secret_key):
    message = s.recv(1024).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode('utf8')    #to remove b'1|rocketman|'
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
