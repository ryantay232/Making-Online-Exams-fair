from sample.server.comdresult import ComdResult

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


# Given streamkey return stream link
def get_streamlink(student_id, streamlink):
    #server_ip = socket.gethostbyname(socket.gethostname())
    return ComdResult("SSTREAM", student_id, streamlink)


def end_stream(msg):
    return ComdResult("ESTREAM", msg)


def push_script(student_id, fsize_ans, fsize_logs, fsize_json):
    return ComdResult("PUSH_ANSWER", student_id, fsize_ans, fsize_logs,
                      fsize_json)


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
        res = get_streamlink(msg_list[1], msg_list[2])
    elif comd == "ESTREAM":
        data = msg_list[1]
        res = end_stream(data)
    elif comd == "PUSH":
        #submit answer to server
        student_id = msg_list[1]
        fsize_ans = msg_list[2]
        fsize_logs = msg_list[3]
        fsize_json = msg_list[4]
        res = push_script(student_id, fsize_ans, fsize_logs, fsize_json)
    elif comd == "GET":
        #get the script from server
        res = get_quiz()
    else:
        print("{} Invalid command".format(ERROR_TAG))

    return res
