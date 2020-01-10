"""Monitor status of DHT22 probe logger and update on locally hosted webpage.

This script should be in the same directory as the probe logger script, and be
run with permissions allowing it to edit /var/www/html. It should launch at
startup.



Author: James Chamness
Last modified April 28, 2017
"""
import jinja2
import json
import logging
import subprocess
import os
import time

""""Set up logger routing to console and to file"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('Monitor.log', mode='w'))

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

"""Return a diagnostic from test of ProbeLogger status.

    Checks to see if the system process for the ProbeLogger script is currently
    running, and return two values. If the process is running, return True and
    the uptime in seconds. If the process is not running, return False and the
    downtime in seconds.
"""
def testProbeLoggerStatus():
    
    #logger.debug("Testing probe status")
    
    operational = True
    try:
        pid = subprocess.check_output(["pgrep","-f","ProbeLogger.py"])
        #logger.debug("Found process!")
    except subprocess.CalledProcessError as e:
        # interestingly, if this same command is called from a bash terminal and
        # no results are found, it just doesn't print anything, but if called
        # using subprocess, and no results are found, it throws an exception.
        # I don't have a good explanation for that but hey this works
        operational = False
        #logger.debug("Did NOT find process!")
    
    if operational:
        """determine uptime from log file"""
        with open("ProbeLogger.log") as f:
            lines = f.readlines()
            firstRead = int(lines[-1].split('\t')[1])
            present = int(time.time())
            uptime = present - firstRead        
        return(True,uptime)
    else:
        """determine downtime from readings log file"""
        with open("ProbeLog.csv") as f:
            lastRead = int(f.readlines()[-1].split('\t')[1])
            present = int(time.time())
            downtime = present - lastRead
        return(False,downtime)

"""Perform initial render of webpage and set status object to "booting"
    
    Arguments:
    probeName -- the name of the probe this script is running on
"""
def renderMonitoringPage(probeName):
    
    publicPageFilename = "../../var/www/html/index.html"
        
    templateLoader = jinja2.FileSystemLoader(searchpath=os.getcwd())
    templateEnv = jinja2.Environment(loader=templateLoader)
    templateFilename = "MonitoringPage.jinja"
    template = templateEnv.get_template(templateFilename)
        
    templateVars = { "probeName" : probeName + " (Unit " + unitNumber + ")"}
    
    outputText = template.render(templateVars)
    outputFile = open(publicPageFilename,'w')
    outputFile.write(outputText)
    outputFile.close()
    
    
    with open("ProbeLog.csv") as f:
        lastRead = int(f.readlines()[-1].split('\t')[1])
        present = int(time.time())
        downtime = present - lastRead
    
    obj = ["Pi booted, sensor logger still launching...","Downtime",downtime]
    publicPageFilename = "../../var/www/html/status.html"
    jsonFilestream = open(publicPageFilename,'w')
    json.dump(obj,jsonFilestream)
    jsonFilestream.close()
    return

"""Update status object on public page for site.
"""
def updateMonitoringPage():
    
    status, time = testProbeLoggerStatus()
    if status:
        status = "running"
        timeCode = "Uptime"
    else:
        status = "DOWN"
        timeCode = "Downtime"
    
    obj = [status,timeCode,time]
    
    publicPageFilename = "../../var/www/html/status.html"
    jsonFilestream = open(publicPageFilename,'w')
    json.dump(obj,jsonFilestream)
    jsonFilestream.close()
    return

"""Executable"""
if __name__ == "__main__":
    
    logger.debug('Monitor launched at ' + str(time.asctime()))
    logger.debug("Loading configuration")
    probeName, unitNumber, pin, host, user, passwd, db, table = loadConf("ProbeLogger.conf")
    logger.debug("Performing initial monitoring page render")
    renderMonitoringPage(probeName)
    logger.debug("Waiting for ProbeLogger to launch...")
    time.sleep(120) # wait so that ProbeLogger.py can finish startup routine
    logger.debug("Starting Monitoring loop...")
    
    while (True):
        updateMonitoringPage()
        time.sleep(1)
    
    