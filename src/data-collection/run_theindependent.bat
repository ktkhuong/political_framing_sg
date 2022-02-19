@echo off
start cmd

start cmd /k "python theindependent.py -s 0 -e 400"
start cmd /k "python theindependent.py -s 400 -e 800"
start cmd /k "python theindependent.py -s 801 -e 1200"
start cmd /k "python theindependent.py -s 1201 -e 1600"
start cmd /k "python theindependent.py -s 1601 -e 2000"
start cmd /k "python theindependent.py -s 2001 -e 2231"