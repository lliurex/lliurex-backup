#!/bin/bash

cp ../install-files/usr/sbin/lliurex-backup  /tmp/lliurex-backup.py

xgettext ../install-files/usr/share/lliurex-backup/rsrc/lliurex-backup.glade /tmp/lliurex-backup.py -o lliurex-backup/lliurex-backup.pot

