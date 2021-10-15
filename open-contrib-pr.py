#!/usr/bin/env python

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
    REPOS_JSON_LOCATION = os.getenv("REPOS_JSON_LOCATION")
    os.system(
        "git clone https://%s:%s@github.com/%s"
        % (gh_actor, os.getenv("GH_TOKEN"), REPOS_JSON_LOCATION)
    )
    repos_file = open(REPOS_JSON_LOCATION, "r")
    innersource_repos = json.loads(repos_file.read())

    for repo in innersource_repos:
        print(repo["name"])
        # check if the repo has a contributing.md file
        try:
            if repo["_InnerSourceMetadata"]["guidelines"] == "CONTRIBUTING.md":
                continue
        except KeyError:
            # clone the repo
            os.system(
                "git clone https://%s:%s@github.com/%s"
                % (gh_actor, os.getenv("GH_TOKEN"), repo["full_name"])
            )
            # checkout a branch called contributing-doc
            os.chdir("%s" % repo["name"])
            os.system("git checkout -b contributing-doc")
            # copy, customize, and git add the template file
            os.system("cp ../CONTRIBUTING.md .")
            os.system("sed -i 's/Project-Name/%s/g' CONTRIBUTING.md" %
                      repo["name"])
            os.system("git add CONTRIBUTING.md")
            # git commit that file
            os.system(
                "git commit -m'Request to add a document outling how to contribute'")
            # git push -u origin code-scanning
            os.system("git push -u origin contributing-doc")
            # open a PR from that branch to the default branch
            default_branch = repo["default_branch"]
            PR_TITLE = os.getenv("PR_TITLE")
            PR_BODY = os.getenv("PR_BODY")
            # create the pull request
            repository_object = gh.repository(organization, repo["name"])
            try:
                repository_object.create_pull(
                    title=PR_TITLE,
                    body=PR_BODY,
                    head="contributing-doc",
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
            os.system("rm -rf %s" % repo["name"])

            # rate limit to 20 repos per hour
            sleep(180)
