git pull
python save_most_stars_forks.py
git add .
set today=%date:~0,4%-%date:~5,2%-%date:~8,2%
git commit -m "Auto update %today%."
git push origin master
ping 127.0.0.1 -n 6 > nul
