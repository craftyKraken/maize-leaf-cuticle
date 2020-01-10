"""A module to interface with the MySQL databases hosted on the GoreLab RasPi's.

The purpose of this module is to retrieve data hosted on each RasPi, and to
sync a local (e.g. on the system from which this script is run) copy of that
data. A design invariant is that data is never deleted from the MySQL databases.

This module is dependent on a configuration file, ProbeDB_auth.conf, containing
each unit-specific IP address and authentication criteria for connecting to each
MySQL database. See the "Raspberry Pi Guide" document for details on how to
ensure this is set up properly.

Also assumes the table always has at least the null first entry (with ID = 0).

VERSION: this version is intended to run on the GoreLab server, and is dependent
on other code on the server to identify the appropriate path in the filesystem
for the table for each unit.

Author:         James Chamness
Last modified:  May 30, 2017
"""

"""Dependencies"""
import logging
import sys
import os
import time
import datetime
import pymysql
from importlib.machinery import SourceFileLoader
Common = SourceFileLoader("Common","../../../pipeline/Common.py").load_module()

""""Set up logger routing to console and to file"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('SyncProbeDBs.log', mode='w'))

"""Return a table object read from the given input file.

    Arguments:
    filename -- the filename of the file containing the table to read
    delimChar -- the delimiter character to expect
    header -- whether or not to skip the first line of the file
"""
def readTableFromFile(filename, delimChar="\t", header=True):
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
        vals = line.strip().split(delimChar)
        table.append(vals)
    return table

"""Write the given table to file.

    No trailing delimiter chars or end of file empty lines.
    Any non-string table entries will be coerced to strings.
    
    Arguments:
    table -- the table to write
    filename -- the filename of the file to write to
    header -- the header for the table to write as the first line
    delim -- delimiter character
    pad -- fill in empty "cells" with NA (based on length of longest entry)
    mode -- file write mode. Default is to overwrite/make new file 
"""
def writeTableToFile(table, filename, header=None, delim="\t", pad=True, mode='w'):
    
    # determine length of longest entry in table:
    maxEntryLength = max(list(map(lambda x: len(x), table)))
    
    out = open(filename, mode)
    if header is not None:
        out.write(header + "\n")
        
    for i in range(0, len(table)-1):
        if len(table[i]) == maxEntryLength:
            for j in range(0,maxEntryLength-1):
                out.write(str(table[i][j]) + delim)
            out.write(str(table[i][maxEntryLength-1]) + "\n")
        else:
            for j in range(0,len(table[i])):
                out.write(str(table[i][j]) + delim)
            for j in range(0,maxEntryLength - len(table[i])-1):
                out.write("NA" + delim)
            out.write("NA" + "\n")
            
    if len(table[-1]) == maxEntryLength:
        for j in range(0,maxEntryLength-1):
            out.write(str(table[-1][j]) + delim)
        out.write(str(table[-1][maxEntryLength-1]) + "\n")
    else:
        for j in range(0,len(table[-1])):
            out.write(str(table[-1][j]) + delim)
        for j in range(0,maxEntryLength - len(table[-1])-1):
            out.write("NA" + delim)
        out.write("NA" + "\n")

    out.close()

"""Read db auth file and return connection info for the given named probe. 

    It is assumed that the db auth file is located in the same directory as this
    script. Returns: (host, user, password, databaseName, tableName)

    Arguments:
    probeName -- e.g. 'probe1', 'probe2', etc.
"""
def _loadAuthConf(probeName):
    dbAuthFilename = "ProbeDB_auth.conf"
    dbAuthFile = open(dbAuthFilename)
    lines = list(map(lambda x: x.strip(), dbAuthFile.readlines()))
    for i in range(0, len(lines)):
        line = lines[i]
        if line == "": continue
        if line[0] == "#": continue
        if line.split(" ")[2] == probeName:
            unitNumber = lines[i+1].split(" ")[2]
            host = lines[i+2].split(" ")[2]
            user = lines[i+3].split(" ")[2]
            pwd = lines[i+4].split(" ")[2]
            db = lines[i+5].split(" ")[2]
            table = lines[i+6].split(" ")[2]
            return (unitNumber, host, user, pwd, db, table)
    logger.debug("WARNING: " + probeName + " not found")
    return None

"""Query a given probe database for new entries and return as an ordered table.

    "New" entries are determined by ID number. Order is by ID. Recall script
    invariant.
    
    Arguments:
    probeName -- e.g. 'probe1', 'probe2', etc. 
"""
def queryNewData(probeName, mostRecentID):
    
    unitNumber, host, user, pwd, db, table = _loadAuthConf(probeName)
    
    try:
        dbConn = pymysql.connect(host=host, user=user, passwd=pwd, db=db)
        cursor = dbConn.cursor()
    except Exception as e:
        logger.debug("Database connection test failed")
        logger.debug("Details:")
        logger.debug(str(e))
        return None
    
    query = ("SELECT * FROM " + table + " WHERE ID > " + str(mostRecentID))
    res = []
    
    cursor.execute(query)
    for row in cursor:
        res.append([row[0],row[1],row[2], row[3]])
    
    return res

"""Sync the local database for a probe with all new entries from the remote one.

    Arguments:
    probeName -- e.g. 'probe1', 'probe2', etc.
    localArchivePath -- path to the directory in which the local tables are (to be) stored 
"""
def update(probeName, localArchivePath):
    
    logger.debug("Initiating update for " + probeName + "...")
    
    unitNumber, host, user, pwd, db, table = _loadAuthConf(probeName)
    
    localArchivePath = localArchivePath + os.sep + "probe" + unitNumber + "_" + probeName + ".csv"
    
    # is this the first ever sync call?
    if not os.path.exists(localArchivePath):
        # if so, get all available data from the database
        queryTable = queryNewData(probeName, 0)
        # if the queryTable is None, there was an error connecting
        if queryTable is None:
            logger.debug("Unable to connect to the database: abandoning sync attempt")
            return
        # if the database is empty, do nothing
        if len(queryTable) == 0:
            logger.debug("No new entries; sync already complete")
            return
        # if not, write the whole table to file with the header
        logger.debug(probeName + ":\t" + str(len(queryTable)) + " new entries synced!")
        header = "ID\tTimestamp\tTemperature\tRH"
        writeTableToFile(queryTable, localArchivePath, header=header)  
    # if this is not the first sync call, determine what needs to be synced
    else:
        currentArchive = readTableFromFile(localArchivePath)
        mostRecentID = max(list(map(lambda x: int(x[0]), currentArchive)))
        #print(mostRecentID)
        # query for any new entries
        queryTable = queryNewData(probeName, mostRecentID)
        # if the queryTable is None, there was an error connecting
        if queryTable is None:
            logger.debug("Unable to connect to the database: abandoning sync attempt")
            return
        # if the database is empty, do nothing
        if len(queryTable) == 0:
            logger.debug("No new entries; sync already complete")
            return
        # if the query is not empty, add these to the local database
        writeTableToFile(queryTable, localArchivePath, mode='a')
        logger.debug(probeName + ":\t" + str(len(queryTable)) + " new entries synced!")
    
    return

"""Executable"""
if __name__ == "__main__":
    
    """
    ============================================================================
    ==== CONFIGURATION
    ============================================================================
    """
    
    localArchivePath = Common.microclimateArchivePath 
    
    """
    ============================================================================
    ==== SYNC
    ============================================================================
    """
    
    logger.debug('SyncProbeDBs launched at ' + str(time.asctime()))
    
    probes = ['rpithon1','rpithon2', 'rpithon3', 'rpithon4', 'rpithon5', 'rpithon6', 'rpithon7']
    
    for probe in probes:
        update(probe, localArchivePath)
    
    logger.debug('SyncProbeDBs shutdown at ' + str(time.asctime()))