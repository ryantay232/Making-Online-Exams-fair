import socket

from sample.server.comdresult import ComdResult

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


# Given streamkey return stream link
def get_streamlink(msg):
    server_ip = socket.gethostbyname(socket.gethostname())
    return ComdResult("SSTREAM",
                      (msg, "rtmp://{}/live/{}".format(server_ip, msg)))


def end_stream(msg):
    return ComdResult("ESTREAM", msg)


def push_script(answer_file, log_file, json_file):
    return ComdResult("PUSH_ANSWER", answer_file, log_file, json_file)


def get_quiz():
    return ComdResult("GET_QUIZ")


# Handle commands from clients
def handle_command(addr, msg):
    # Add additional header tags for different commands
    print("{} Student from {}: ".format(INFO_TAG, addr))
    msg_list = str(msg).split('|')
    comd = msg_list[0]
    res = None

    if comd == "SSTREAM":
        data = msg_list[1]
        res = get_streamlink(data)
    elif comd == "ESTREAM":
        data = msg_list[1]
        res = end_stream(data)
    elif comd == "PUSH":
        #submit answer to server
        data = msg_list[1]
        data1 = msg_list[2]
        data2 = msg_list[3]
        res = push_script(data, data1, data2)
    elif comd == "GET":
        #get the script from server
        res = get_quiz()
    else:
        print("{} Invalid command".format(ERROR_TAG))

    return res
