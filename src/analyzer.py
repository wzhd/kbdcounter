#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from optparse import OptionParser
import csv
import sqlite3

from record import Record

class KbdAnalyzer(object):
    def __init__(self, options):
        self.storepath=os.path.expanduser(options.storepath)
        self.conn = sqlite3.connect(self.storepath)
        self.dbcursor = self.conn.cursor()

        self.records = []
        self.read_existing()

    def read_existing(self):
        records_record = self.dbcursor.execute('select time,app_name,code,scancode,value from record')
        for rec in records_record:
            record = Record()
            record.time = rec[0]
            record.app_name = rec[1]
            record.code = rec[2]
            record.scancode = rec[3]
            record.value = rec[4]
            self.records.append(record)

    def run(self):
        self.read_existing()

if __name__ == '__main__':
    oparser = OptionParser()
    oparser.add_option("--storepath", dest="storepath",
                       help="Filename into which number of keypresses per hour is written",
                       default="~/.kbdcounter.db")

    (options, args) = oparser.parse_args()

    kc = KbdAnalyzer(options)
    kc.run()








