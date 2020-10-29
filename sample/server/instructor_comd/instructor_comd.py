from sample.server.comdresult import ComdResult

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


# Handle commands from clients
def handle_command(addr, msg):
    # Add additional header tags for different commands
    print("{} Instructor from {}: {}".format(INFO_TAG, addr, msg))
    msg_list = msg.split('|')
    comd = msg_list[0]
    data = msg_list[1]
    res = None

    return res
