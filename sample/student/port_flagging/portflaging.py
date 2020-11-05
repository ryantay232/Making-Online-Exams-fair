#duration of the exam
#Sever to accept log every one min or log it locally 1st then upload.
#Access list of the restricted app so that it would notified the server?
#log file
#

#need sudo to run the script

# run on student end - who will start my script? 
# do i peridically send log ot the server? or after the exam 
# flag out on the base on restricted list and send notification on instructor end? 


import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM

import psutil

AD = "-"
AF_INET6 = getattr(socket, 'AF_INET6', object())
proto_map = {
    (AF_INET, SOCK_STREAM): 'tcp',
    (AF_INET6, SOCK_STREAM): 'tcp6',
    (AF_INET, SOCK_DGRAM): 'udp',
    (AF_INET6, SOCK_DGRAM): 'udp6',
}


def main():
    templ = "%-5s %-30s %-30s %-13s %-6s %s"
    print(templ % ("Proto", "Local address", "Remote address", "Status", "PID",
                   "Program name"))
    proc_names = {}
    for p in psutil.process_iter(['pid', 'name']):
        proc_names[p.info['pid']] = p.info['name']
    for c in psutil.net_connections(kind='inet'):
        laddr = "%s:%s" % (c.laddr)
        raddr = ""
        if c.raddr:
            raddr = "%s:%s" % (c.raddr)
        print(templ % (
            proto_map[(c.family, c.type)],
            laddr,
            raddr or AD,
            c.status,
            c.pid or AD,
            proc_names.get(c.pid, '?')[:15],
        ))