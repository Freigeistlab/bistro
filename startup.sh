#!/bin/bash
# script to be run at boot of docker container
git pull origin master
python3 -m http.server 8000 &
python3 src/server/bistro.py
