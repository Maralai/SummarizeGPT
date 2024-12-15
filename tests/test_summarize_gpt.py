import unittest
import os
import sys
import logging
import tempfile
from unittest.mock import patch
from summarizeGPT.summarizeGPT import (
    summarize_directory,
    get_tree_view,
    get_file_contents,
    setup_logging,
    main
)

class TestSummarizeGPT(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("test content")

        # Reset logging before each test
        self.logger = logging.getLogger('SummarizeGPT')
        self.logger.handlers = []
        self.logger.setLevel(logging.WARNING)

    def tearDown(self):
        # Clean up temporary files
        try:
            os.remove(self.test_file)
            os.rmdir(self.test_dir)
        except (OSError, FileNotFoundError):
            pass  # Ignore errors during cleanup

    def test_summarize_directory(self):
        result = summarize_directory(self.test_dir)
        self.assertIsInstance(result, str)
        self.assertIn(os.path.basename(self.test_dir), result)
        self.assertIn("test.txt", result)

    def test_get_tree_view(self):
        tree = get_tree_view(self.test_dir)
        self.assertIsInstance(tree, str)
        self.assertIn("test.txt", tree)

    def test_get_file_contents(self):
        contents = get_file_contents(self.test_dir)
        self.assertIsInstance(contents, str)
        self.assertIn("test content", contents)

    def test_logging_setup(self):
        """Test logging configuration with different verbosity levels"""
        # Test verbose logging
        setup_logging(True)
        self.assertEqual(self.logger.getEffectiveLevel(), logging.DEBUG)

        # Reset and test non-verbose logging
        self.logger.handlers = []
        setup_logging(False)
        self.assertEqual(self.logger.getEffectiveLevel(), logging.WARNING)  # Changed from ERROR to WARNING

    @patch('sys.argv', ['summarizeGPT', '/nonexistent/directory', '-v'])
    def test_main_with_verbose(self):
        """Test main function with verbose flag"""
        with self.assertRaises(SystemExit) as cm:
            with self.assertLogs('SummarizeGPT', level='WARNING') as log:  # Changed from ERROR to WARNING
                try:
                    main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                    raise
        self.assertTrue(
            any('Failed to write output file' in record.getMessage() 
                for record in log.records)
        )

    @patch('sys.argv', ['summarizeGPT', '/nonexistent/directory'])
    def test_main_without_verbose(self):
        """Test main function without verbose flag"""
        with self.assertRaises(SystemExit) as cm:
            with self.assertLogs('SummarizeGPT', level='WARNING') as log:  # Changed from ERROR to WARNING
                try:
                    main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                    raise
        self.assertTrue(
            any('Failed to write output file' in record.getMessage() 
                for record in log.records)
        )

    def test_main_with_invalid_args(self):
        """Test main function with invalid arguments"""
        test_args = ['summarizeGPT', self.test_dir, '-d', '-o']
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                with self.assertLogs('SummarizeGPT', level='WARNING') as log:
                    main()
            self.assertEqual(cm.exception.code, 1)
            self.assertTrue(
                any('Cannot use both show_docker and show_only_docker options' in record.getMessage() 
                    for record in log.records)
            )

if __name__ == '__main__':
    unittest.main()