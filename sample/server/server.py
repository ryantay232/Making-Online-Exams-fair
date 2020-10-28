import socket
import threading
import json

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
    else:
        print("{} Error in command".format(ERROR_TAG))


# Handle requests from clients
def handle_client(conn, addr):
    print("{} New connection from {}".format(INFO_TAG, addr))

    connected = True
    while connected:
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


def main():
    print("{} Server starting...".format(INFO_TAG))
    start_server()


if __name__ == "__main__":
    main()
