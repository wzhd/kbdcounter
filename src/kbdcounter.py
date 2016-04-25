#!/usr/bin/env python3

import os
import time
import threading
from datetime import datetime, timedelta
from optparse import OptionParser
import csv
from xlib import XEvents
from ast import literal_eval
from gi.repository import Gtk, Wnck
import sqlite3
from record import *

class KbdCounter(object):
    def __init__(self, options):
        self.storepath=os.path.expanduser(options.storepath)
        self.conn = sqlite3.connect(self.storepath)
        self.dbcursor = self.conn.cursor()
        self.initialise_database()

        self.records = []
        self.lastsave = datetime.now()

        Gtk.init([])  # necessary if not using a Gtk.main() loop
        self.screen = Wnck.Screen.get_default()
        self.screen.force_update()  # recommended per Wnck documentation

        self.cur_win = 'Unknown window'
        self.set_current_window()

    def initialise_database(self):
        self.dbcursor.execute('create table if not exists record \
                               (time text, app_name text, code text, scancode text, value text)')

    def save(self):
        # self.set_nextsave()
        for record in self.records:
            self.dbcursor.execute('insert into record \
                                  (time,app_name,code,scancode,value) values \
                                  (?,?,?,?,?)', \
                                  (record.time, record.app_name, record.code, record.scancode, record.value))
        self.records = []
        self.lastsave = datetime.now()
        self.conn.commit()

    def set_current_window(self):
        while Gtk.events_pending():
            # Without this, get_active_window() returns outdated information
            Gtk.main_iteration()
        window = self.screen.get_active_window()
        if window:
            # when switching windows, get_active_window() sometimes returns None
            self.cur_win = window.get_class_group_name()

    def event_handler(self):
        evt = self.events.next_event()
        while(evt):
            if evt.type != "EV_KEY": # Only count key down, not up.
                evt = self.events.next_event()
                continue

            self.set_current_window()

            record = Record()
            record.time = datetime.now().strftime(timeformat)
            record.app_name = self.cur_win
            record.code = evt.get_code()
            record.scancode = evt.get_scancode()
            record.value = evt.get_value()
            self.records.append(record)

            if (datetime.now() - self.lastsave).total_seconds() > 60:
                self.save()

            evt = self.events.next_event()

    def run(self):
        self.events = XEvents()
        event_ready = threading.Event()
        self.events.set_event(event_ready)
        self.events.start()
        while not self.events.listening():
            # Wait for init
            time.sleep(1)
        try:
            while True:
                self.event_handler()
                event_ready.clear()
                event_ready.wait()
        except KeyboardInterrupt:
            self.events.stop_listening()
            self.save()




if __name__ == '__main__':
    oparser = OptionParser()
    oparser.add_option("--storepath", dest="storepath",
                       help="Filename into which number of keypresses per hour is written",
                       default="~/.kbdcounter.db")

    (options, args) = oparser.parse_args()

    kc = KbdCounter(options)
    kc.run()








