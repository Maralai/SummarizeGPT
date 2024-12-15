import unittest
import os
import sys
import logging
import tempfile
from unittest.mock import patch, MagicMock
from summarizeGPT.summarizeGPT import (
    summarize_directory,
    get_tree_view,
    get_file_contents,
    setup_logging,
    main,
    logger,
    output_file
)

class TestSummarizeGPT(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w", encoding='utf-8') as f:
            f.write("test content")
        
        # Reset logging before each test
        logger.handlers = []

    def tearDown(self):
        # Clean up temporary files
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_summarize_directory_basic(self):
        """Test basic directory summarization"""
        result = summarize_directory(self.test_dir)
        self.assertIsInstance(result, str)
        self.assertIn(self.test_dir.replace("\\", "/"), result)  # Ensure proper path formatting
        self.assertIn("test.txt", result)

    def test_get_tree_view_basic(self):
        """Test basic tree view generation"""
        tree = get_tree_view(self.test_dir)
        self.assertIsInstance(tree, str)
        self.assertIn("test.txt", tree)

    def test_get_file_contents_basic(self):
        """Test basic file contents retrieval"""
        contents = get_file_contents(self.test_dir)
        self.assertIsInstance(contents, str)
        self.assertIn("test content", contents)

    def test_logging_setup_verbose(self):
        """Test logging configuration with verbose mode"""
        setup_logging(True)
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].level, logging.DEBUG)

    def test_logging_setup_non_verbose(self):
        """Test logging configuration without verbose mode"""
        setup_logging(False)
        self.assertEqual(logger.level, logging.WARNING)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].level, logging.WARNING)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_docker_flags_conflict(self, mock_exit, mock_args):
        """Test handling of conflicting docker flags"""
        # Mock the parsed arguments
        mock_args.return_value = MagicMock(
            directory=self.test_dir,
            gitignore=None,
            include=None,
            exclude=None,
            show_docker=True,
            show_only_docker=True,
            max_lines=None,
            encoding='cl100k_base',
            verbose=False
        )

        with self.assertLogs(logger, level='ERROR') as captured:
            main()
            self.assertIn(
                'ERROR:SummarizeGPT:Cannot use both show_docker and show_only_docker options.',
                captured.output
            )
            mock_exit.assert_called_once_with(1)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_file_write_error(self, mock_exit, mock_args):
        """Test handling of file write errors"""
        # Mock the parsed arguments
        mock_args.return_value = MagicMock(
            directory=self.test_dir,
            gitignore=None,
            include=None,
            exclude=None,
            show_docker=False,
            show_only_docker=False,
            max_lines=None,
            encoding='cl100k_base',
            verbose=False
        )

        # Create a mock that only affects the output file
        original_open = open
        def mock_open_wrapper(*args, **kwargs):
            if args and isinstance(args[0], str) and args[0].endswith(output_file):
                raise IOError("Permission denied")
            return original_open(*args, **kwargs)

        with patch('builtins.open', side_effect=mock_open_wrapper):
            with self.assertLogs(logger, level='ERROR') as captured:
                main()
                self.assertIn(
                    'ERROR:SummarizeGPT:Failed to write output file: Permission denied',
                    captured.output
                )
                mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()