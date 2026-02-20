# -*- coding: utf-8 -*-
from datetime import datetime, timezone
import os
import pandas as pd
from common import get_graphql_data, write_text, write_ranking_repo
import inspect

# languages = ['Python']  # For test
# languages_md = ['Python']  # For test
# table_of_contents = """
# * [Python](#python)"""  # For test
languages = ["ActionScript", "C", "CSharp", "CPP", "Clojure", "CoffeeScript", "CSS", "Dart", "DM", "Elixir", "Go", "Groovy", "Haskell", "HTML", "Java",
             "JavaScript", "Julia", "Kotlin", "Lua", "MATLAB", "Objective-C", "Perl", "PHP", "PowerShell", "Python", "R", "Ruby", "Rust", "Scala", "Shell",
             "Swift", "TeX", "TypeScript", "Vim-script"]
# Escape characters in markdown like # + - etc
languages_md = ["ActionScript", "C", "C\#", "C\+\+", "Clojure", "CoffeeScript", "CSS", "Dart", "DM", "Elixir", "Go", "Groovy", "Haskell", "HTML", "Java",
                "JavaScript", "Julia", "Kotlin", "Lua", "MATLAB", "Objective\-C", "Perl", "PHP", "PowerShell", "Python", "R", "Ruby", "Rust", "Scala", "Shell",
                "Swift", "TeX", "TypeScript", "Vim script"]
table_of_contents = """
* [ActionScript](#actionscript)
* [C](#c)
* [C\#](#c-1)
* [C\+\+](#c-2)
* [Clojure](#clojure)
* [CoffeeScript](#coffeescript)
* [CSS](#css)
* [Dart](#dart)
* [DM](#dm)
* [Elixir](#elixir)
* [Go](#go)
* [Groovy](#groovy)
* [Haskell](#haskell)
* [HTML](#html)
* [Java](#java)
* [JavaScript](#javascript)
* [Julia](#julia)
* [Kotlin](#kotlin)
* [Lua](#lua)
* [MATLAB](#matlab)
* [Objective\-C](#objective-c)
* [Perl](#perl)
* [PHP](#php)
* [PowerShell](#powershell)
* [Python](#python)
* [R](#r)
* [Ruby](#ruby)
* [Rust](#rust)
* [Scala](#scala)
* [Shell](#shell)
* [Swift](#swift)
* [TeX](#tex)
* [TypeScript](#typeScript)
* [Vim script](#vim-script)"""


class ProcessorGQL(object):
    """
    Github GraphQL API v4
    ref: https://docs.github.com/en/graphql
    use graphql to get data, limit 5000 points per hour
    check rate_limit with :
    curl -H "Authorization: bearer your-access-token" -X POST -d "{\"query\": \"{ rateLimit { limit cost remaining resetAt used }}\" }" https://api.github.com/graphql
    """

    def __init__(self):
        self.gql_format = """query{
    search(query: "%s", type: REPOSITORY, first:%d %s) {
      pageInfo { endCursor }
                edges {
                    node {
                        ...on Repository {
                            id
                            name
                            url
                            forkCount
                            stargazerCount
                            owner {
                                login
                            }
                            description
                            pushedAt
                            primaryLanguage {
                                name
                            }
                            openIssues: issues(states: OPEN) {
                                totalCount
                            }
                        }
                    }
                }
            }
        }
        """
        self.bulk_size = 50
        self.bulk_count = 2
        self.gql_stars = self.gql_format % ("stars:>1000 sort:stars", self.bulk_size, "%s")
        self.gql_forks = self.gql_format % ("forks:>1000 sort:forks", self.bulk_size, "%s")
        self.gql_stars_lang = self.gql_format % ("language:%s stars:>0 sort:stars", self.bulk_size, "%s")

        self.col = ['rank', 'item', 'repo_name', 'stars', 'forks', 'language', 'repo_url', 'username', 'issues',
                    'last_commit', 'description']

    @staticmethod
    def parse_gql_result(result):
        res = []
        for repo in result["data"]["search"]["edges"]:
            repo_data = repo['node']
            res.append({
                'name': repo_data['name'],
                'stargazers_count': repo_data['stargazerCount'],
                'forks_count': repo_data['forkCount'],
                'language': repo_data['primaryLanguage']['name'] if repo_data['primaryLanguage'] is not None else None,
                'html_url': repo_data['url'],
                'owner': {
                    'login': repo_data['owner']['login'],
                },
                'open_issues_count': repo_data['openIssues']['totalCount'],
                'pushed_at': repo_data['pushedAt'],
                'description': repo_data['description']
            })
        return res

    def get_repos(self, qql):
        cursor = ''
        repos = []
        for i in range(0, self.bulk_count):
            repos_gql = get_graphql_data(qql % cursor)
            cursor = ', after:"' + repos_gql["data"]["search"]["pageInfo"]["endCursor"] + '"'
            repos += self.parse_gql_result(repos_gql)
        return repos

    def get_all_repos(self):
        # get all repos of most stars and forks, and different languages
        print("Get repos of most stars...")
        repos_stars = self.get_repos(self.gql_stars)
        print("Get repos of most stars success!")

        print("Get repos of most forks...")
        repos_forks = self.get_repos(self.gql_forks)
        print("Get repos of most forks success!")

        repos_languages = {}
        for lang in languages:
            print("Get most stars repos of {}...".format(lang))
            repos_languages[lang] = self.get_repos(self.gql_stars_lang % (lang, '%s'))
            print("Get most stars repos of {} success!".format(lang))
        return repos_stars, repos_forks, repos_languages


class WriteFile(object):
    def __init__(self, repos_stars, repos_forks, repos_languages):
        self.repos_stars = repos_stars
        self.repos_forks = repos_forks
        self.repos_languages = repos_languages
        self.col = ['rank', 'item', 'repo_name', 'stars', 'forks', 'language', 'repo_url', 'username', 'issues',
                    'last_commit', 'description']
        self.repo_list = []
        self.repo_list.extend([{
            "desc": "Stars",
            "desc_md": "Stars",
            "title_readme": "Most Stars",
            "title_100": "Top 100 Stars",
            "file_100": "Top-100-stars.md",
            "data": repos_stars,
            "item": "top-100-stars",
        }, {
            "desc": "Forks",
            "desc_md": "Forks",
            "title_readme": "Most Forks",
            "title_100": "Top 100 Forks",
            "file_100": "Top-100-forks.md",
            "data": repos_forks,
            "item": "top-100-forks",
        }])
        for i in range(len(languages)):
            lang = languages[i]
            lang_md = languages_md[i]
            self.repo_list.append({
                "desc": "Forks",
                "desc_md": "Forks",
                "title_readme": lang_md,
                "title_100": f"Top 100 Stars in {lang_md}",
                "file_100": f"{lang}.md",
                "data": repos_languages[lang],
                "item": lang,
            })

    @staticmethod
    def write_head_contents():
        # write the head and contents of README.md
        write_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        head_contents = inspect.cleandoc("""[Github Ranking](./README.md)
            ==========

            **A list of the most github stars and forks repositories.**

            *Last Automatic Update Time: {write_time}*

            ## Sponsor me

            [Buy Me a Coffee | Alipay & WeChat Pay](https://afdian.com/a/EvanLi/plan)

            [afdian 爱发电 EvanLi | 支付宝/微信支付](https://afdian.com/a/EvanLi/plan)

            ## Table of Contents

            * [Most Stars](#most-stars)
            * [Most Forks](#most-forks)""".format(write_time=write_time)) + table_of_contents
        write_text("../README.md", 'w', head_contents)

    def write_readme_lang_md(self):
        os.makedirs('../Top100', exist_ok=True)
        for repo in self.repo_list:
            # README.md
            title_readme, title_100, file_100, data = repo["title_readme"], repo["title_100"], repo["file_100"], repo["data"]
            write_text('../README.md', 'a',
                       f"\n## {title_readme}\n\nThis is top 10, for more click **[{title_100}](Top100/{file_100})**\n\n")
            write_ranking_repo('../README.md', 'a', data[:10])
            print(f"Save {title_readme} in README.md!")

            # Top 100 file
            write_text(f"../Top100/{file_100}", "w",
                       f"[Github Ranking](../README.md)\n==========\n\n## {title_100}\n\n")
            write_ranking_repo(f"../Top100/{file_100}", 'a', data)
            print(f"Save {title_100} in Top100/{file_100}!\n")

    def repo_to_df(self, repos, item):
        # prepare for saving data to csv file
        repos_list = []
        for idx, repo in enumerate(repos):
            repo_info = [idx + 1, item, repo['name'], repo['stargazers_count'], repo['forks_count'], repo['language'],
                         repo['html_url'], repo['owner']['login'], repo['open_issues_count'], repo['pushed_at'],
                         repo['description']]
            repos_list.append(repo_info)
        return pd.DataFrame(repos_list, columns=self.col)

    def save_to_csv(self):
        # save top100 repos info to csv file in Data/github-ranking-year-month-day.md
        df_all = pd.DataFrame(columns=self.col)
        for repo in self.repo_list:
            df_repos = self.repo_to_df(repos=repo["data"], item=repo["item"])
            df_all = df_all.append(df_repos, ignore_index=True)

        save_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        os.makedirs('../Data', exist_ok=True)
        df_all.to_csv('../Data/github-ranking-' + save_date + '.csv', index=False, encoding='utf-8')
        print('Save data to Data/github-ranking-' + save_date + '.csv')


def run_by_gql():
    ROOT_PATH = os.path.abspath(os.path.join(__file__, "../../"))
    os.chdir(os.path.join(ROOT_PATH, 'source'))

    processor = ProcessorGQL()  # use Github GraphQL API v4
    repos_stars, repos_forks, repos_languages = processor.get_all_repos()
    wt_obj = WriteFile(repos_stars, repos_forks, repos_languages)
    wt_obj.write_head_contents()
    wt_obj.write_readme_lang_md()
    wt_obj.save_to_csv()


if __name__ == "__main__":
    t1 = datetime.now()
    run_by_gql()
    print("Total time: {}s".format((datetime.now() - t1).total_seconds()))

