import socket
import json

# Temporary menu, will change if needed
menu = """
1. Upload quiz
2. Choose default quiz
3. Check flagged students
4. Print list of students' streams
5. Download student's stream
6. Exit
"""

# Client info
CLIENT_IP = socket.gethostbyname(socket.gethostname())

# Server info
HOST = "35.185.186.41"  # to change to server ip address
PORT = 5050
FORMAT = 'utf-8'

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


# Get list of student streams (will move to own file)
def get_streams():
    s = socket.socket()
    s.connect((HOST, PORT))
    msg = "GETSTREAM"
    to_send = "!INS|{:08d}|{}".format(len(msg), msg)
    s.send(str.encode(to_send))
    reply = s.recv(4096).decode(FORMAT)
    s.send(str.encode("!END"))
    s.close()
    streams_dict = json.loads(reply)
    if len(streams_dict) == 0:
        print("{} No streams running now.".format(INFO_TAG))
    else:
        print("Student Id   Stream Link")
        for key in list(streams_dict.keys()):
            print("{: <13}{}".format(key, streams_dict[key]))


def main():
    choice = 0
    while choice != 6:
        print(menu)
        choicestr = input("Input: ")
        try:
            choice = int(choicestr)
        except ValueError:
            print("{} Invalid input".format(ERROR_TAG))
        if choice == 1:
            # replace with your own code
            print("Upload quiz")
        elif choice == 2:
            # replace with your own code
            print("Choose default quiz")
        elif choice == 3:
            # replace with your own code
            print("Check flagged students")
        elif choice == 4:
            get_streams()
        elif choice == 5:
            # replace with your own code
            print("Download student's stream")
        elif choice == 6:
            print("Exiting...")
        else:
            print("{} Invalid input".format(ERROR_TAG))


if __name__ == "__main__":
    main()
