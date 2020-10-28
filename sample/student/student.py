import socket

from multiprocessing import Process

from sample.student.webcam.webcam import get_webcam_list, test_webcam, stream_webcam, start_stream

# Client info
CLIENT_IP = socket.gethostbyname(socket.gethostname())

# Server info
HOST = "192.168.2.100"  # to change to server ip address
PORT = 5050
FORMAT = 'utf-8'

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


def quiz_platform(n):
    # replace with your own code
    for i in range(n):
        print("func1 {}".format(i))


def port_flagging(n):
    # replace with your own code
    for i in range(n):
        print("func2 {}".format(i))


def webcam_streaming(student_id, webcam):
    stream_webcam(student_id, webcam, HOST)


def run_in_parallel(funcs, args):
    proc = []
    for i in range(len(funcs)):
        p = Process(target=funcs[i], args=args[i])
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


def main():
    # identify student
    student_id = input("Student id: ")

    # authenticate student (are we still doing account and password?)
    # sock = socket.socket()
    # sock.conect((HOST, PORT))

    # choose webcam
    webcam_list = get_webcam_list()
    webcam = None
    while webcam is None:
        while webcam is None:
            print("Webcams available:")
            for i in range(len(webcam_list)):
                print("{}. {}".format(i + 1, webcam_list[i]))
            choice = input("Choose a webcam: ")
            try:
                webcam = webcam_list[int(choice) - 1]
            except ValueError:
                print("{} Invalid input".format(ERROR_TAG))
            except IndexError:
                print("{} Invalid input".format(ERROR_TAG))
        isWorking = test_webcam(webcam)
        if not isWorking:
            webcam = None

    start_stream(student_id, HOST, PORT)

    # list of functions and args tuples
    # (replace args with your own args, numbers just for testing)
    funcs = [quiz_platform, port_flagging, webcam_streaming]
    args = [(70, ), (100, ), (
        student_id,
        webcam,
    )]

    run_in_parallel(funcs, args)


if __name__ == "__main__":
    main()
