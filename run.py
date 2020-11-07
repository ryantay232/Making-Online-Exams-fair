import sys


def main():
    arg_count = len(sys.argv)
    if arg_count < 2 or arg_count > 2:
        print("USAGE: run.py <student|instructor|server>")
    else:
        if sys.argv[1] == 'student':
            import sample.student.student as student
            print("Running student...")
            student.main()
        elif sys.argv[1] == 'instructor':
            import sample.instructor.instructor as instructor
            print("Running instructor...")
            instructor.main()
        elif sys.argv[1] == 'server':
            import sample.server.server as server
            print("Running server...")
            server.main()
        else:
            print("USAGE: run.py <student|instructor|server>")


if __name__ == "__main__":
    main()
