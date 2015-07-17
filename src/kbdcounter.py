#!/usr/bin/env python

import os
import time
from datetime import datetime, timedelta
from optparse import OptionParser
import csv
from xlib import XEvents
from ast import literal_eval
from gi.repository import Gtk, Wnck
import sqlite3


class KbdCounter(object):
    def __init__(self, options):
        self.storepath=os.path.expanduser(options.storepath)
        conn = sqlite3.connect(self.storepath)
        self.dbcursor = conn.cursor()
        self.initialise_database()

        self.set_thishour()
        self.set_nextsave()
        self.read_existing()

        Gtk.init([])  # necessary if not using a Gtk.main() loop
        self.screen = Wnck.Screen.get_default()
        self.screen.force_update()  # recommended per Wnck documentation
        while Gtk.events_pending():  # This is required to capture all existing events
            Gtk.main_iteration()
        self.cur_win = self.screen.get_active_window().get_class_group_name()

    def initialise_database(self):
        self.dbcursor.execute('create table if not exists record \
                               (time text, app_name text, key_name text, count int, \
                               primary key (time, app_name, key_name))')
    def set_thishour(self):
        self.thishour = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.nexthour = self.thishour + timedelta(hours=1)
        self.thishour_count = {}

    def set_nextsave(self):
        now = time.time()
        self.nextsave = now + min((self.nexthour - datetime.now()).seconds+1, 300)

    def read_existing(self):
        thishour_repr = self.thishour.strftime("%Y-%m-%dT%H")
        thishour_record = self.dbcursor.execute('select app_name,key_name,count \
                                                from record where time=?', (thishour_repr, ))
        for rec in thishour_record:
            self.thishour_count[rec[0]] = {}
            self.thishour_count[rec[0]][rec[1]] == rec[2]

    def save(self):
        self.set_nextsave()
        for app in self.thishour_count:
            for key in self.thishour_count[app]:
                self.dbcursor.execute('insert into record \
                                      (time,app_name,key_name,count) values \
                                      (?,?,?,?)', \
                                      (self.thishour.strftime("%Y-%m-%dT%H"),
                                      app, key, self.thishour_count[app][key]))

    def event_handler(self):
        evt = self.events.next_event()
        while(evt):
            if evt.type != "EV_KEY" or evt.value != 1: # Only count key down, not up.
                evt = self.events.next_event()
                continue

            while Gtk.events_pending():
                # Without this, get_active_window() returns outdated information
                Gtk.main_iteration()
            self.cur_win = self.screen.get_active_window().get_class_group_name()

            self.thishour_count.setdefault(self.cur_win, {})
            self.thishour_count[self.cur_win].setdefault(evt.get_code(), 0)
            self.thishour_count[self.cur_win][evt.get_code()] += 1

            if time.time() > self.nextsave:
                self.save()

                if datetime.now().hour != self.thishour.hour:
                    self.set_thishour()

            evt = self.events.next_event()

    def run(self):
        self.events = XEvents()
        self.events.set_callback(self.event_handler)
        self.events.start()
        while not self.events.listening():
            # Wait for init
            time.sleep(1)
        try:
            # Keep the program from exiting
            while True:
                time.sleep(100)
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

    

    

    
    
    
