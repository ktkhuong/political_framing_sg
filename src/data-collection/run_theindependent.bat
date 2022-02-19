@echo off
start cmd

start cmd /k "python theindependent.py -s 0 -e 2000"
start cmd /k "python theindependent.py -s 2000 -e 4000"
start cmd /k "python theindependent.py -s 4000 -e 6000"
start cmd /k "python theindependent.py -s 6000 -e 8000"
start cmd /k "python theindependent.py -s 8000 -e 10000"
start cmd /k "python theindependent.py -s 10000 -e 12000"
start cmd /k "python theindependent.py -s 12000 -e 13103"