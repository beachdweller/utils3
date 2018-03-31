import os
import unittest

from .. import find_git_repos


class TestFindGitRepositories(unittest.TestCase):
    def test_find_git_repos(self):
        # try to find repositories on the same level as this one
        git_repositories_found = find_git_repos.find_git_repos(os.path.abspath(os.path.join(os.pardir, os.pardir)),
                                                               b_verbose=False)

        expected_set = set()
        sample_file_name = 'test_find_git_repos.txt'
        if not os.path.exists(sample_file_name):
            sample_file_name = os.path.join(sample_file_name)

        with open(sample_file_name, 'rt') as sample_file:
            for item in sample_file:
                expected_set.add(item.strip())

        self.assertSetEqual(expected_set, git_repositories_found.found_set)


if __name__ == '__main__':
    unittest.main()