from multiprocessing import Process


def quizplatform(n):
    # replace with your own code
    for i in range(n):
        print("func1 {}".format(i))


def portflagging(n):
    # replace with your own code
    for i in range(n):
        print("func2 {}".format(i))


def webcamstreaming(n):
    # replace with your own code
    for i in range(n):
        print("func3 {}".format(i))


def runInParallel(funcs, args):
    proc = []
    for i in range(len(funcs)):
        p = Process(target=funcs[i], args=args[i])
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


def main():
    # list of functions and args tuples 
    # (replace args with your own args, numbers just for testing)
    funcs = [quizplatform, portflagging, webcamstreaming]
    args = [(70, ), (100, ), (80, )]

    runInParallel(funcs, args)


if __name__ == "__main__":
    main()
