#!/bin/bash

cd /home/pi/FlujometrosDMH

if ! pgrep -f "python.*/home/pi/FlujometrosDMH/getData.py"; then
  echo "FLUJOMETROS GET DATA OFF"
  python -u /home/pi/FlujometrosDMH/getData.py &
fi

if ! pgrep -f "python.*/home/pi/FlujometrosDMH/sendDataWeb.py"; then
  echo "FLUJOMETROS sendDataWeb OFF"
  python -u /home/pi/FlujometrosDMH/sendDataWeb.py &
fi
