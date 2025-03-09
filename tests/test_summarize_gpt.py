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
    discover_gitignore,
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
        self.assertIn(os.path.basename(self.test_dir), result)
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
        mock_args.return_value = type('Args', (), {
            'directory': self.test_dir,
            'gitignore': None,
            'auto_gitignore': False,
            'include': None,
            'exclude': None,
            'show_docker': True,
            'show_only_docker': True,
            'max_lines': None,
            'encoding': 'cl100k_base',
            'verbose': False,
            'tree_depth': None,
            'file_depth': None,
            'max_depth': None  # Added missing attribute
        })()
        
        with patch('logging.Logger.error') as mock_logger:
            main()
            mock_logger.assert_called_once_with(
                'Cannot use both show_docker and show_only_docker options.'
            )
            mock_exit.assert_called_once_with(1)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_file_write_error(self, mock_exit, mock_args):
        """Test handling of file write errors"""
        mock_args.return_value = type('Args', (), {
            'directory': self.test_dir,
            'gitignore': None,
            'auto_gitignore': False,
            'include': None,
            'exclude': None,
            'show_docker': False,
            'show_only_docker': False,
            'max_lines': None,
            'encoding': 'cl100k_base',
            'verbose': False,
            'tree_depth': None,
            'file_depth': None,
            'max_depth': None  # Added missing attribute
        })()

        original_open = open
        def mock_open_wrapper(*args, **kwargs):
            if args and isinstance(args[0], str) and args[0].endswith(output_file):
                raise IOError("Permission denied")
            return original_open(*args, **kwargs)

        with patch('builtins.open', side_effect=mock_open_wrapper):
            with patch('logging.Logger.error') as mock_logger:
                main()
                mock_logger.assert_called_once_with(
                    'Failed to write output file: Permission denied'
                )
                mock_exit.assert_called_once_with(1)

    def test_depth_limiting(self):
        """Test directory depth limiting functionality"""
        # Create a nested directory structure
        nested_dir = os.path.join(self.test_dir, "level1", "level2")
        os.makedirs(nested_dir)
        
        # Create files at different levels
        with open(os.path.join(self.test_dir, "root.txt"), "w") as f:
            f.write("root")
        with open(os.path.join(self.test_dir, "level1", "level1.txt"), "w") as f:
            f.write("level1")
        with open(os.path.join(nested_dir, "level2.txt"), "w") as f:
            f.write("level2")

        # Test with tree_depth=2 to ensure we see one level of nesting
        result = summarize_directory(self.test_dir, tree_depth=2, file_depth=2)
        self.assertIn("root.txt", result)
        self.assertIn("level1", result)
        self.assertIn("level1.txt", result)
        self.assertIn("root", result)  # File content
        self.assertIn("level1", result)  # File content

    def test_depth_edge_cases(self):
        """Test edge cases for depth parameters"""
        nested_dir = os.path.join(self.test_dir, "level1", "level2")
        os.makedirs(nested_dir)
        
        with open(os.path.join(self.test_dir, "root.txt"), "w") as f:
            f.write("root")

        # Test with depth=0
        result = summarize_directory(self.test_dir, tree_depth=0, file_depth=0)
        self.assertIn(os.path.basename(self.test_dir), result)
        
        # Test with unlimited depth
        result = summarize_directory(self.test_dir, tree_depth=None, file_depth=None)
        self.assertIn("root.txt", result)

    def test_separate_tree_and_file_depths(self):
        """Test different depth limits for tree view and file contents"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a nested directory structure
            os.makedirs(os.path.join(tmp_dir, "level1/level2"))
            with open(os.path.join(tmp_dir, "level1/file1.txt"), "w") as f:
                f.write("level1 content")
            with open(os.path.join(tmp_dir, "level1/level2/file2.txt"), "w") as f:
                f.write("level2 content")
                
            result = summarize_directory(tmp_dir, tree_depth=2, file_depth=2)
            
            # Check tree view shows both levels and file contents
            self.assertIn("level1", result)
            self.assertIn("file1.txt", result)
            self.assertIn("level1 content", result)
            self.assertNotIn("level2 content", result)

    def test_discover_gitignore_current_dir(self):
        """Test discovering .gitignore in current directory"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a .gitignore file in the test directory
            gitignore_path = os.path.join(tmp_dir, '.gitignore')
            with open(gitignore_path, 'w') as f:
                f.write("*.tmp\n")
            
            # Test discovery
            with patch('logging.Logger.info') as mock_logger:
                result = discover_gitignore(tmp_dir)
                self.assertEqual(result, gitignore_path)
                mock_logger.assert_called_with(f"Found .gitignore in current directory: {gitignore_path}")

    def test_discover_gitignore_parent_dir(self):
        """Test discovering .gitignore in parent directory"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a nested structure
            child_dir = os.path.join(tmp_dir, 'child')
            os.makedirs(child_dir)
            
            # Create a .gitignore in the parent directory
            gitignore_path = os.path.join(tmp_dir, '.gitignore')
            with open(gitignore_path, 'w') as f:
                f.write("*.tmp\n")
            
            # Test discovery from child directory
            with patch('logging.Logger.info') as mock_logger:
                result = discover_gitignore(child_dir)
                self.assertEqual(result, gitignore_path)
                mock_logger.assert_called_with(f"Found .gitignore in parent directory: {gitignore_path}")

    def test_discover_gitignore_child_dir(self):
        """Test discovering .gitignore in child directory"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a nested structure
            child_dir = os.path.join(tmp_dir, 'child')
            os.makedirs(child_dir)
            
            # Create a .gitignore in the child directory
            gitignore_path = os.path.join(child_dir, '.gitignore')
            with open(gitignore_path, 'w') as f:
                f.write("*.tmp\n")
            
            # Test discovery from parent directory
            with patch('logging.Logger.info') as mock_logger:
                # Patch os.walk to only return our controlled directory structure
                with patch('os.walk') as mock_walk:
                    mock_walk.return_value = [
                        (tmp_dir, ['child'], []),
                        (child_dir, [], ['.gitignore'])
                    ]
                    result = discover_gitignore(tmp_dir)
                    self.assertEqual(result, gitignore_path)
                    mock_logger.assert_called_with(f"Found .gitignore in child directory: {gitignore_path}")

    def test_discover_gitignore_not_found(self):
        """Test behavior when no .gitignore file is found"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('logging.Logger.info') as mock_logger:
                # Patch os.walk and os.path.isfile to ensure no .gitignore is found
                with patch('os.walk') as mock_walk:
                    mock_walk.return_value = [(tmp_dir, [], [])]
                    with patch('os.path.isfile') as mock_isfile:
                        mock_isfile.return_value = False
                        result = discover_gitignore(tmp_dir)
                        self.assertIsNone(result)
                        mock_logger.assert_called_with("No .gitignore file found.")

    @patch('argparse.ArgumentParser.parse_args')
    @patch('summarizeGPT.summarizeGPT.discover_gitignore')
    def test_auto_gitignore_option(self, mock_discover, mock_args):
        """Test the -ig flag for auto-discovering gitignore files"""
        mock_args.return_value = type('Args', (), {
            'directory': self.test_dir,
            'gitignore': None,
            'auto_gitignore': True,
            'include': None,
            'exclude': None,
            'show_docker': False,
            'show_only_docker': False,
            'max_lines': None,
            'encoding': 'cl100k_base',
            'verbose': False,
            'tree_depth': None,
            'file_depth': None,
            'max_depth': None
        })()
        
        # Set up mock to return a fake gitignore path
        mock_discover.return_value = '/mock/path/.gitignore'
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.write = lambda x: None
            with patch('logging.Logger.info') as mock_logger:
                main()
                mock_discover.assert_called_once_with(self.test_dir)
                mock_logger.assert_any_call("Using auto-discovered .gitignore: /mock/path/.gitignore")

    @patch('argparse.ArgumentParser.parse_args')
    def test_explicit_gitignore_precedence(self, mock_args):
        """Test that explicit gitignore takes precedence over auto-discovery"""
        mock_args.return_value = type('Args', (), {
            'directory': self.test_dir,
            'gitignore': '/explicit/path/.gitignore',
            'auto_gitignore': True,
            'include': None,
            'exclude': None,
            'show_docker': False,
            'show_only_docker': False,
            'max_lines': None,
            'encoding': 'cl100k_base',
            'verbose': False,
            'tree_depth': None,
            'file_depth': None,
            'max_depth': None
        })()
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.write = lambda x: None
            with patch('summarizeGPT.summarizeGPT.discover_gitignore') as mock_discover:
                main()
                # Verify discover_gitignore was not called because explicit path was provided
                mock_discover.assert_not_called()

if __name__ == '__main__':
    unittest.main()