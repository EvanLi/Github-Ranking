echo -e "\n----------Run Time:----------"
date
git pull
python source/process.py
git add .
today=`date +"%Y-%m-%d"`
git commit -m "auto update $today"
git push origin master
