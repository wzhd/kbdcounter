kdbcounter - a program for counting keyboard activity
-----------------------------------------------------

This program will log every keypresses you make on your keyboard
and mouse, on any X Window System environment, for example Linux. 

It will store the log in a SQLite database, by default ~/.kbdcounter.db.

Installation
------------

Required packages, they might have a different name on your system (python should work, too):
- python3-xlib

Run *src/kbdcounter.py*. After 1 minute, verify that it's working by
inspecting ~/.kbdcounter.db (e.g. with sqlitebrowser).

The program should be started automatically when your desktop session
is started. 

Analyzing
---------

Run *src/analyzer.py* to get statistics of the keypresses.
It groups the results to a single mode (counting every release of a key)
or a combined mode (counting how often combinations of keys occur).

The combined mode hides letter-only-combinations per default.
Here an example output:

```
single
	KEY_RETURN: 363
	KEY_D: 392
	KEY_ISO_LEVEL3_SHIFT: 448
	KEY_E: 450
combined
	('KEY_T', 'KEY_SPACE'): 12
	('KEY_SUPER_L', 'KEY_SHIFT_L'): 12
	('KEY_SPACE', 'KEY_F'): 13
	('KEY_ISO_LEVEL3_SHIFT', 'KEY_SPACE'): 19
```

Known bugs
----------

* The program will not save the last minute of stats if it's
  killed. Killing it with Ctrl-C will however save state.

   



