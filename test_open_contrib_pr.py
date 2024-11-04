""" Tests for the open_contrib_pr.py functions. """

import unittest
from unittest.mock import MagicMock, mock_open, patch

import github3
from open_contrib_pr import clone_repository, create_pull_request, get_repos_json


class TestOpenContribPR(unittest.TestCase):
    """Test case for the open_contrib_pr module."""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"repos": ["repo1", "repo2"]}',
    )
    @patch("os.system")
    def test_get_repos_json(self, mock_system, mock_file):
        """
        Test the get_repos_json function.
        """
        gh_actor = "test_actor"
        repos_json_location = "test_location"
        token = "test_token"
        endpoint = "test_endpoint"

        expected_repos = {"repos": ["repo1", "repo2"]}

        result = get_repos_json(gh_actor, repos_json_location, token, endpoint)

        mock_system.assert_called_once_with(
            f"git clone https://{gh_actor}:{token}@{endpoint}/{repos_json_location}"
        )
        mock_file.assert_called_once_with(
            str(repos_json_location), "r", encoding="utf-8"
        )
        self.assertEqual(result, expected_repos)


class TestCloneRepository(unittest.TestCase):
    """Test case for the clone_repository function."""

    @patch("os.system")
    def test_clone_repository_success(self, mock_system):
        """
        Test the clone_repository function when the clone is successful.
        """
        mock_system.return_value = 0  # Simulate successful clone

        result = clone_repository(
            gh_actor="test_actor",
            token="test_token",
            endpoint="test_endpoint",
            repo={"full_name": "test_actor/test_repo", "name": "test_repo"},
        )

        mock_system.assert_called_once_with(
            "git clone https://test_actor:test_token@test_endpoint/test_actor/test_repo"
        )
        self.assertEqual(result, "test_repo")

    @patch("os.system")
    def test_clone_repository_failure(self, mock_system):
        """
        Test the clone_repository function when the clone fails.
        """
        mock_system.side_effect = Exception("Clone failed")  # Simulate clone failure

        result = clone_repository(
            gh_actor="test_actor",
            token="test_token",
            endpoint="test_endpoint",
            repo={"full_name": "test_actor/test_repo", "name": "test_repo"},
        )

        mock_system.assert_called_once_with(
            "git clone https://test_actor:test_token@test_endpoint/test_actor/test_repo"
        )
        self.assertIsNone(result)


class TestCreatePullRequest(unittest.TestCase):
    """Test case for the create_pull_request function."""

    def test_create_pull_request_success(self):
        """
        Test the create_pull_request function when the pull request is created successfully.
        """
        github_connection = MagicMock()
        github_connection.repository.return_value = MagicMock()

        create_pull_request(
            organization="test_org",
            pr_body="Test PR body",
            pr_title="Test PR title",
            github_connection=github_connection,
            repo_name="test_repo",
            branch_name="test_branch",
            default_branch="main",
        )

        github_connection.repository.return_value.create_pull.assert_called_once_with(
            title="Test PR title", body="Test PR body", head="test_branch", base="main"
        )

    def test_create_pull_exceptions(self):
        """
        Test the create_pull_request function when an exception occurs.
        """
        github_connection = MagicMock()
        github_connection.repository.return_value = MagicMock()
        for exception, message in [
            (
                github3.exceptions.UnprocessableEntity(MagicMock()),
                "Pull request already exists",
            ),
            (github3.exceptions.ForbiddenError(MagicMock()), "Pull request failed"),
            (github3.exceptions.NotFoundError(MagicMock()), "Pull request failed"),
            (github3.exceptions.ConnectionError(MagicMock()), "Pull request failed"),
        ]:
            github_connection.repository.return_value.create_pull.side_effect = (
                exception
            )
            with patch("builtins.print") as mock_print:
                create_pull_request(
                    organization="test_org",
                    pr_body="Test PR body",
                    pr_title="Test PR title",
                    github_connection=github_connection,
                    repo_name="test_repo",
                    branch_name="test_branch",
                    default_branch="main",
                )
                mock_print.assert_called_once_with(message)


if __name__ == "__main__":
    unittest.main()
