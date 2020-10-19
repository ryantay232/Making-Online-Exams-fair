import socket
import threading

# Server info
HEADER = 4
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# Tagging logs
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'

# Headers to differentiate commands from different clients
END_MSG = "!END"
STUDENT_MSG = "!STU"
INST_MSG = "!INS"

# Binding server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


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
            # Add additional header tags for different commands
            print("student side")
        elif msg == INST_MSG:
            # Instructor side
            # Same as student, add additional header tags for different commands
            print("instructor side")
        else:
            print("{} Invalid header".format(ERROR_TAG))
        print("{} From {}: {}".format(INFO_TAG, addr, msg))

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
