#!/usr/bin/python
from configparser import ConfigParser
import os

def config(filename=os.path.dirname(__file__)+'/database.ini', section='galera'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to galera
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]

        print(db)
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
