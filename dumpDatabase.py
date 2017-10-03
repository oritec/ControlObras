# -*- coding: utf-8 -*-
import subprocess
from datetime import date
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from django.db import connection


if __name__ == '__main__':

    aux = connection.introspection.table_names()
    tables = []
    for t in aux:
        if not t.startswith("django"):
            tables.append(t)

    cmd = 'mysqldump -u root -pcntpasscfg controlobras'
    command = cmd.split() + tables
    fecha = date.today()
    archivo = fecha.strftime("%Y%m%d")
    with open('./backups/' + archivo + '.sql', 'w') as f:
        subprocess.call(command, stdout=f)



