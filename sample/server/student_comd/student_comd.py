import socket

from sample.server.comdresult import ComdResult

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


# Given streamkey return stream link
def get_streamlink(msg):
    server_ip = socket.gethostbyname(socket.gethostname())
    return ComdResult("SSTREAM", (msg, "rtmp://{}/live/{}".format(server_ip, msg)))


def end_stream(msg):
    return ComdResult("ESTREAM", msg)


# Handle commands from clients
def handle_command(addr, msg):
    # Add additional header tags for different commands
    print("{} Student from {}: {}".format(INFO_TAG, addr, msg))
    msg_list = msg.split('|')
    comd = msg_list[0]
    res = None

    if comd == "SSTREAM":
        data = msg_list[1]
        res = get_streamlink(data)
    elif comd == "ESTREAM":
        data = msg_list[1]
        res = end_stream(data)
    else:
        print("{} Invalid command".format(ERROR_TAG))

    return res
