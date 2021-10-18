#!/usr/bin/env python
""" Automatically open a pull request for repositories that have no CONTRIBUTING.md file """

import json
import os
from os.path import dirname, join
from time import sleep

import github3
from dotenv import load_dotenv

if __name__ == "__main__":

    # Load env variables from file
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    # Auth and identitiy to GitHub.com
    gh = github3.login(token=os.getenv("GH_TOKEN"))
    os.system("git config --global user.name 'GitHub Actions'")
    os.system("git config --global user.email 'no-reply@github.com'")

    # Get innersource repos from organization
    organization = os.getenv("ORGANIZATION")
    gh_actor = os.getenv("GH_ACTOR")
    token = os.getenv("GH_TOKEN")
    REPOS_JSON_LOCATION = "repos.json"
    os.system(f"git clone https://{gh_actor}:{token}@github.com/{REPOS_JSON_LOCATION}")
    repos_file = open(str(REPOS_JSON_LOCATION), "r", encoding="utf-8")
    innersource_repos = json.loads(repos_file.read())

    for repo in innersource_repos:
        print(repo["name"])
        # check if the repo has a contributing.md file
        try:
            if repo["_InnerSourceMetadata"]["guidelines"] == "CONTRIBUTING.md":
                continue
        except KeyError:
            # clone the repo
            repo_full_name = repo["full_name"]
            repo_name = repo["name"]
            os.system(
                f"git clone https://{gh_actor}:{token}@github.com/{repo_full_name}"
            )
            # checkout a branch called contributing-doc
            BRANCH_NAME = "contributing-doc"
            os.chdir(f"{repo_name}")
            os.system(f"git checkout -b {BRANCH_NAME}")
            # copy, customize, and git add the template file
            os.system("cp /action/workspace/CONTRIBUTING-template.md CONTRIBUTING.md")
            os.system(f"sed -i 's/Project-Name/{repo_name}/g' CONTRIBUTING.md")
            os.system("git add CONTRIBUTING.md")
            # git commit that file
            os.system(
                "git commit -m'Request to add a document outlining how to contribute'"
            )
            # git push the branch
            os.system(f"git push -u origin {BRANCH_NAME}")
            # open a PR from that branch to the default branch
            default_branch = repo["default_branch"]
            PR_TITLE = os.getenv("PR_TITLE")
            PR_BODY = os.getenv("PR_BODY")
            # create the pull request
            repository_object = gh.repository(organization, repo_name)
            try:
                repository_object.create_pull(
                    title=PR_TITLE,
                    body=PR_BODY,
                    head=BRANCH_NAME,
                    base=default_branch,
                )
            except github3.exceptions.UnprocessableEntity:
                print("Pull request already exists")
            except github3.exceptions.ForbiddenError:
                print("Pull request failed")
            except github3.exceptions.NotFoundError:
                print("Pull request failed")
            except github3.exceptions.ConnectionError:
                print("Pull request failed")
            except Exception as e:
                print(e)
            # Clean up repository dir
            os.chdir("../")
            os.system(f"rm -rf {repo_name}")

            # rate limit to 20 repos per hour
            print("Waiting 3 minutes so as not to exceed API limits")
            sleep(180)
