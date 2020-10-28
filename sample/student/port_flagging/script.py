import portflaging
from contextlib import redirect_stdout
import os.path
import shutil
import diff_match_patch as dmp_module  # pip3 install diff-match-patch

#check windows user need admin privillage to run the script anot

if __name__ == '__main__':
    with open('temp', 'w') as f:
        with redirect_stdout(f):
            portflaging.main()

    if (os.path.isfile('./log') == False):
        original = r'temp'
        target = r'log'
        shutil.copyfile(original, target)
    else:
        temp = open("temp").read()
        log = open("log").read()

        dmp = dmp_module.diff_match_patch()
        diff = dmp.diff_main(temp, log)
        dmp.diff_cleanupSemantic(diff)

        output = ""
        for s in diff:
            output += s[1]

        f = open("log", "w")
        f.write(output)
        f.close()
