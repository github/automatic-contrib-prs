"""Test cases for the auth module."""

import unittest
from unittest.mock import MagicMock, patch

import auth
import github3


class TestAuthToGitHub(unittest.TestCase):
    """
    Test case for the auth module.
    """

    def test_auth_to_github_with_token(self):
        """
        Test the auth_to_github function when the token is provided.
        """

        result = auth.auth_to_github("", "", b"", "", "token")

        self.assertIsInstance(result, github3.github.GitHub)

    @patch("github3.github.GitHub.login_as_app_installation")
    def test_auth_to_github_with_github_app(self, mock_login):
        """
        Test the auth_to_github function when the token is provided.
        """
        mock_login.return_value = MagicMock()

        result = auth.auth_to_github("12345", "678910", b"hello", "", "")

        self.assertIsInstance(result, github3.github.GitHub)

    def test_auth_to_github_without_token(self):
        """
        Test the auth_to_github function when the token is not provided.
        Expect a ValueError to be raised.
        """
        with self.assertRaises(ValueError) as cm:
            auth.auth_to_github("", "", b"", "", "")
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PRIVATE_KEY] environment variables are not set",
        )

    def test_auth_to_github_with_github_enterprise_url(self):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided.
        """
        result = auth.auth_to_github("", "", b"", "https://github.example.com", "token")

        self.assertIsInstance(result, github3.github.GitHubEnterprise)


if __name__ == "__main__":
    unittest.main()
