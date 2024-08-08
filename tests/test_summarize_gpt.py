import os
import unittest
from summarizeGPT.summarizeGPT import summarize_directory

class TestSummarizeGPT(unittest.TestCase):
    def setUp(self):
        self.directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.gitignore_file = os.path.join(self.directory, '.gitignore')
        self.test_file = os.path.join(self.directory, 'testfile.txt')
        # Create a test file with known content
        with open(self.test_file, 'w') as f:
            f.write("line1\\nline2\\nline3\\nline4\\nline5\\n")
    
    def tearDown(self):
        # Remove the test file after tests
        if os.path.isfile(self.test_file):
            os.remove(self.test_file)

    def test_gitignore(self):
        # Test that .gitignore is working by checking that LICENSE is not in the summary
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file)
        self.assertNotIn('LICENSE', summary)
    
    def test_include(self):
        # Test include and exclude arguments
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file, include_exts=['.md'])
        self.assertIn('python summarize_directory.py', summary)
    
    def test_exclude(self):
        # Test exclude argument
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file, exclude_exts=['.md'])
        self.assertNotIn('python summarize_directory.py', summary)  # README.md should be excluded
    
    def test_max_lines(self):
        # Test max_lines argument
        max_lines = 3
        summary = summarize_directory(self.directory, max_lines=max_lines)
        file_summary_start = "## {}/testfile.txt\\n".format(self.directory.replace("\\\\", "/"))
        file_summary = "line1\\nline2\\nline3"
        # Check that the file summary in summary includes only max_lines lines
        self.assertIn(file_summary_start, summary)
        self.assertIn(file_summary, summary)
        self.assertNotIn("line4\\nline5", summary)
    
if __name__ == '__main__':
    unittest.main()