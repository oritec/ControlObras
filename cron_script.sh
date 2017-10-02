#!/bin/bash

cd /home/andres/ControlObras

source  /home/andres/Env/SaroenGlobal/bin/activate

python dumpDatabase.py
find /home/andres/ControlObras/backups/ -mtime +30 -type f -delete
