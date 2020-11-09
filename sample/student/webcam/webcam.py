import socket
from subprocess import PIPE, Popen, run


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


# Stream webcam to server
def stream_webcam(student_id, webcam, HOST):
    # ffmpeg -f dshow -s 640x480 -framerate 30 -i video=<webcam> -vcodec libx264
    # -preset ultrafast -tune zerolatency -f flv rtmp://<server>/live/<student_id>
    child_process = Popen([
        "ffmpeg", "-f", "dshow", "-s", "640x480", "-framerate", "30", "-i",
        "video={}".format(webcam), "-vcodec", "libx264", "-preset",
        "ultrafast", "-tune", "zerolatency", "-f", "flv",
        "rtmp://{}/live/{}".format(HOST, student_id)
    ],
                          stdout=PIPE,
                          stderr=PIPE)
    return child_process


# Tell server that stream is starting
def start_stream(student_id, server):
    msg = "SSTREAM|{0}|rtmp://{1}/live/{0}".format(student_id, server)
    return msg


# Tell server that stream is ending
def end_stream(student_id):
    msg = "ESTREAM|{}".format(student_id)
    return msg
