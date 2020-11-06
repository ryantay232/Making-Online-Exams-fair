import socket

from sample.server.comdresult import ComdResult

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


# Given streamkey return stream link
def get_streamlink(msg):
    server_ip = socket.gethostbyname(socket.gethostname())
    return ComdResult("SSTREAM", "rtmp://{}/{}".format(server_ip, msg))

def push_script(answer_file, log_file):
    return ComdResult("PUSH", answer_file, log_file)

# Handle commands from clients
def handle_command(addr, msg):
    # Add additional header tags for different commands
    print("{} Student from {}: ".format(INFO_TAG, addr))
    msg_list = str(msg).split('|')
    comd = msg_list[0]
    data = msg_list[1]
    data1 = msg_list[2]
    res = None

    if comd == "SSTREAM":
        res = get_streamlink(data)
    elif comd == "PUSH":
        #submit answer to server
        res = push_script(data, data1)
    elif comd == "GET":
        #get the script from server
        print("get script")
        quiz_file = " "
        try:
            with open('quiz.txt', 'rt') as file:
                for lines in file:
                    quiz_file = quiz_file + lines

            res = quiz_file
        except FileNotFoundError:
            print(f"{ERROR_TAG}, quiz file not found in directory...")
    else:
        print("{} Invalid command".format(ERROR_TAG))

    return res
