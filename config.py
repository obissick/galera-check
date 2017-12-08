#!/usr/bin/python
from configparser import ConfigParser
import os, codecs

def config(filename=os.path.dirname(__file__)+'/database.ini', section='galera'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read_file(codecs.open(filename,"r","utf8"))

    # get section, default to galera
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
	raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db