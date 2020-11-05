import sys

import sample.student.student as student
import sample.instructor.instructor as instructor
import sample.server.server as server


def main():
    arg_count = len(sys.argv)
    if arg_count < 2 or arg_count > 2:
        print("USAGE: run.py <student|instructor|server>")
    else:
        if sys.argv[1] == 'student':
            print("Running student...")
            student.main()
        elif sys.argv[1] == 'instructor':
            print("Running instructor...")
            instructor.main()
        elif sys.argv[1] == 'server':
            print("Running server...")
            server.main()
        else:
            print("USAGE: run.py <student|instructor|server>")


if __name__ == "__main__":
    main()
