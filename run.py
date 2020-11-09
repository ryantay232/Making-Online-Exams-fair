import sys


def main():
    usage = "USAGE: run.py <student|instructor|server> <ip address if student|instructor>"
    arg_count = len(sys.argv)
    if arg_count < 2 or arg_count > 3:
        print(usage)
    else:
        if sys.argv[1] == 'student':
            import sample.student.student as student
            try:
                server_ip = sys.argv[2]
                print("Running student...")
                student.main(server_ip)
            except IndexError:
                print(usage)
        elif sys.argv[1] == 'instructor':
            import sample.instructor.instructor as instructor
            try:
                server_ip = sys.argv[2]
                print("Running instructor...")
                instructor.main(server_ip)
            except IndexError:
                print(usage)
        elif sys.argv[1] == 'server':
            import sample.server.server as server
            print("Running server...")
            server.main()
        else:
            print(usage)


if __name__ == "__main__":
    main()
