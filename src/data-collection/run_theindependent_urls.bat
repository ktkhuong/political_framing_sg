@echo off
start cmd

start cmd /k "python theindependent_urls.py -s 1 -e 400"
start cmd /k "python theindependent_urls.py -s 401 -e 800"
start cmd /k "python theindependent_urls.py -s 801 -e 1200"
start cmd /k "python theindependent_urls.py -s 1201 -e 1600"
start cmd /k "python theindependent_urls.py -s 1601 -e 2000"
start cmd /k "python theindependent_urls.py -s 2001 -e 2231"
rem start cmd /k "python theindependent.py -s 8"
rem start cmd /k "python theindependent.py -s 9"
rem start cmd /k "python theindependent.py -s 10"
rem start cmd /k "python theindependent.py -s 11"
rem start cmd /k "python theindependent.py -s 12"
rem start cmd /k "python theindependent.py -s 13"
rem start cmd /k "python theindependent.py -s 14"