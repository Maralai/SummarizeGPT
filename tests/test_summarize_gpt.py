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
        logger = logging.getLogger('SummarizeGPT')
        logger.handlers = []
        logger.setLevel(logging.WARNING)

    def tearDown(self):
        # Clean up temporary files
        os.remove(self.test_file)
        os.rmdir(self.test_dir)

    def test_summarize_directory(self):
        result = summarize_directory(self.test_dir)
        self.assertIsInstance(result, str)
        self.assertIn(self.test_dir, result)
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
        self.assertEqual(logging.getLogger('SummarizeGPT').level, logging.DEBUG)

        # Test non-verbose logging
        setup_logging(False)
        self.assertEqual(logging.getLogger('SummarizeGPT').level, logging.ERROR)

    @patch('sys.argv', ['summarizeGPT', '/tmp/test', '-v'])
    def test_main_with_verbose(self):
        """Test main function with verbose flag"""
        with self.assertRaises(SystemExit) as cm:
            with self.assertLogs('SummarizeGPT', level='ERROR') as log:
                main()
        self.assertEqual(cm.exception.code, 1)
        self.assertTrue(any('Failed to write output file' in r.message for r in log.records))

    @patch('sys.argv', ['summarizeGPT', '/tmp/test'])
    def test_main_without_verbose(self):
        """Test main function without verbose flag"""
        with self.assertRaises(SystemExit) as cm:
            with self.assertLogs('SummarizeGPT', level='ERROR') as log:
                main()
        self.assertEqual(cm.exception.code, 1)
        self.assertTrue(any('Failed to write output file' in r.message for r in log.records))

    def test_main_with_invalid_args(self):
        """Test main function with invalid arguments"""
        with patch('sys.argv', ['summarizeGPT', '/tmp/test', '-d', '-o']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()