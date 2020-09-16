# -*- coding: utf-8 -*-
from datetime import datetime
import os
import pandas as pd
from common import get_api_repos, get_graphql_data
from writefile import write_text, write_head_contents, write_ranking_repo

class Processor(object):

    def __init__(self):
        # self.languages = ['Python'] # For test
        # self.languages_md = ['Python'] # For test
        self.languages = ["ActionScript","C","CSharp","CPP","Clojure","CoffeeScript","CSS","Go",
                        "Haskell","HTML","Java","JavaScript","Lua","MATLAB","Objective-C","Perl",
                        "PHP","Python","R","Ruby","Scala","Shell","Swift","TeX","Vim-script"]
        self.languages_md = ["ActionScript","C","C\#","C\+\+","Clojure","CoffeeScript","CSS","Go",
                        "Haskell","HTML","Java","JavaScript","Lua","MATLAB","Objective\-C","Perl",
                        "PHP","Python","R","Ruby","Scala","Shell","Swift","TeX","Vim script"]
        # search limit 10 times per minute, with token is 30 per minute
        # check rate_limit with : curl -H "Authorization: token your-access-token" https://api.github.com/rate_limit
        self.api_repo_stars = r'https://api.github.com/search/repositories?q=stars:>0&sort=stars&per_page=100'
        self.api_repo_forks = r'https://api.github.com/search/repositories?q=forks:>0&sort=forks&per_page=100'
        self.api_repo_stars_lang = r'https://api.github.com/search/repositories?q=language:{lang}&stars:>0&sort=stars&per_page=100'

        self.col = ['rank','item','repo_name','stars','forks','language','repo_url','username','issues','last_commit','description']
        self.repos_stars, self.repos_forks, self.repos_languages = self.get_all_repos()

    def get_all_repos(self):
        # get all repos of most stars and forks, and different languages

        print("Get repos of most stars...")
        repos_stars = get_api_repos(self.api_repo_stars)

        print("Get repos of most forks...")
        repos_forks = get_api_repos(self.api_repo_forks)

        repos_languages = {}
        for lang in self.languages:
            print("Get most stars repos of {}...".format(lang))
            repos_languages[lang] = get_api_repos(self.api_repo_stars_lang.format(lang = lang))
        return repos_stars, repos_forks, repos_languages

    def write_head_contents(self):
        write_head_contents('../README.md')

    def write_readme_lang_md(self):
        # Most stars save
        write_text('../README.md','a','\n## Most Stars\n\nThis is top 10 list, for more click **[Github Top 100 Stars](Top100/Top-100-stars.md)**\n\n')
        write_ranking_repo('../README.md','a',self.repos_stars[0:10])
        print("Save most stars in README.md!")
        os.makedirs('../Top100',exist_ok=True)
        write_text('../Top100/Top-100-stars.md','w','[Github Ranking](../README.md)\n==========\n\n## Github Top 100 Stars\n\n')
        write_ranking_repo('../Top100/Top-100-stars.md','a',self.repos_stars)
        print("Save most stars in Top100/Top-100-stars.md!\n")

        # Most forks save
        write_text("../README.md",'a',"## Most Forks\n\nThis is top 10 list, for more click **[Github Top 100 Forks](Top100/Top-100-forks.md)**\n\n")
        write_ranking_repo('../README.md','a',self.repos_forks[0:10])
        print("Save most forks in README.md!")
        write_text('../Top100/Top-100-forks.md','w','[Github Ranking](../README.md)\n==========\n\n## Github Top 100 Forks\n\n')
        write_ranking_repo('../Top100/Top-100-forks.md','a',self.repos_forks)
        print("Save most forks in Top100/Top-100-forks.md!\n")

        # Most stars in language save
        for i in range(len(self.languages)):
            lang = self.languages[i]
            write_text('../README.md','a',"## {}\n\nThis is top 10 list, for more click **[Top 100 Stars in {}](Top100/{}.md)**\n\n".format(self.languages_md[i],self.languages_md[i],lang))
            write_ranking_repo('../README.md','a',self.repos_languages[lang][0:10])
            print("Save most stars of {} in README.md!".format(lang))
            write_text('../Top100/'+lang+'.md','w',"[Github Ranking](../README.md)\n==========\n\n## Top 100 Stars in {}\n\n".format(self.languages_md[i]))
            write_ranking_repo('../Top100/'+lang+'.md','a',self.repos_languages[lang])
            print("Save most stars of {} in Top100/{}.md!\n".format(lang,lang))

    def repo_to_df(self,repos,item):
    # prepare for saving data to csv file
        repos_list = []
        for idx, repo in enumerate(repos):
            repo_info = [idx + 1,item,repo['name'],repo['stargazers_count'],repo['forks_count'],repo['language'],repo['html_url'],repo['owner']['login'],repo['open_issues_count'],repo['pushed_at'],repo['description']]
            repos_list.append(repo_info)
        return pd.DataFrame(repos_list,columns = self.col)

    def save_to_csv(self):
    # save top100 repos info to csv file in Data/github-ranking-year-month-day.md
        df_all = pd.DataFrame(columns=self.col)
        df_repos_stars = self.repo_to_df(self.repos_stars,'top-100-stars')
        df_repos_forks = self.repo_to_df(self.repos_forks,'top-100-forks')
        df_all = df_all.append(df_repos_stars,ignore_index = True)
        df_all = df_all.append(df_repos_forks,ignore_index = True)
        for lang in self.repos_languages.keys():
            df_repos_lang = self.repo_to_df(self.repos_languages[lang],lang)
            df_all = df_all.append(df_repos_lang,ignore_index = True)

        save_date = datetime.utcnow().strftime("%Y-%m-%d")
        os.makedirs('../Data',exist_ok=True)
        df_all.to_csv('../Data/github-ranking-'+save_date+'.csv',index=False,encoding='utf-8')
        print('Save data to Data/github-ranking-'+save_date+'.csv')

class ProcessorGQL(object):

    def __init__(self):
        # self.languages = ["ActionScript","C","CSharp","CPP"] # For test
        # self.languages_md = ["ActionScript","C","C\#","CPP"] # For test
        self.languages = ["ActionScript","C","CSharp","CPP","Clojure","CoffeeScript","CSS","Go",
                        "Haskell","HTML","Java","JavaScript","Lua","MATLAB","Objective-C","Perl",
                        "PHP","Python","R","Ruby","Scala","Shell","Swift","TeX","Vim-script"]
        self.languages_md = ["ActionScript","C","C\#","C\+\+","Clojure","CoffeeScript","CSS","Go",
                        "Haskell","HTML","Java","JavaScript","Lua","MATLAB","Objective\-C","Perl",
                        "PHP","Python","R","Ruby","Scala","Shell","Swift","TeX","Vim script"]
        # use graphql to get data, limit 5000 points per hour
        # check rate_limit with :
        # curl -H "Authorization: bearer your-access-token" -X POST -d "{\"query\": \"{ rateLimit { limit cost remaining resetAt used }}\" }" https://api.github.com/graphql
        self.gql_format = """query{
            search(query: "%s", type: REPOSITORY, first: 100) {
                edges {
                    node {
                        ...on Repository {
                            id
                            name
                            url
                            forkCount
                            stargazers {
                                totalCount
                            }
                            owner {
                                login
                            }
                            issues(states: OPEN) {
                                totalCount
                            }
                            description
                            pushedAt
                            primaryLanguage {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        self.gql_stars = self.gql_format % ("stars:>1000 sort:stars")
        self.gql_forks = self.gql_format % ("forks:>1000 sort:forks")
        self.gql_stars_lang = self.gql_format % ("language:%s stars:>0 sort:stars")

        self.col = ['rank','item','repo_name','stars','forks','language','repo_url','username','issues','last_commit','description']
        self.repos_stars, self.repos_forks, self.repos_languages = self.get_all_repos()

    def parse_gql_result(self,result):
        res = []
        for repo in result["data"]["search"]["edges"]:
            repo_data = repo['node']
            res.append({
                'name': repo_data['name'],
                'stargazers_count': repo_data['stargazers']['totalCount'],
                'forks_count': repo_data['forkCount'],
                'language': repo_data['primaryLanguage']['name'] if repo_data['primaryLanguage'] is not None else None,
                'html_url': repo_data['url'],
                'owner': {
                    'login': repo_data['owner']['login'],
                },
                'open_issues_count': repo_data['issues']['totalCount'],
                'pushed_at': repo_data['pushedAt'],
                'description': repo_data['description'],
            })
        return res

    def get_all_repos(self):
        # get all repos of most stars and forks, and different languages
        print("Get repos of most stars...")
        repos_stars_gql = get_graphql_data(self.gql_stars)
        repos_stars = self.parse_gql_result(repos_stars_gql)

        print("Get repos of most forks...")
        repos_forks_gql = get_graphql_data(self.gql_forks)
        repos_forks = self.parse_gql_result(repos_forks_gql)

        repos_languages = {}
        for lang in self.languages:
            print("Get most stars repos of {}...".format(lang))
            repos_languages[lang] = self.parse_gql_result(
                get_graphql_data(self.gql_stars_lang % (lang))
            )
        return repos_stars, repos_forks, repos_languages

    def write_head_contents(self):
        write_head_contents('../README.md')

    def write_readme_lang_md(self):
        # Most stars save
        write_text('../README.md','a','\n## Most Stars\n\nThis is top 10 list, for more click **[Github Top 100 Stars](Top100/Top-100-stars.md)**\n\n')
        write_ranking_repo('../README.md','a',self.repos_stars[0:10])
        print("Save most stars in README.md!")
        os.makedirs('../Top100',exist_ok=True)
        write_text('../Top100/Top-100-stars.md','w','[Github Ranking](../README.md)\n==========\n\n## Github Top 100 Stars\n\n')
        write_ranking_repo('../Top100/Top-100-stars.md','a',self.repos_stars)
        print("Save most stars in Top100/Top-100-stars.md!\n")

        # Most forks save
        write_text("../README.md",'a',"## Most Forks\n\nThis is top 10 list, for more click **[Github Top 100 Forks](Top100/Top-100-forks.md)**\n\n")
        write_ranking_repo('../README.md','a',self.repos_forks[0:10])
        print("Save most forks in README.md!")
        write_text('../Top100/Top-100-forks.md','w','[Github Ranking](../README.md)\n==========\n\n## Github Top 100 Forks\n\n')
        write_ranking_repo('../Top100/Top-100-forks.md','a',self.repos_forks)
        print("Save most forks in Top100/Top-100-forks.md!\n")

        # Most stars in language save
        for i in range(len(self.languages)):
            lang = self.languages[i]
            write_text('../README.md','a',"## {}\n\nThis is top 10 list, for more click **[Top 100 Stars in {}](Top100/{}.md)**\n\n".format(self.languages_md[i],self.languages_md[i],lang))
            write_ranking_repo('../README.md','a',self.repos_languages[lang][0:10])
            print("Save most stars of {} in README.md!".format(lang))
            write_text('../Top100/'+lang+'.md','w',"[Github Ranking](../README.md)\n==========\n\n## Top 100 Stars in {}\n\n".format(self.languages_md[i]))
            write_ranking_repo('../Top100/'+lang+'.md','a',self.repos_languages[lang])
            print("Save most stars of {} in Top100/{}.md!\n".format(lang,lang))

    def repo_to_df(self,repos,item):
    # prepare for saving data to csv file
        repos_list = []
        for idx, repo in enumerate(repos):
            repo_info = [idx + 1,item,repo['name'],repo['stargazers_count'],repo['forks_count'],repo['language'],repo['html_url'],repo['owner']['login'],repo['open_issues_count'],repo['pushed_at'],repo['description']]
            repos_list.append(repo_info)
        return pd.DataFrame(repos_list,columns = self.col)

    def save_to_csv(self):
    # save top100 repos info to csv file in Data/github-ranking-year-month-day.md
        df_all = pd.DataFrame(columns=self.col)
        df_repos_stars = self.repo_to_df(self.repos_stars,'top-100-stars')
        df_repos_forks = self.repo_to_df(self.repos_forks,'top-100-forks')
        df_all = df_all.append(df_repos_stars,ignore_index = True)
        df_all = df_all.append(df_repos_forks,ignore_index = True)
        for lang in self.repos_languages.keys():
            df_repos_lang = self.repo_to_df(self.repos_languages[lang],lang)
            df_all = df_all.append(df_repos_lang,ignore_index = True)

        save_date = datetime.utcnow().strftime("%Y-%m-%d")
        os.makedirs('../Data',exist_ok=True)
        df_all.to_csv('../Data/github-ranking-'+save_date+'.csv',index=False,encoding='utf-8')
        print('Save data to Data/github-ranking-'+save_date+'.csv')