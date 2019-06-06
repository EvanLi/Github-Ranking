#!/bin/sh
# crontab auto run this file
echo -e "\n----------Run Time:----------"
date
cd /home/li/code/github/Github-Ranking
git pull
source /home/li/tf36/bin/activate
python save_most_stars_forks.py
git add .
today=`date +"%Y-%m-%d"`
git commit -m "Auto update $today."
git push origin master