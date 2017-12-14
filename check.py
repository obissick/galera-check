#!/usr/bin/python
import subprocess
import sys
import mysql.connector
from mysql.connector import Error
from config import config


def sleep(time):
    subprocess.call(["sleep "+time], shell=True)

def http_out(message, length, out, exit_code):
    sys.stdout.write(message)
    sys.stdout.write("Content-Type: text/plain\r\n")
    sys.stdout.write("Connection: close\r\n")
    sys.stdout.write("Content-Length: "+length+"\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write(out)
    sleep("0.1")
    exit(exit_code)

def connect(query):
    #""" Connect to the MySQL database server """
    conn = None
    try:
        # read connection parameters
        db_params = config(section='galera')
        # connect to the MySQL server
        conn = mysql.connector.connect(**db_params)
        # create a cursor
        cur = conn.cursor()
        #get node status
        cur.execute(query)
        #save status to variable
        result = cur.fetchone()
        # close the communication with the MySQL
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

    if wsrep_status[1] == "4" or wsrep_status[1] == "2" and opt_params["available_when_donor"] == "1":
        if opt_params["available_when_readonly"] == 0:
            read_only = connect("SHOW GLOBAL VARIABLES LIKE 'read_only';")
            if read_only[1] == "ON":
                http_out("HTTP/1.1 503 Service Unavailable\r\n", "43", "Galera Cluster Node is read-only.\r\n", 1)

        #if status = r then send OK status to HAProxy
        # Shell return-code is 0
        http_out("HTTP/1.1 200 Galera Node is synced.\r\n", "40", "Galera Node is ready.\r\n", 0)

    else:
        #else node in a not in a ready state.
        # Shell return-code is 1
        http_out("HTTP/1.1 503 Galera Node is not synced.\r\n", "44", "Galera Node is not ready.\r\n", 1)

if __name__ == '__main__':
    run()
