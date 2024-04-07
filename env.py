"""
Sets up the environment variables for the action.
"""

import os
from os.path import dirname, join

from dotenv import load_dotenv

MAX_TITLE_LENGTH = 70
MAX_BODY_LENGTH = 65536


def get_int_env_var(env_var_name: str, default: int = -1) -> int | None:
    """Get an integer environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as an integer or None.
    """
    default_place_holder = -1
    env_var = os.environ.get(env_var_name, "")
    if default == default_place_holder and not env_var.strip():
        return None
    try:
        return int(env_var)
    except ValueError:
        return default if default > default_place_holder else None


class EnvVars:
    # pylint: disable=too-many-instance-attributes
    """
    Environment variables

    Attributes:
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for authentication
        gh_token (str | None): GitHub personal access token (PAT) for API authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        gh_actor (str): The GitHub actor to use for authentication
        organization (str): The GitHub organization to use for the PR
        pr_body (str): The PR body to use for the PR
        pr_title (str): The PR title to use for the PR
        repos_json_location (str): The location of the repos.json file
    """

    def __init__(
        self,
        gh_actor: str | None,
        gh_app_id: int | None,
        gh_app_installation_id: int | None,
        gh_app_private_key_bytes: bytes,
        gh_enterprise_url: str | None,
        gh_token: str | None,
        organization: str | None,
        pr_body: str | None,
        pr_title: str | None,
        repos_json_location: str,
    ):
        self.gh_actor = gh_actor
        self.gh_app_id = gh_app_id
        self.gh_app_installation_id = gh_app_installation_id
        self.gh_app_private_key_bytes = gh_app_private_key_bytes
        self.gh_enterprise_url = gh_enterprise_url
        self.gh_token = gh_token
        self.organization = organization
        self.pr_body = pr_body
        self.pr_title = pr_title
        self.repos_json_location = repos_json_location

    def __repr__(self):
        return (
            f"EnvVars("
            f"{self.gh_actor},"
            f"{self.gh_app_id},"
            f"{self.gh_app_installation_id},"
            f"{self.gh_app_private_key_bytes},"
            f"{self.gh_enterprise_url},"
            f"{self.gh_token},"
            f"{self.organization},"
            f"{self.pr_body},"
            f"{self.pr_title},"
            f"{self.repos_json_location})"
        )


def get_env_vars(test: bool = False) -> EnvVars:
    """
    Get the environment variables for use in the action.

    Args:
        test (bool): Whether or not to load the environment variables from a .env file (default: False)

    Returns:
        gh_actor (str): The GitHub actor to use for authentication
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for authentication
        gh_enterprise_url (str): The GitHub Enterprise URL to use for authentication
        gh_token (str | None): The GitHub token to use for authentication
        organization (str): The GitHub organization to use for the PR
        pr_body (str): The PR body to use for the PR
        pr_title (str): The PR title to use for the PR
        repos_json_location (str): The location of the repos.json file
    """
    if not test:
        # Load from .env file if it exists
        dotenv_path = join(dirname(__file__), ".env")
        load_dotenv(dotenv_path)

    gh_actor = os.getenv("GH_ACTOR", "nobody")
    gh_app_id = get_int_env_var("GH_APP_ID")
    gh_app_private_key_bytes = os.environ.get("GH_APP_PRIVATE_KEY", "").encode("utf8")
    gh_app_installation_id = get_int_env_var("GH_APP_INSTALLATION_ID")

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    gh_token = os.getenv("GH_TOKEN")
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not gh_token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    gh_enterprise_url = os.getenv("GH_ENTERPRISE_URL", default="").strip()

    organization = os.getenv("ORGANIZATION")
    if not organization:
        raise ValueError("ORGANIZATION environment variable not set")

    pr_title = os.getenv("PR_TITLE", "chore: Add new CONTRIBUTING.md file")
    # make sure that title is a string with less than 70 characters
    if len(pr_title) > MAX_TITLE_LENGTH:
        raise ValueError("PR_TITLE environment variable is too long. Max 70 characters")

    pr_body = os.getenv(
        "PR_BODY",
        "Add file that specifies the processes and procedures for new contributors to make a new contribution",
    )
    # make sure that body is a string with less than 65536 characters
    if len(pr_body) > MAX_BODY_LENGTH:
        raise ValueError("BODY environment variable is too long. Max 65536 characters")

    repos_json_location = os.getenv("REPOS_JSON_LOCATION", default="repos.json").strip()

    return EnvVars(
        gh_actor,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        gh_enterprise_url,
        gh_token,
        organization,
        pr_body,
        pr_title,
        repos_json_location,
    )
