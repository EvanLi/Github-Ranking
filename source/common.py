# -*- coding: utf-8 -*-
import json
import requests
import time

def get_access_token():
    with open('access_token.txt', 'r') as f:
        access_token = f.read().strip()
    return access_token

def get_api_repos(API_URL):
    '''
    get repos of api, return repos list
    '''
    access_token = get_access_token()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'token {}'.format(access_token),
    }
    s = requests.session()
    s.keep_alive = False  # don't keep the session
    time.sleep(3) # not get so fast
    # requests.packages.urllib3.disable_warnings() # disable InsecureRequestWarning of verify=False,
    r = requests.get(API_URL,headers=headers)
    if r.status_code != 200:
        raise ValueError('Can not retrieve from {}'.format(api))
    repos_dict = json.loads(r.content)
    repos = repos_dict['items']
    return repos