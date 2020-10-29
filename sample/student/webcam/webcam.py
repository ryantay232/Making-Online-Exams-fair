from subprocess import run, CompletedProcess


# Get a list of webcam from command
def get_webcam_list():
    # ffmpeg -list_devices true -f dshow -i dummy
    obj = run(
        ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
        capture_output=True)
    output = obj.stderr.decode("utf-8")
    # parsing output
    s = output.split("DirectShow video devices")[1].split(
        "DirectShow audio devices")[0].split("\n")
    devices = []
    for i in s:
        ss = i.split("Alternative name")
        if len(ss) <= 1:
            device = ss[0].split('"')
            if len(device) > 1:
                devices.append(device[1])
    return devices


# Test webcam and if working, return true
def test_webcam(webcam):
    # ffmpeg -f dshow -i video="webcam"
    obj = run(["ffmpeg", "-f", "dshow", "-i", "video={}".format(webcam)],
              capture_output=True)
    output = obj.stderr.decode("utf-8")
    # parsing output
    s = output.split("\n")
    s = s.pop(len(s) - 2)
    # if ffmpeg is able to open the webcam,
    # the string below will be returned since output file isn't specified
    return s == "At least one output file must be specified\r"


# Tell server that stream is starting
def start_stream(s, student_id, HOST, PORT):
    s.connect((HOST, PORT))
    msg = "SSTREAM|{}".format(student_id)
    to_send = "!STU|{:08d}|{}".format(len(msg), msg)
    s.send(str.encode(to_send))
    s.send(str.encode("!END"))
    s.close()


# Tell server that stream is ending
def end_stream(s, webcam):

    print("test")
