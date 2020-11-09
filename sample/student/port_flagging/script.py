import json
import os.path
import shutil
from contextlib import redirect_stdout

import sample.student.port_flagging.portflaging as portflaging

diffFileName = 'diff.log'
logFileNamePath = './student_files/studentId.log'
tempFileName = 'temp.log'
accessAppFilePath = './student_files/studentId_access.json'


def compare(File1, File2):
    with open(File1, 'r') as f:
        d = set(f.readlines())

    with open(File2, 'r') as f:
        e = set(f.readlines())

    open(diffFileName, 'w').close()

    with open(diffFileName, 'a') as f:
        for line in list(d - e):
            f.write(line)


def append(File1):
    f1 = open(File1, 'a+')
    f2 = open(diffFileName, 'r')
    f1.write(f2.read())
    f1.seek(0)
    f2.seek(0)
    f1.close()
    f2.close()
    os.remove(diffFileName)


def main():
    with open(tempFileName, 'w') as f:
        with redirect_stdout(f):
            portflaging.main()

    if (os.path.isfile(logFileNamePath) == False):
        original = tempFileName
        target = logFileNamePath
        shutil.copyfile(original, target)
    else:
        compare(tempFileName, logFileNamePath)
        append(logFileNamePath)

    #open log file to read if student have access app in the restricted list
    with open(logFileNamePath) as l:
        logFileContent = l.read()

    #load restricted app list
    with open('./sample/student/port_flagging/restricted_app.json', 'r') as ra:
        jsonObject = json.load(ra)
        appList = jsonObject['restricted_app']

    #load the current access app on the json end
    with open(accessAppFilePath, 'r') as access:
        jsonObjectAccess = json.load(access)
        accessApp = set(jsonObjectAccess['app_accessed'])
        for app in appList:
            if app in logFileContent:
                accessApp.add(app)
        jsonObjectAccess['app_accessed'] = list(accessApp)

    #update the app accessed
    with open(accessAppFilePath, 'w') as access:
        json.dump(jsonObjectAccess, access)


if __name__ == '__main__':
    main()
