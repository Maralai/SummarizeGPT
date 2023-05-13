import os
import unittest
from SummarizeGPT.SummarizeGPT import summarize_directory

class TestSummarizeDirectory(unittest.TestCase):
    def setUp(self):
        self.directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.gitignore_file = os.path.join(self.directory, '.gitignore')

    def test_gitignore(self):
        # Test that .gitignore is working by checking that LICENSE is not in the summary
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file)
        self.assertNotIn('build.README.md', summary)

    def test_include(self):
        # Test include and exclude arguments
        summary = summarize_directory(self.directory, include_exts=['.md'])
        self.assertIn('python summarize_directory.py', summary)
            
    def test_exclude(self):
        # Test exclude argument        
        summary = summarize_directory(self.directory, exclude_exts=['.md'])
        self.assertNotIn('python summarize_directory.py', summary)  # README.md should be excluded


if __name__ == '__main__':
    unittest.main()
