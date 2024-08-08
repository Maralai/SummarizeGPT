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
            for i in range(5):
                f.write(f'line{i+1}\n')

        # Create a prompt file with the summary
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file)
        prompt_file = os.path.join(self.directory, 'Context_for_ChatGPT.md')
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(summary)
            
    def tearDown(self):
        # Remove the test file after tests
        if os.path.isfile(self.test_file):
            os.remove(self.test_file)

    def test_gitignore(self):
        # Test that .gitignore is working by checking that LICENSE is not in the summary
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file)
        self.assertNotIn('## ./Context_for_ChatGPT.md', summary)

    def test_include(self):
        # Test include and exclude arguments
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file, include_exts=['.md'])
        self.assertIn('python summarize_directory.py', summary) # line from readme should be included
            
    def test_exclude(self):
        # Test exclude argument        
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file, exclude_exts=['.md'])
        self.assertNotIn('python summarize_directory.py', summary)  # README.md should be excluded

    def test_max_lines(self):
        # Test the max_lines argument
        max_lines = 3
        summary = summarize_directory(self.directory, gitignore_file=self.gitignore_file, max_lines=max_lines)
        # Check if the 'testfile.txt' content is truncated to 'max_lines' lines
        self.assertNotIn('line4', summary)
        self.assertNotIn('line5', summary)
    
if __name__ == '__main__':
    unittest.main()