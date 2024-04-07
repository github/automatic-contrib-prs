"""Test the get_env_vars function"""

import os
import unittest
from unittest.mock import patch

from env import EnvVars, get_env_vars

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
        with self.assertRaises(ValueError) as cm:
            get_env_vars()
        the_exception = cm.exception
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
        with self.assertRaises(ValueError) as cm:
            get_env_vars()
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "ORGANIZATION environment variable not set",
        )


if __name__ == "__main__":
    unittest.main()
