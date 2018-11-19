#!/bin/bash
# script to be run at boot of docker container
# after running this, open:
# http://0.0.0.0:8000/src/frontprojection/bistro.html for frontprojectin
# http://0.0.0.0:8000/src/backprojection/bistro_back.html for backprojection

git pull origin master
python3 -m http.server 8000 &
python3 src/server/bistro.py

