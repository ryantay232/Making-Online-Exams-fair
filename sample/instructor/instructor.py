# Temporary menu, will change if needed
menu = """
1. Upload quiz
2. Choose default quiz
3. Check flagged students
4. Print list of students' streams
5. Download student's stream
6. Exit
"""

# logging tags
INFO_TAG = '[INFO]'
ERROR_TAG = '[ERROR]'


def main():
    choice = 0
    while choice != 6:
        print(menu)
        choicestr = input("Input: ")
        try:
            choice = int(choicestr)
        except ValueError:
            print("{} Invalid input".format(ERROR_TAG))
        if choice == 1:
            # replace with your own code
            print("Upload quiz")
        elif choice == 2:
            # replace with your own code
            print("Choose default quiz")
        elif choice == 3:
            # replace with your own code
            print("Check flagged students")
        elif choice == 4:
            # replace with your own code
            print("Print list of students' streams")
        elif choice == 5:
            # replace with your own code
            print("Download student's stream")
        elif choice == 6:
            print("Exiting...")
        else:
            print("{} Invalid input".format(ERROR_TAG))


if __name__ == "__main__":
    main()
