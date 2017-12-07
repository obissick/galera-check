## galera-check ##

Script to make a proxy (ie HAProxy) capable of monitoring PostgreSQL BDR Cluster nodes properly.

## Requirements ##
* xinetd
* python 2.7+
* python-pip
* mysql.connector (install with pip)
* ConfigParser (install with pip)

## Usage ##
Below is a sample configuration for HAProxy on the client. The point of this is that the application will be able to connect to localhost port 3306, so although we are using Galera with several nodes, the application will see this as a single Galera server running on localhost.

`/etc/haproxy/haproxy.cfg`

    ...
    listen Galera-Cluster 0.0.0.0:3306
      balance leastconn
      option httpchk
      mode tcp
        server node1 1.2.3.4:3306 check port 9200 inter 5000 fastinter 2000 rise 2 fall 2
        server node2 1.2.3.5:3306 check port 9200 inter 5000 fastinter 2000 rise 2 fall 2
        server node3 1.2.3.6:3306 check port 9200 inter 5000 fastinter 2000 rise 2 fall 2 backup

Below is a sample config for checker script, this user will be used to check the status of DBR.

`/usr/bin/galera-check/database.ini`

    [galera]
    host=10.1.10.222
    database=mysql
    user=
    password=

    [options]
    available_when_donor=0
    err_file=/dev/null
    available_when_readonly=-1

Galera connectivity is checked via HTTP on port 9200. The check script is a simple Python script which accepts HTTP requests and checks Galera on an incoming request. If the Galera Cluster node is ready to accept requests, it will respond with HTTP code 200 (OK), otherwise a HTTP error 503 (Service Unavailable) is returned.

## Setup with xinetd ##
This setup will create a process that listens on TCP port 9200 using xinetd. This process uses the clustercheck script from this repository to report the status of the node.

First, create a database user that will be doing the checks.

    mysql> GRANT PROCESS ON *.* TO 'clustercheckuser'@'localhost' IDENTIFIED BY 'clustercheckpassword!'

Copy the files from the repository to a location (`/usr/bin` in the example below) and make it executable. Then add the following service to xinetd (make sure to match your location of the script with the 'server'-entry).

`/etc/xinetd.d/mysqlchk`:

    # default: on
    # description: mysqlchk
    service mysqlchk
    {
            disable = no
            flags = REUSE
            socket_type = stream
            port = 9200
            wait = no
            user = nobody
            server = /usr/bin/galera-check/check.py
            log_on_failure += USERID
            only_from = 0.0.0.0/0
            per_source = UNLIMITED
    }

Also, you should add the mysqlchk service to `/etc/services` before restarting xinetd.

    xinetd      9098/tcp    # ...
    mysqlchk    9200/tcp    # Galera check  <--- Add this line
    git         9418/tcp    # Git Version Control System
    zope        9673/tcp    # ...

Clustercheck will now listen on port 9200 after xinetd restart, and HAproxy is ready to check Galera via HTTP poort 9200.
