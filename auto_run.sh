#!/bin/sh
# crontab auto run this file
# crontab command:
# 0 12 * * * nohup sh /home/kfiry/Github-Ranking/auto_run.sh >> /home/kfirt/tmp/Github-Ranking.log 2>&1 &

echo -e "\n----------Run Time:----------"
date
cd /home/kfiry/Github-Ranking
git pull
python source/process.py
git add .
today=`date +"%Y-%m-%d"`
git commit -m "auto update $today"
git push origin master
