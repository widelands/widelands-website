#!/usr/bin/env python
# encoding: utf-8

from optparse import OptionParser
import logging

from twisted.internet import reactor

from wlms import MetaServer

def parse_args():
    parser = OptionParser()
    parser.add_option("-d", "--dbfile", default="",
        help="Use flatfile database. File format is 'user\\tpassword\\tpermissions\n'", metavar="DB")
    parser.add_option("-p", "--port", type=int, default=7395,
        help="Listen on this port")
    parser.add_option("-l", "--log", type=str, default="warning",
            help="level of logging. Can be debug, info, warning, error, critical. Warning: if you set this do debug, password might appear in the logfile. [%default]")
    parser.add_option("-f", "--logfile", type=str, default=None,
        help="Logfile to use. Otherwise, logging goes to the console.")

    o, args =  parser.parse_args()

    numeric_level = getattr(logging, o.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
            level=numeric_level, filename=o.logfile)

    return o, args

def main():
    o, args = parse_args()

    if o.dbfile:
        logging.info("Using flat file database.")
        from wlms.db.flatfile import FlatFileDatabase
        db = FlatFileDatabase(open(o.dbfile, "r").read())
    else:
        logging.info("Using django database with settings.py.")
        from wlms.db.djangobridge import DjangoDatabaseBridge
        db = DjangoDatabaseBridge()

    logging.info("Now accepting connections")
    reactor.listenTCP(o.port, MetaServer(db))
    reactor.run()

if __name__ == '__main__':
    main()
