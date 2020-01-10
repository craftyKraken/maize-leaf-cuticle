"""Script written to ping the GoreLab server with any changes to IP address.

This is written to be run as a regular cron job. When run, it checks to see if
there is an internet connection. If there is not, nothing else will be done. If
there is, it will check to see if the IP address has changed since the last
update. If so, it will change the local record (in ip.txt) and ping the GoreLab
server with the change, which should then be reflected at a known url.

Author: James Chamness
Last modified: May 04, 2017
"""
import httplib
import logging
import socket
import subprocess
import time

""""Set up logger routing to console and to file"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('IP_Tracker.log', mode='a'))

"""Load the probe-specific configuration"""
def loadConf(confFilename):
    confFile = open(confFilename)
    lines = list(map(lambda x: x.strip(), confFile.readlines()))
    probeName = lines[0].split(" ")[2]
    unitNumber = lines[1].split(" ")[2]
    pin = int(lines[2].split(" ")[2]) # GPIO pin the DHT22 probe is connected to
    host = lines[3].split(" ")[2]
    user = lines[4].split(" ")[2]
    pwd = lines[5].split(" ")[2]
    db = lines[6].split(" ")[2]
    table = lines[7].split(" ")[2]
    return (probeName, unitNumber, pin, host, user, pwd, db, table)

"""Test if there is an internet connection"""
def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

"""Get the current IP address"""
def get_ip():
    # What I was using before, which works when calling python script from shell but not when script is put in cron job
    # Go figure
#     sysCommandString = "ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'"
#     ip = subprocess.check_output(sysCommandString,shell=True)
#     ip = ip.strip()
#     logger.debug("IP is: #" + ip + "#")
#     return ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80)) # this is Google's public DNS page. this line would fail if there was no internet connection
    return(s.getsockname()[0])

"""Update the local file storing the IP address with (potentially) new address.

    Check the local file storing IP address. If address on file is the same as
    argument, return False. If different, replace old address on file with new
    address and return True.

    Arguments:
    ip -- string of new IP address
"""
def update_ip_local(ip):
    ipFilename = "ip.txt"
    with open(ipFilename, 'r') as f:
        oldIP = f.readlines()[0].strip()
        #logger.debug("Old IP: " + oldIP)
        if oldIP == ip:
            return False
    with open(ipFilename, 'w') as f:
        f.write(ip)
        return True

"""Ping the GoreLab server with IP update.
"""
def update_ip_server(ip, unitNumber):
    sysCommandString = "" # hardcoded
    subprocess.call(sysCommandString, shell=True)

"""Executable"""
if __name__ == "__main__":
    
    probeName, unitNumber, pin, host, user, passwd, db, table = loadConf("ProbeLogger.conf")
    
    if not have_internet():
        quit()
    else:
        ip = get_ip()
        if update_ip_local(ip):
            logger.debug("IP change logged at " + str(time.asctime()))
            logger.debug("New IP: " + ip)
            update_ip_server(ip, unitNumber)
            logger.debug("GoreLab server pinged with new IP")
    
    
    
    
    
    
    
    
    
    