#-*- coding:utf-8 -*-
from datetime import datetime
import json
import requests
import os
import pandas as pd

t1 = datetime.now()

def get_access_token():
    with open('access_token.txt', 'r') as f:
        return f.read().strip()

def get_api_repos(api):
    # get repos of api, return repos list
    r = requests.get(api)
    if r.status_code != 200:
        raise ValueError('Can not retrieve from {}'.format(api))
    repos_dict = json.loads(r.content)
    repos = repos_dict['items']
    return repos

def save_ranking(file_name,method,repos):
    # method: 'a'-append or 'w'-overwrite
    table_head = "| Ranking | Project Name | Stars | Forks | Language | Open Issues | Description | Last Commit |\n\
| ------- | ------------ | ----- | ----- | -------- | ----------- | ----------- | ----------- |\n"
    with open(file_name, method, encoding='utf-8') as f:
        f.write(table_head)
        count = 0
        for repo in repos:
            count += 1
            if repo['description'] is not None:
                repo_description = repo['description'].replace('|','\|') #in case there is '|' in description
            f.write('| {} | [{}]({}) | {} | {} | {} | {} | {} | {} |\n'.format(count,
                                                                     repo['name'],
                                                                     repo['html_url'],
                                                                     repo['stargazers_count'],
                                                                     repo['forks_count'],
                                                                     repo['language'],
                                                                     repo['open_issues_count'],
                                                                     repo_description, 
                                                                     repo['pushed_at']))       
        f.write('\n')

def write_text(file_name,method,text):
    with open(file_name, method, encoding='utf-8') as f:
        f.write(text)

def get_all_repos(languages):
    # get all repos of most stars and forks, and different languages
    access_token = get_access_token()
    
    repo_stars_api = 'https://api.github.com/search/repositories?q=stars:>0&sort=stars&per_page=100&access_token={}'.format(access_token)
    repo_forks_api = 'https://api.github.com/search/repositories?q=forks:>0&sort=forks&per_page=100&access_token={}'.format(access_token)
    
    print("Get repos of most stars...")
    repos_stars = get_api_repos(repo_stars_api)
    print("Done!\n")
    
    print("Get repos of most forks...")
    repos_forks = get_api_repos(repo_forks_api)
    print("Done!\n")
    
    repos_languages = {}
    for lang in languages:
        print("Get repos of most stars of {}...".format(lang))
        repo_language_api = 'https://api.github.com/search/repositories?q=language:{}&stars:>0&sort=stars&per_page=100&access_token={}'.format(lang,access_token)
        repos_languages[lang] = get_api_repos(repo_language_api)
        print("Done!\n")
    return repos_stars, repos_forks, repos_languages
    
def write_head_contents():
# write the head and contents of README.md
    write_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    head = "[Github Ranking](./README.md)\n==========\n\n\
**A list of the most github stars and forks repositories.**\n\
\n*Last Automatic Update Time: {}*\n\n".format(write_time)
    contents = '''## Table of Contents\n
* [Most Stars](#most-stars)
* [Most Forks](#most-forks)
* [ActionScript](#actionscript)
* [C](#c)
* [C\#](#c-1)
* [C\+\+](#c-2)
* [Clojure](#clojure)
* [CoffeeScript](#coffeescript)
* [CSS](#css)
* [Go](#go)
* [Haskell](#haskell)
* [HTML](#html)
* [Java](#java)
* [JavaScript](#javascript)
* [Lua](#lua)
* [MATLAB](#matlab)
* [Objective\-C](#objective-c)
* [Perl](#perl)
* [PHP](#php)
* [Python](#python)
* [R](#r)
* [Ruby](#ruby)
* [Scala](#scala)
* [Shell](#shell)
* [Swift](#swift)
* [TeX](#tex)
* [Vim script](#vim-script)\n
'''
    write_text('README.md','w',head+contents)

def write_readme_lang_md(repos_stars, repos_forks, repos_languages,languages,languages_md):
    # Most stars save
    write_text('README.md','a','## Most Stars\n\nThis is top 10 list, for more click **[Github Top 100 Stars](Top100/Top-100-stars.md)**\n\n')
    save_ranking('README.md','a',repos_stars[0:10])
    print("Save most stars in README.md!")
    os.makedirs('Top100',exist_ok=True)
    write_text('Top100/Top-100-stars.md','w','[Github Ranking](../README.md)\n==========\n\n## Github Top 100 Stars\n\n')
    save_ranking('Top100/Top-100-stars.md','a',repos_stars)
    print("Save most stars in Top100/Top-100-stars.md!\n")
    
    # Most forks save
    write_text("README.md",'a',"## Most Forks\n\nThis is top 10 list, for more click **[Github Top 100 Forks](Top100/Top-100-forks.md)**\n\n")
    save_ranking('README.md','a',repos_forks[0:10])
    print("Save most forks in README.md!")
    write_text('Top100/Top-100-forks.md','w','[Github Ranking](../README.md)\n==========\n\n## Github Top 100 Forks\n\n')
    save_ranking('Top100/Top-100-forks.md','a',repos_forks)
    print("Save most forks in Top100/Top-100-forks.md!\n")
    
    # Most stars in language save
    for i in range(len(languages)):
        lang = languages[i]
        write_text('README.md','a',"## {}\n\nThis is top 10 list, for more click **[Top 100 Stars in {}](Top100/{}.md)**\n\n".format(languages_md[i],languages_md[i],lang))
        save_ranking('README.md','a',repos_languages[lang][0:10])
        print("Save most stars of {} in README.md!".format(lang))
        write_text('Top100/'+lang+'.md','w',"[Github Ranking](../README.md)\n==========\n\n## Top 100 Stars in {}\n\n".format(languages_md[i]))
        save_ranking('Top100/'+lang+'.md','a',repos_languages[lang])
        print("Save most stars of {} in Top100/{}.md!\n".format(lang,lang))
    
def repo_to_df(repos,item,col):
# prepare for saving data to csv file
    repos_list = []
    count = 0
    for repo in repos:
        count += 1
        repo_info = [count,item,repo['name'],repo['stargazers_count'],repo['forks_count'],repo['language'],repo['html_url'],repo['owner']['login'],repo['open_issues_count'],repo['pushed_at'],repo['description']]
        repos_list.append(repo_info)
    return pd.DataFrame(repos_list,columns = col)

def save_to_csv(repos_stars,repos_forks,repos_languages):
# save top100 repos info to csv file in Data/github-ranking-year-month-day.md
    col = ['rank','item','repo_name','stars','forks','language','repo_url','username','issues','last_commit','description']
    df_all = pd.DataFrame(columns=col)
    df_repos_stars = repo_to_df(repos_stars,'top-100-stars',col)
    df_repos_forks = repo_to_df(repos_forks,'top-100-forks',col)
    df_all = df_all.append(df_repos_stars,ignore_index = True)
    df_all = df_all.append(df_repos_forks,ignore_index = True)
    for lang in repos_languages.keys():
        df_repos_lang = repo_to_df(repos_languages[lang],lang,col)
        df_all = df_all.append(df_repos_lang,ignore_index = True)
    
    save_date = datetime.utcnow().strftime("%Y-%m-%d")
    os.makedirs('Data',exist_ok=True)
    df_all.to_csv('Data/github-ranking-'+save_date+'.csv',index=False,encoding='utf-8')
    print('Save data to Data/github-ranking-'+save_date+'.csv')

if __name__=="__main__":
    languages = ["ActionScript","C","CSharp","CPP","Clojure","CoffeeScript","CSS","Go","Haskell","HTML","Java","JavaScript","Lua","MATLAB","Objective-C","Perl","PHP","Python","R","Ruby","Scala","Shell","Swift","TeX","Vim-script"]
    languages_md = ["ActionScript","C","C\#","C\+\+","Clojure","CoffeeScript","CSS","Go","Haskell","HTML","Java","JavaScript","Lua","MATLAB","Objective\-C","Perl","PHP","Python","R","Ruby","Scala","Shell","Swift","TeX","Vim script"]
    
    print("Get repos, please wait for seconds...")
    repos_stars, repos_forks, repos_languages = get_all_repos(languages)
    print("Get all repos!\n")
    
    write_head_contents()
    print("Write head and contents of README.md!")
    
    # write to readme and languages.md
    write_readme_lang_md(repos_stars, repos_forks, repos_languages, languages, languages_md)
    
    # Save data to csv file
    save_to_csv(repos_stars,repos_forks,repos_languages)
    
    print("Total time: {}s".format((datetime.now()-t1).total_seconds()))