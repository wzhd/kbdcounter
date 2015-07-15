#!/usr/bin/env python

import os
import time
from datetime import datetime, timedelta
from optparse import OptionParser
import csv
from xlib import XEvents
from ast import literal_eval
from gi.repository import Gtk, Wnck


class KbdCounter(object):
    def __init__(self, options):
        self.storepath=os.path.expanduser(options.storepath)

        self.set_thishour()
        self.set_nextsave()
        self.read_existing()

        Gtk.init([])  # necessary if not using a Gtk.main() loop
        self.screen = Wnck.Screen.get_default()
        self.screen.force_update()  # recommended per Wnck documentation
        while Gtk.events_pending():  # This is required to capture all existing events
            Gtk.main_iteration()
        self.cur_win = self.screen.get_active_window().get_class_group_name()

    def set_thishour(self):
        self.thishour = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.nexthour = self.thishour + timedelta(hours=1)
        self.thishour_count = {}

    def set_nextsave(self):
        now = time.time()
        self.nextsave = now + min((self.nexthour - datetime.now()).seconds+1, 300)

    def read_existing(self):

        if os.path.exists(self.storepath):
            thishour_repr = self.thishour.strftime("%Y-%m-%dT%H")
            for (hour, value) in csv.reader(open(self.storepath)):
                if hour == thishour_repr:
                    self.thishour_count = literal_eval(value)
                    break
        

    def save(self):
        self.set_nextsave()        
        if len(self.thishour_count) == 0:
            return 
        
        tmpout = csv.writer(open("%s.tmp" % self.storepath, 'w'))
        thishour_repr = self.thishour.strftime("%Y-%m-%dT%H")        

        if os.path.exists(self.storepath):
            for (hour, value) in csv.reader(open(self.storepath)):
                if hour != thishour_repr:
                    tmpout.writerow([hour, value])

        tmpout.writerow([thishour_repr, repr(self.thishour_count)])
        os.rename("%s.tmp" % self.storepath, self.storepath)


    def run(self):
        events = XEvents()
        events.start()
        while not events.listening():
            # Wait for init
            time.sleep(1)

        try:
            while events.listening():
                evt = events.next_event()
                if not evt:
                    time.sleep(0.5)
                    continue
                
                if evt.type != "EV_KEY" or evt.value != 1: # Only count key down, not up.
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
            
        except KeyboardInterrupt:
            events.stop_listening()
            self.save()

            
                    

if __name__ == '__main__':
    oparser = OptionParser()
    oparser.add_option("--storepath", dest="storepath",
                       help="Filename into which number of keypresses per hour is written",
                       default="~/.kbdcounter.csv")

    (options, args) = oparser.parse_args()
    
    kc = KbdCounter(options)
    kc.run()

    

    

    
    
    
