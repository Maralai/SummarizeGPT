import os
import unittest
from summarizeGPT.summarize_directory import summarize_directory

class TestSummarizeDirectory(unittest.TestCase):
    def setUp(self):
        self.directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.gitignore_file = os.path.join(self.directory, '.gitignore')

    def test_gitignore(self):
        # Test that .gitignore is working by checking that LICENSE is not in the summary
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file)
        self.assertNotIn('LICENSE', summary)

    def test_include_exclude(self):
        # Test include and exclude arguments
        summary = summarize_directory(self.directory, include_exts=['.py'])
        self.assertIn('summarize_directory.py', summary)
        self.assertNotIn('README.md', summary)  # README.md should not be included as it's not a .py file

        summary = summarize_directory(self.directory, exclude_exts=['.md'])
        self.assertNotIn('README.md', summary)  # README.md should be excluded


if __name__ == '__main__':
    unittest.main()
