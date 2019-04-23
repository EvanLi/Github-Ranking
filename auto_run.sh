#!/bin/sh
# crontab auto run this file
cd /home/li/code/github/Github-Ranking
git pull
python save_most_stars_forks.py
git add .
today=`date +"%Y-%m-%d"`
git commit -m "Auto update $today."
git push origin master