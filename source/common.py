# -*- coding: utf-8 -*-
import requests

def get_access_token():
    with open('../access_token.txt', 'r') as f:
        access_token = f.read().strip()
    return access_token

def write_text(file_name, method, text):
    """
    write text to file
    method: 'a'-append, 'w'-overwrite
    """
    with open(file_name, method, encoding='utf-8') as f:
        f.write(text)

def write_ranking_repo(file_name, method, repos):
    # method: 'a'-append or 'w'-overwrite
    table_head = "| Ranking | Project Name | Stars | Forks | Language | Open Issues | Description | Last Commit |\n\
| ------- | ------------ | ----- | ----- | -------- | ----------- | ----------- | ----------- |\n"
    with open(file_name, method, encoding='utf-8') as f:
        f.write(table_head)
        for idx, repo in enumerate(repos):
            repo_description = repo['description']
            if repo_description is not None:
                repo_description = repo_description.replace('|', '\|')  # in case there is '|' in description
            f.write("| {} | [{}]({}) | {} | {} | {} | {} | {} | {} |\n".format(
                idx + 1, repo['name'], repo['html_url'], repo['stargazers_count'], repo['forks_count'],
                repo['language'], repo['open_issues_count'], repo_description, repo['pushed_at']
            ))
        f.write('\n')

def get_graphql_data(GQL):
    """
    use graphql to get data
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'bearer {}'.format(access_token),
    }
    s = requests.session()
    s.keep_alive = False  # don't keep the session
    graphql_api = "https://api.github.com/graphql"

    r = requests.post(url=graphql_api, json={"query": GQL}, headers=headers, timeout=120)

    if r.status_code != 200:
        raise ValueError('Can not retrieve from {} error: {} '.format(GQL, r.content))

    return r.json()
