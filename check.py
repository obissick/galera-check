#!/usr/bin/python
import mysql.connector
from mysql.connector import Error
from config import config
from socket import gethostname
import subprocess
import os, sys

def sleep(time):
    subprocess.call(["sleep "+time],shell=True)

def httpOut(message,length,out):
    sys.stdout.write(message)
    sys.stdout.write("Content-Type: text/plain\r\n")
    sys.stdout.write("Connection: close\r\n")
    sys.stdout.write("Content-Length: "+length+"\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write(out)
    sleep("0.1")
    exit(0)

def connect(query):
    #""" Connect to the MySQL database server """
    conn = None
    try:
        # read connection parameters
        db_params = config(section='galera')
        # connect to the PostgreSQL server
        conn = mysql.connector.connect(**db_params)
        # create a cursor
        cur = conn.cursor()
        #get node status
        cur.execute(query)
        #save status to variable
        result = cur.fetchone()
        # close the communication with the PostgreSQL
        cur.close()
        return result

    except mysql.connector.Error as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def run():
    opt_params = config(section='options')

    wsrep_status = connect("SHOW STATUS LIKE 'wsrep_local_state';")

    if wsrep_status[0] == "4" or wsrep_status[0] == "2" and opt_params["options"]["available_when_donor"] == "1":
        if opt_params["options"]["available_when_readonly"] == 0:
            read_only = connect("SHOW GLOBAL VARIABLES LIKE 'read_only';")
            if read_only[0] == "ON":
                httpOut("HTTP/1.1 503 Service Unavailable\r\n","43","Galera Cluster Node is read-only.\r\n")

        #if status = r then send OK status to HAProxy
        # Shell return-code is 0
        httpOut("HTTP/1.1 200 Galera Node is synced.\r\n", "40" ,"Galera Node is ready.\r\n")

    else:
        #else node in a not in a ready state.
        # Shell return-code is 1
        httpOut("HTTP/1.1 503 Galera Node is not synced.\r\n", "44" ,"Galera Node is not ready.\r\n")

if __name__ == '__main__':
    run()
