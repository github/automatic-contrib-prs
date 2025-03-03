#!/usr/bin/env python
"""Automatically open a pull request for repositories that have no CONTRIBUTING.md file"""

import json
import os
from time import sleep

import auth
import env
import github3


def get_repos_json(gh_actor, repos_json_location, token, endpoint):
    """
    Get the list of repositories from the JSON file.

    Args:
        gh_actor (str): The GitHub actor (username).
        repos_json_location (str): The location of the JSON file containing the repositories.
        token (str): The GitHub personal access token.
        endpoint (str): The GitHub endpoint.

    Returns:
        dict: A dictionary containing the list of repositories.
    """
    os.system(f"git clone https://{gh_actor}:{token}@{endpoint}/{repos_json_location}")
    with open(str(repos_json_location), "r", encoding="utf-8") as repos_file:
        innersource_repos = json.loads(repos_file.read())
    return innersource_repos


def main():  # pragma: no cover
    """
    Automatically open a pull request for repositories that have no CONTRIBUTING.md
    file from a list of repositories in a JSON file
    """
    env_vars = env.get_env_vars()
    gh_actor = env_vars.gh_actor
    organization = env_vars.organization
    pr_body = env_vars.pr_body
    pr_title = env_vars.pr_title
    repos_json_location = env_vars.repos_json_location
    token = env_vars.gh_token
    gh_app_id = env_vars.gh_app_id
    gh_app_installation_id = env_vars.gh_app_installation_id
    gh_app_private_key_bytes = env_vars.gh_app_private_key_bytes
    ghe = env_vars.gh_enterprise_url
    gh_app_enterprise_only = env_vars.gh_app_enterprise_only

    # Auth to GitHub.com
    github_connection = auth.auth_to_github(
        token,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        ghe,
        gh_app_enterprise_only,
    )

    if not token and gh_app_id and gh_app_installation_id and gh_app_private_key_bytes:
        token = auth.get_github_app_installation_token(
            ghe, gh_app_id, gh_app_private_key_bytes, gh_app_installation_id
        )

    endpoint = ghe.removeprefix("https://") if ghe else "github.com"

    os.system("git config --global user.name 'GitHub Actions'")
    os.system(f"git config --global user.email 'no-reply@{endpoint}'")

    # Get innersource repos from organization
    innersource_repos = get_repos_json(gh_actor, repos_json_location, token, endpoint)

    for repo in innersource_repos:
        print(repo["name"])
        # check if the repo has a contributing.md file
        try:
            if repo["_InnerSourceMetadata"]["guidelines"] == "CONTRIBUTING.md":
                continue
        except KeyError:
            # clone the repo
            repo_name = clone_repository(gh_actor, token, endpoint, repo)
            if not repo_name:
                continue

            # checkout a branch called contributing-doc
            branch_name = "contributing-doc"
            os.chdir(f"{repo_name}")
            os.system(f"git checkout -b {branch_name}")

            # copy, customize, and git add the template file
            os.system("cp /action/workspace/CONTRIBUTING-template.md CONTRIBUTING.md")
            os.system(f"sed -i 's/Project-Name/{repo_name}/g' CONTRIBUTING.md")
            os.system("git add CONTRIBUTING.md")
            # git commit that file
            os.system(
                "git commit -m'Request to add a document outlining how to contribute'"
            )
            # git push the branch
            os.system(f"git push -u origin {branch_name}")
            # open a PR from that branch to the default branch
            default_branch = repo["default_branch"]
            # create the pull request
            create_pull_request(
                organization,
                pr_body,
                pr_title,
                github_connection,
                repo_name,
                branch_name,
                default_branch,
            )
            # Clean up repository dir
            os.chdir("../")
            os.system(f"rm -rf {repo_name}")

            # rate limit to 20 repos per hour
            print("Waiting 3 minutes so as not to exceed API limits")
            sleep(180)


def create_pull_request(
    organization,
    pr_body,
    pr_title,
    github_connection,
    repo_name,
    branch_name,
    default_branch,
):
    """Create a pull request."""
    repository_object = github_connection.repository(organization, repo_name)
    try:
        repository_object.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
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


def clone_repository(gh_actor, token, endpoint, repo):
    """Clone the repository and return the name of the repository."""
    repo_full_name = repo["full_name"]
    repo_name = repo["name"]
    try:
        os.system(f"git clone https://{gh_actor}:{token}@{endpoint}/{repo_full_name}")
    except OSError as e:
        print(f"Failed to clone repository: {e}")
        return None
    return repo_name


if __name__ == "__main__":
    main()  # pragma: no cover
