import socket

from sample.server.comdresult import ComdResult

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


# Given streamkey return stream link
def get_streamlink(msg):
    server_ip = socket.gethostbyname(socket.gethostname())
    return ComdResult("SSTREAM", "rtmp://{}/{}".format(server_ip, msg))


# Handle commands from clients
def handle_command(addr, msg):
    # Add additional header tags for different commands
    print("{} Student from {}: {}".format(INFO_TAG, addr, msg))
    msg_list = msg.split('|')
    comd = msg_list[0]
    data = msg_list[1]
    res = None

    if comd == "SSTREAM":
        res = get_streamlink(data)
    elif comd == "PUSH":
    elif comd == "GET":
    else:
        print("{} Invalid command".format(ERROR_TAG))

    return res
