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
    data = msg_list[1]
    res = None

    if comd == "PUSH":
        #submit quiz to server
        res = push_quiz(data)
    return res
