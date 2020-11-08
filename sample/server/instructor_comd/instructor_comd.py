from sample.server.comdresult import ComdResult

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


def push_quiz(quiz_file):
    return ComdResult("PUSH_QUIZ", quiz_file)


# Handle commands from clients
def handle_command(addr, msg):
    # Add additional header tags for different commands
    print("{} Instructor from {}".format(INFO_TAG, addr))
    msg_list = msg.split('|')
    comd = msg_list[0]
    res = None

    if comd == "GETSTREAM":
        res = ComdResult(comd)
    elif comd == "GETRECORD":
        res = ComdResult(comd)
    elif comd == "DLRECORD":
        data = msg_list[1]
        res = ComdResult(comd, data)
    elif comd == "PUSH":
        #submit quiz to server
        data = msg_list[1]
        res = push_quiz(data)
    else:
        print("{} Invalid command".format(ERROR_TAG))

    return res
