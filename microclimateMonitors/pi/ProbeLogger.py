"""Fault-tolerant script to continuously log measurements from DHT22 sensor.

This script should be placed in the user (pi) crontab, to launch at boot. 
Readings from the sensor are logged to both a local archive (a text file) and a
MySQL database. Both of these should be initialized with at least the null entry
before this script is first called. Unit-specific configuration for the MySQL
database and the GPIO pin number for the sensor should be specified in a
'ProbeLogger.conf' configuration file, in the same directory as the script. 

This script runs two routines: a startup routine, followed by a continuous
logging routine. At startup, tests are run for the sensor connection, and access
to the target MySQL database. The sensor connection test must pass or the script
will terminate. If the MySQL access test fails, the logger routine will start,
but it will only record readings to the local archive. If it succeeds, a
subroutine will check if the local archive and MySQL database are synced, sync
if necessary, then launching a logging routine recording readings to both.

For any logging routine, new entries will be appended with unique IDs,
incrementing from the ID of the entry with the highest ID found at startup,
(using the local archive for reference). NOTE: encountered a weird bug whereby
a line is written at the end of the local archive (ProbeLog.csv) file that
renders as a repetition of ^@^@^@^@^@ chars but is really corrupted bytecode.
My current hypothesis is this is the result of screwed-up buffer flushing when
the system unexpectedly loses power (with the flushing of corrupted chars
occuring when the system turns back on). When this happens, the last reading
supposed to be logged locally is lost, and if connected, the MySQL database
ends up one entry ahead of the local archive (even though the code to write to
the local file occurs before the database commit). The corrupted bytecode leads
to a bug because python does not read this very well with a standard file()
object, so my readTableFromFile() function locks up. Further, the invariant that
the local archive is always ahead or equal to the MySQL database is violated.
I've thus implemented a hackety workaround, to check the local archive file at
startup for corrupted data and fix it before any other routine attempts to 
read the file. The sync function for the local file and MySQL database can also
handle if this occurs.

NOTE: added feature to dump table as JSON object to the public html folder every
time a reading is added. This is for the live display.

Author: James Chamness
Last modified: June 03, 2017
"""
import Adafruit_DHT
import json
import logging
import MySQLdb
import os
from string import Template
import subprocess
import time

""""Set up logger routing to console and to file"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('ProbeLogger.log', mode='a'))

"""Return a table object read from the given input file.

    Arguments:
    filename -- the filename of the file containing the table to read
    sep -- the delimiter character to expect
    header -- whether or not to skip the first line of the file
"""
def readTableFromFile(filename, sep="\t", header=True):
    try:    
        tableFile = open(filename)
    except IOError:
        print("FILE NOT FOUND: " + filename)
        print("Returning None")
        return None
    table = []
    lineNum = 0
    for line in tableFile:
        lineNum += 1
        if lineNum == 1 and header:
            continue
        vals = line.strip().split(sep)
        table.append(vals)
    return table

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

"""Test sensor connection, log result and terminate script if unsuccessful.

    The test works by trying to take a reading. It will retry up to 15 times,
    with 2 seconds between retries.
    
    Arguments:
    pin -- number of the GPIO pin to which the sensor data cable is connected
"""
def testSensor(pin):
    logger.debug("Initiating probe connection test...    (May take up to 30 seconds)")
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)
    if humidity is not None and temperature is not None:
        logger.debug('Probe connection test successful!')
    else:
        logger.debug("Probe connection test failed: no reading")
        logger.debug("Logger startup terminated")
        quit()

"""Test MySQL db connection. If pass return connection object, else return None.

    If an initial test fails, wait 30 seconds and retry.

    Arguments:
    host,user,passwd,db -- MySQL db parameters provided in configuration file
"""
def testDB(host,user,passwd,db):
    logger.debug("Initiating database connection test... (May take up to 30 seconds)")
    time.sleep(20) # The connection attempt will fail if made immediately. Delay allows MySQL to startup first
    try:
        connection = MySQLdb.connect(host,user,passwd,db)
        logger.debug("Database connection successful!")
        return connection
    except MySQLdb.Error as e:
        logger.debug("Database connection test failed")
        logger.debug("Details:")
        logger.debug(str(e))
        logger.debug("Wait 30 seconds and retry...")
        time.sleep(30)
        try:
            connection = MySQLdb.connect(host,user,passwd,db)
            logger.debug("Database connection successful!")
            return connection
        except MySQLdb.Error as e:
            logger.debug("Database connection test failed again")
            logger.debug("Details:")
            logger.debug(str(e))
            return None

"""Check and fix local archive file for any corrupted binary data at the end.

    This is a bug that occurs when the Pi loses power unexpectedly, e.g. if it
    is just unplugged. Note that it only seems to occur if this script was
    launched from the crontab- if called directly from terminal, doesn't occur.
    
    Arguments:
    localArchiveFilepath -- filepath to the local archive (path + filename)
"""
def bugFixLocal(localArchiveFilepath):
    
    # Determine if there are readings in the table, or just the table stub.
    # This is necessary because Dan's bash one-liner below wipes the table clean
    # (including the header) if there is not at least one real entry. I don't
    # know enough bash to figure out why so this is a hackety workaround
    sysCommandString = "wc -l < " + localArchiveFilepath
    lines = int(subprocess.Popen(sysCommandString,shell=True,stdout=subprocess.PIPE).stdout.read().strip())
    # If just the table stub, no way for there to be bytecode error (since
    # logger must not have been run yet), so return
    if lines == 2: return
        
    # Check for the weird char string and remove if found
    sysCommandString = "tfile='mktemp'; sudo cat -v " + localArchiveFilepath + " | grep -P '^([0-9]+|ID)' > $tfile; sudo mv $tfile " + localArchiveFilepath
    subprocess.call(sysCommandString, shell=True)

"""Test if MySQL db is synced with local archive, and if not, perform sync.

    Basic assumption is that entries are never deleted from either source, and
    are always ordered in the local archive by ID. Determines entries to sync by
    ID. Presumably the local archive is always at or ahead of the MySQL db, but
    if the end-of-file bug occurred, a fix is implemented to import the lost
    reading from the hosted db to the local one.
    
    Arguments:
    localArchiveFilepath -- filepath to the local archive (path + filename)
    cursor -- a MySQLdb cursor object to the relevant database
    table -- the name of the MySQL table to sync
"""
def syncDBwithLocal(localArchiveFilepath, connection, table):
    logger.debug("Testing local archive sync with db...")
    
    # Once determined archive is safe to read as table, do so
    localArchive = readTableFromFile(localArchiveFilepath)
    
    if len(localArchive) == 0:
        logger.debug("WARNING: local archive not initialized")
        logger.debug("Terminating sync routine and ProbeLogger script")
        quit()
    if len(localArchive) == 1:
        logger.debug("Local archive is empty, no sync required!")
        return
    else:
        latestID = max(list(map(lambda x: int(x[0]), localArchive)))
    logger.debug("Local archive latest ID: " + str(latestID))
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM " + table + " ORDER BY ID DESC LIMIT 1", )
    for row in cursor:
        latestIDdb = row[0]
    
    logger.debug("MySQL database latest ID: " + str(latestIDdb))
    diff = latestID - latestIDdb
    
    if diff > 0:
        logger.debug("Syncing " + str(diff) + " local entries to MySQL database...")
        
        for entry in localArchive[latestIDdb+1:]:
            cursor.execute("INSERT INTO " + table + " VALUES (" + entry[0] + "," + entry[1] + "," + entry[2] + ","+ entry[3] + ")" )
    
        connection.commit() # must be called explicitly to make changes to the database
        logger.debug("Entries synced")
    elif diff == 0:
        logger.debug("Already synced")
    elif diff < 0:
        # this block is only reached if there are more MySQL entries than in the local
        # file. this should only ever be 1 or 2, due to the power-off bug
        logger.debug("Applying bugfix...")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM " + table + " ORDER BY ID DESC LIMIT " + str(-diff), )
        f = open(localArchiveFilepath,'a')
        for row in cursor:
            latestIDdb = row[0]
            missingEntryLine = str(row[0]) + "\t" + str(row[1]) + "\t" + str(row[2]) + "\t" + str(row[3]) + "\n"
            f.write(missingEntryLine)
        logger.debug(str(-diff) + " entries synced from MySQL table to local archive.")
        logger.debug("Local archive and database re-synced.")
    else:
        logger.debug("WARNING: SYNC INVARIANT VIOLATED")
        logger.debug("Terminating sync routine and ProbeLogger script")
        quit()

"""Routine to continuously log readings.

    Arguments:
    localArchiveFilepath -- filepath to the local archive (path + filename)
    localOnly -- if True, only record readings to local archive
    pin -- number of the GPIO pin to which the sensor data cable is connected
    w -- measurement frequency, in seconds
"""
def loggerRoutine(localArchiveFilepath, localOnly, pin, connection=None, table=None,w = 30):
    
    if localOnly:
        logger.debug("Launching logger routine in local-only mode")
    else:
        logger.debug("Launching logger routine in standard mode")
        cursor = connection.cursor()
    
    localArchive = readTableFromFile(localArchiveFilepath)
    if len(localArchive) == 0:
        startID = 1
    else:
        startID = max(list(map(lambda x: int(x[0]), localArchive))) + 1
    id = startID
    localFilestream = open(localArchiveFilepath,'a')
    
    jsonFilename = "/var/www/html/data.html"
    
    logger.debug("Logging...")
    
    while(True):
        try:
            ### get reading
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)
            humidity = round(humidity,2)
            temperature = round(temperature,2)
            timestamp = int(time.time())
            
            ### record reading in local archive
            entryString = str(id) + "\t" + str(timestamp) + "\t" + str(temperature) + "\t" + str(humidity) + "\n"
            localFilestream.write(entryString)
            localFilestream.flush()
            
            ### update table and dump as JSON object to file in the public directory of LAMP server
            ### ONLY write most recent 1000 readings (8+ hours of continuous data)
            localArchive.append([str(id),str(timestamp),str(temperature),str(humidity)])
            jsonFilestream = open(jsonFilename,'w')
            if len(localArchive) > 1000:
                json.dump(localArchive[-1000:],jsonFilestream)
            else:
                json.dump(localArchive[1:],jsonFilestream) # skip null entry at beginning
            jsonFilestream.close()
            
            ### update MySQL
            if not localOnly:
                command = Template('INSERT INTO $Table VALUES ($ID, $Time, $Temperature, $Humidity);')
                command = command.substitute(Table=table, ID=id, Time=timestamp, Temperature=temperature, Humidity=humidity)
                cursor.execute(command)
                connection.commit() # must be called explicitly to make changes to the database
            
            # Note the first entry of this batch in the log file
            if id == startID:
                logger.debug("First entry:")
                logger.debug(entryString.strip())
            
            time.sleep(30)
            id += 1
            
        except TypeError:
            if humidity is None or temperature is None:
                logger.debug("Probe reading failed!")
                logger.debug("Initiating ProbeLogger termination...")
                localFilestream.close()
                jsonFilestream.close()
                # Note the final entry of this batch in the log file
                logger.debug("Last entry:")
                logger.debug(entryString)
                logger.debug('ProbeLogger shutdown at ' + str(time.time()))

"""Executable"""
if __name__ == "__main__":
    
    logger.debug('Logger launched at ' + str(time.asctime()))
    
    probeName, unitNumber, pin, host, user, passwd, db, table = loadConf("ProbeLogger.conf")
    localArchiveFilepath = "ProbeLog.csv"
    
    if not os.path.isfile(localArchiveFilepath):
        logger.debug("WARNING: local archive file not found!")
        logger.debug("Terminating sync routine and ProbeLogger script")
        quit()
    
    bugFixLocal(localArchiveFilepath)
    testSensor(pin)
    connection = testDB(host,user,passwd,db)
      
    if connection is None:
        loggerRoutine(localArchiveFilepath, True, pin, w=30)
    else:
        syncDBwithLocal(localArchiveFilepath, connection, table)
        loggerRoutine(localArchiveFilepath, False, pin, connection, table, w=30)
    
