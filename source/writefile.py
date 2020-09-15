# -*- coding: utf-8 -*-
from datetime import datetime

def write_text(file_name,method,text):
    '''
    write text to file

    method: 'a'-append, 'w'-overwrite
    '''
    with open(file_name, method, encoding='utf-8') as f:
        f.write(text)

def write_head_contents(file_name):
    # write the head and contents of README.md
    # write_head_contents('README.md')
    write_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    head = "*Last Automatic Update Time: {}*\n\n".format(write_time)
    with open('contents.md','r') as f:
        contents = f.read()
    write_text(file_name,'w',head+contents)

def write_ranking_repo(file_name,method,repos):
    # method: 'a'-append or 'w'-overwrite
    table_head = "| Ranking | Project Name | Stars | Forks | Language | Open Issues | Description | Last Commit |\n\
| ------- | ------------ | ----- | ----- | -------- | ----------- | ----------- | ----------- |\n"
    with open(file_name, method, encoding='utf-8') as f:
        f.write(table_head)
        for idx, repo in enumerate(repos):
            repo_description = repo['description']
            if repo_description is not None:
                repo_description = repo_description.replace('|','\|') #in case there is '|' in description
            f.write('| {} | [{}]({}) | {} | {} | {} | {} | {} | {} |\n'.format(
                    idx + 1,
                    repo['name'],
                    repo['html_url'],
                    repo['stargazers_count'],
                    repo['forks_count'],
                    repo['language'],
                    repo['open_issues_count'],
                    repo_description,
                    repo['pushed_at']
                )
            )
        f.write('\n')