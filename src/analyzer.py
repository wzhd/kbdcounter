#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
from optparse import OptionParser
import csv
import sqlite3
from collections import defaultdict

from record import *

class KbdAnalyzer(object):
    def __init__(self, options):
        self.options = options
        self.conn = sqlite3.connect(os.path.expanduser(options.storepath))
        self.dbcursor = self.conn.cursor()
        self.records = []

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
        print("read " + str(len(self.records)) + " records")

    def analyze(self):
        keyToTime = {}
        singleCount = defaultdict(int)
        combinedCount = defaultdict(int)

        for rec in self.records:
            if(rec.code[:3] == "BTN"): continue

            if rec.value == "1":
                keyToTime[rec.code] = rec.time
            elif rec.value == "0":
                del keyToTime[rec.code]

            rectime = datetime.strptime(rec.time, timeformat)
            keys = list(keyToTime.keys())
            for key in keys:
                last = datetime.strptime(keyToTime[key], timeformat)
                if (rectime - last).total_seconds() > 60:
                    print("WARNING: ignoring key pressed for longer than 60 seconds: " + key)
                    del keyToTime[key]

            if rec.value == "0":
                singleCount[rec.code] += 1
                if len(keyToTime) > 0:
                    combinedCount[tuple(keyToTime.keys())] += 1

        print("combined")
        sortedCombinedCount = sorted(combinedCount.items(), key=lambda kv: kv[1])
        for item in sortedCombinedCount:
            if(len(item[0]) == 1): continue
            if(self.options.letterCombination == False):
                isLetterCombination = True
                for i in item[0]:
                    if(len(i) > 5):
                        isLetterCombination = False
                        break
                if(isLetterCombination):
                    continue

            print("\t" + str(item[0]) + ": " + str(combinedCount[item[0]]))

        print("single")
        sortedSingleCount = sorted(singleCount.items(), key=lambda kv: kv[1])
        for item in sortedSingleCount:
            print("\t" + str(item[0]) + ": " + str(singleCount[item[0]]))


    def run(self):
        self.read_existing()
        self.analyze()

if __name__ == '__main__':
    oparser = OptionParser()
    oparser.add_option("--storepath", dest="storepath",
                       help="Filename into which number of keypresses per hour is written",
                       default="~/.kbdcounter.db")

    oparser.add_option("--letter-combination", dest="letterCombination",
                       help="Whether simultaneously pressed letters will be treated as combination",
                       default=False)


    (options, args) = oparser.parse_args()

    kc = KbdAnalyzer(options)
    kc.run()








