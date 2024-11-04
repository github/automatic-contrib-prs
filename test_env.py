"""Test the get_env_vars function"""

import os
import random
import string
import unittest
from unittest.mock import patch

from env import MAX_BODY_LENGTH, MAX_TITLE_LENGTH, EnvVars, get_env_vars

BODY = "example CONTRIBUTING file contents"
ORGANIZATION = "Organization01"
REPOS_JSON_LOCATION = "repos.json"
TITLE = "New CONTRIBUTING file"
TOKEN = "Token01"


class TestEnv(unittest.TestCase):
    """Test the get_env_vars function"""

    def setUp(self):
        env_keys = [
            "GH_ACTOR",
            "GH_APP_ID",
            "GH_APP_INSTALLATION_ID",
            "GH_APP_PRIVATE_KEY",
            "GITHUB_APP_ENTERPRISE_ONLY",
            "GH_ENTERPRISE_URL",
            "GH_TOKEN",
            "ORGANIZATION",
            "PR_BODY",
            "PR_TITLE",
            "REPOS_JSON_LOCATION",
        ]
        for key in env_keys:
            if key in os.environ:
                del os.environ[key]

    @patch.dict(
        os.environ,
        {
            "GH_ACTOR": "",
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GITHUB_APP_ENTERPRISE_ONLY": "",
            "GH_ENTERPRISE_URL": "",
            "GH_TOKEN": TOKEN,
            "ORGANIZATION": ORGANIZATION,
            "PR_BODY": BODY,
            "PR_TITLE": TITLE,
        },
    )
    def test_get_env_vars_with_token(self):
        """Test that all environment variables are set correctly using a token"""
        expected_result = EnvVars(
            "",
            None,
            None,
            b"",
            False,
            "",
            TOKEN,
            ORGANIZATION,
            BODY,
            TITLE,
            REPOS_JSON_LOCATION,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_ACTOR": "",
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "678910",
            "GH_APP_PRIVATE_KEY": "hello",
            "GITHUB_APP_ENTERPRISE_ONLY": "",
            "GH_ENTERPRISE_URL": "",
            "GH_TOKEN": "",
            "ORGANIZATION": ORGANIZATION,
            "PR_BODY": BODY,
            "PR_TITLE": TITLE,
        },
        clear=True,
    )
    def test_get_env_vars_with_github_app(self):
        """Test that all environment variables are set correctly using github app authentication"""
        expected_result = EnvVars(
            "",
            12345,
            678910,
            b"hello",
            False,
            "",
            "",
            ORGANIZATION,
            BODY,
            TITLE,
            REPOS_JSON_LOCATION,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_ACTOR": "testactor",
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GITHUB_APP_ENTERPRISE_ONLY": "",
            "GH_ENTERPRISE_URL": "testghe",
            "GH_TOKEN": TOKEN,
            "ORGANIZATION": ORGANIZATION,
            "PR_BODY": BODY,
            "PR_TITLE": TITLE,
            "REPOS_JSON_LOCATION": "test/repos.json",
        },
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = EnvVars(
            "testactor",
            None,
            None,
            b"",
            False,
            "testghe",
            TOKEN,
            ORGANIZATION,
            BODY,
            TITLE,
            "test/repos.json",
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(os.environ, {})
    def test_get_env_vars_missing_all_authentication(self):
        """Test that an error is raised if required authentication environment variables are not set"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars()
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "GH_TOKEN environment variable not set",
        )

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": TOKEN,
        },
    )
    def test_get_env_vars_missing_organization(self):
        """Test that an error is raised if required organization environment variables is not set"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars()
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "ORGANIZATION environment variable not set",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_auth_with_github_app_installation_missing_inputs(self):
        """Test that an error is raised when there are missing inputs for the gh app"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "",
            "GH_TOKEN": "test",
        },
        clear=True,
    )
    def test_get_env_vars_no_organization_set(self):
        """Test that an error is raised whenthere are missing inputs for the gh app"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "ORGANIZATION environment variable not set",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "test",
            "PR_TITLE": "".join(
                random.choices(string.ascii_letters, k=MAX_TITLE_LENGTH + 1)
            ),
        },
        clear=True,
    )
    def test_get_env_vars_pr_title_too_long(self):
        """Test that an error is raised when the PR_TITLE env variable has more than MAX_TITLE_LENGTH characters"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            f"PR_TITLE environment variable is too long. Max {MAX_TITLE_LENGTH} characters",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "test",
            "PR_BODY": "".join(
                random.choices(string.ascii_letters, k=MAX_BODY_LENGTH + 1)
            ),
        },
        clear=True,
    )
    def test_get_env_vars_pr_body_too_long(self):
        """Test that an error is raised when the PR_BODY env variable has more than MAX_BODY_LENGTH characters"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            f"BODY environment variable is too long. Max {MAX_BODY_LENGTH} characters",
        )


if __name__ == "__main__":
    unittest.main()
