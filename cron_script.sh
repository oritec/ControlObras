#!/bin/bash

cd /home/andres/ControlObras

workon SaroenGlobal

python dumpDatabase.py
#find /home/andres/ControlObras/backups/ -mtime +10 -type f -delete