import portflaging
from contextlib import redirect_stdout
import os.path
import shutil

#check windows user need admin privillage to run the script anot

diffFileName = 'diff.log'
logFileName = 'studentId.log'
tempFileName = 'temp.log'

def compare(File1,File2):
    with open(File1,'r') as f:
        d=set(f.readlines())

    with open(File2,'r') as f:
        e=set(f.readlines())

    open(diffFileName,'w').close() #Create the file


    with open(diffFileName,'a') as f:
        for line in list(d-e):
            f.write(line)

def append(File1):
    f1 = open(File1,'a+')
    f2 = open(diffFileName,'r')
    f1.write(f2.read())
    f1.seek(0) 
    f2.seek(0)
    f1.close() 
    f2.close() 
    # os.remove(diffFileName)


if __name__ == '__main__':
    with open(tempFileName, 'w') as f:
        with redirect_stdout(f):
            portflaging.main()

    if (os.path.isfile(logFileName) == False):
        # original = r'temp'
        # target = r'log'
        original = tempFileName
        target = logFileName
        shutil.copyfile(original, target)
    else:
        compare(tempFileName,logFileName)
        append(logFileName)
        # temp = open("temp").read()
        # log = open("log").read()

        # dmp = dmp_module.diff_match_patch()
        # diff = dmp.diff_main(temp, log)
        # dmp.diff_cleanupSemantic(diff)

        # output = ""
        # for s in diff:
        #     output += s[1]

        # f = open("log", "w")
        # f.write(output)
        # f.close()
