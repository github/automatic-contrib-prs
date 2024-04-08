#!/usr/bin/env python
""" Automatically open a pull request for repositories that have no CONTRIBUTING.md file """

import json
import os
from time import sleep

import auth
import env
import github3

if __name__ == "__main__":
    env_vars = env.get_env_vars()
    gh_actor = env_vars.gh_actor
    organization = env_vars.organization
    pr_body = env_vars.pr_body
    pr_title = env_vars.pr_title
    repos_json_location = env_vars.repos_json_location
    token = env_vars.gh_token

    # Auth to GitHub.com
    github_connection = auth.auth_to_github(
        env_vars.gh_app_id,
        env_vars.gh_app_installation_id,
        env_vars.gh_app_private_key_bytes,
        env_vars.gh_enterprise_url,
        token,
    )

    os.system("git config --global user.name 'GitHub Actions'")
    os.system("git config --global user.email 'no-reply@github.com'")

    # Get innersource repos from organization
    os.system(f"git clone https://{gh_actor}:{token}@github.com/{repos_json_location}")
    with open(str(repos_json_location), "r", encoding="utf-8") as repos_file:
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
            # create the pull request
            repository_object = github_connection.repository(organization, repo_name)
            try:
                repository_object.create_pull(
                    title=pr_title,
                    body=pr_body,
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
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(e)
            # Clean up repository dir
            os.chdir("../")
            os.system(f"rm -rf {repo_name}")

            # rate limit to 20 repos per hour
            print("Waiting 3 minutes so as not to exceed API limits")
            sleep(180)
