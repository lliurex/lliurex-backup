#!/bin/bash

xgettext --join-existing ./lliurex-backup/python3-lliurexbackup/MainWindow.py -o ./translations/lliurex-backup.pot
xgettext --join-existing ./lliurex-backup/python3-lliurexbackup/BackupBox.py -o ./translations/lliurex-backup.pot
xgettext --join-existing ./lliurex-backup/python3-lliurexbackup/RestoreBox.py -o ./translations/lliurex-backup.pot
xgettext --join-existing ./lliurex-backup/python3-lliurexbackup/LoginBox.py -o ./translations/lliurex-backup.pot
xgettext --join-existing ./lliurex-backup/python3-lliurexbackup/rsrc/lliurex-backup.ui -o ./translations/lliurex-backup.pot
