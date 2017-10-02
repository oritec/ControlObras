#!/bin/bash

cd /home/andres/ControlObras

source  /home/andres/Env/SaroenGlobal/bin/activate

python dumpDatabase.py
#find /home/andres/ControlObras/backups/ -mtime +10 -type f -delete