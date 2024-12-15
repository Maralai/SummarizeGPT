import unittest
import os
import sys
import logging
import tempfile
import shutil
from io import StringIO
from unittest.mock import patch, MagicMock
from summarizeGPT.summarizeGPT import (
    summarize_directory,
    setup_logging,
    print_summary,
    main
)

class TestSummarizeGPT(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_files = {
            'test.py': 'print("Hello, World!")',
            'test.txt': 'Hello, World!',
            'Dockerfile': 'FROM python:3.9',
        }
        
        # Create test files
        for filename, content in self.test_files.items():
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)

    def tearDown(self):
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_logging_setup(self):
        """Test logging configuration with different verbosity levels"""
        # Test verbose mode
        setup_logging(verbose=True)
        self.assertEqual(logging.getLogger('SummarizeGPT').level, logging.DEBUG)

        # Test non-verbose mode
        setup_logging(verbose=False)
        self.assertEqual(logging.getLogger('SummarizeGPT').level, logging.ERROR)

    @patch('tiktoken.get_encoding')
    def test_print_summary_with_tokens(self, mock_get_encoding):
        """Test summary printing with token counting"""
        # Mock the token encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [1, 2, 3, 4]  # 4 tokens
        mock_get_encoding.return_value = mock_encoder

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        test_text = "Hello\nWorld"
        print_summary(test_text, encoding_name="cl100k_base")

        # Reset stdout
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Total Lines: 1", output)
        self.assertIn("Approximate Tokens (cl100k_base): 4", output)

    @patch('tiktoken.get_encoding')
    def test_print_summary_with_token_warnings(self, mock_get_encoding):
        """Test token count warnings in verbose mode"""
        # Mock the token encoder for large token count
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [i for i in range(9000)]  # 9000 tokens
        mock_get_encoding.return_value = mock_encoder

        # Setup logging to capture warnings
        setup_logging(verbose=True)
        logger = logging.getLogger('SummarizeGPT')
        with self.assertLogs(logger, level='WARNING') as log:
            print_summary("Test" * 9000, encoding_name="cl100k_base")
            self.assertIn("exceeds GPT-4's context window", log.output[0])

    def test_main_with_verbose(self):
        """Test main function with verbose flag"""
        test_args = [
            'summarizeGPT',
            self.test_dir,
            '--verbose'
        ]
        with patch('sys.argv', test_args):
            with self.assertLogs('SummarizeGPT', level='DEBUG') as log:
                main()
                # Verify that debug messages are present
                self.assertTrue(any(record.levelno == logging.DEBUG for record in log.records))

    def test_main_without_verbose(self):
        """Test main function without verbose flag"""
        test_args = [
            'summarizeGPT',
            self.test_dir
        ]
        with patch('sys.argv', test_args):
            logger = logging.getLogger('SummarizeGPT')
            with self.assertNoLogs(logger, level='WARNING'):
                main()

    @patch('tiktoken.get_encoding')
    def test_different_encodings(self, mock_get_encoding):
        """Test different tiktoken encodings"""
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [1, 2, 3]
        mock_get_encoding.return_value = mock_encoder

        test_args = [
            'summarizeGPT',
            self.test_dir,
            '--encoding',
            'p50k_base'
        ]
        with patch('sys.argv', test_args):
            captured_output = StringIO()
            sys.stdout = captured_output
            main()
            sys.stdout = sys.__stdout__
            
            output = captured_output.getvalue()
            self.assertIn("Approximate Tokens (p50k_base): 3", output)

    def test_unicode_decode_error_handling(self):
        """Test handling of files that can't be decoded with UTF-8"""
        # Create a binary file
        binary_file = os.path.join(self.test_dir, 'binary.bin')
        with open(binary_file, 'wb') as f:
            f.write(b'\x80\x81\x82')

        setup_logging(verbose=True)
        logger = logging.getLogger('SummarizeGPT')
        with self.assertLogs(logger, level='WARNING') as log:
            summarize_directory(self.test_dir)
            self.assertIn("unable to decode with UTF-8 encoding", log.output[0])

    def test_file_write_error_handling(self):
        """Test handling of file write errors"""
        test_args = [
            'summarizeGPT',
            '/nonexistent/directory'  # This should cause a write error
        ]
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()