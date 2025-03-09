"""
Command-line interface tests for summarizeGPT.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from summarizeGPT.summarizeGPT import main, output_file


@pytest.fixture
def mock_args():
    """Mock command line arguments."""
    return {
        "directory": "/mock/dir",
        "gitignore": None,
        "auto_gitignore": False,
        "include": None,
        "exclude": None,
        "show_docker": False,
        "show_only_docker": False,
        "max_lines": None,
        "encoding": "cl100k_base",
        "verbose": False,
        "tree_depth": None,
        "file_depth": None,
        "max_depth": None
    }


@patch('argparse.ArgumentParser.parse_args')
@patch('sys.exit')
def test_docker_flags_conflict(mock_exit, mock_parse_args, mock_args, temp_test_directory):
    """Test handling of conflicting docker flags."""
    args = mock_args.copy()
    args["directory"] = temp_test_directory
    args["show_docker"] = True
    args["show_only_docker"] = True
    
    mock_args_obj = MagicMock()
    for key, value in args.items():
        setattr(mock_args_obj, key, value)
    
    mock_parse_args.return_value = mock_args_obj
    
    with patch('logging.Logger.error') as mock_logger:
        main()
        mock_logger.assert_called_once_with(
            'Cannot use both show_docker and show_only_docker options.'
        )
        mock_exit.assert_called_once_with(1)


@patch('argparse.ArgumentParser.parse_args')
@patch('sys.exit')
def test_file_write_error(mock_exit, mock_parse_args, mock_args, temp_test_directory):
    """Test handling of file write errors."""
    args = mock_args.copy()
    args["directory"] = temp_test_directory
    
    mock_args_obj = MagicMock()
    for key, value in args.items():
        setattr(mock_args_obj, key, value)
    
    mock_parse_args.return_value = mock_args_obj

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


@patch('argparse.ArgumentParser.parse_args')
@patch('summarizeGPT.summarizeGPT.discover_gitignore')
def test_auto_gitignore_option(mock_discover, mock_parse_args, mock_args, temp_test_directory):
    """Test the -ig flag for auto-discovering gitignore files."""
    args = mock_args.copy()
    args["directory"] = temp_test_directory
    args["auto_gitignore"] = True
    
    mock_args_obj = MagicMock()
    for key, value in args.items():
        setattr(mock_args_obj, key, value)
    
    mock_parse_args.return_value = mock_args_obj
    
    # Set up mock to return a fake gitignore path
    mock_discover.return_value = '/mock/path/.gitignore'
    
    with patch('builtins.open', create=True) as mock_open:
        # Avoid actually writing files
        mock_open.return_value.__enter__.return_value.write = lambda x: None
        
        with patch('logging.Logger.info') as mock_logger:
            with patch('summarizeGPT.summarizeGPT.print_summary'):
                main()
                mock_discover.assert_called_once_with(temp_test_directory)
                mock_logger.assert_any_call("Using auto-discovered .gitignore: /mock/path/.gitignore")


@patch('argparse.ArgumentParser.parse_args')
def test_explicit_gitignore_precedence(mock_parse_args, mock_args, temp_test_directory):
    """Test that explicit gitignore takes precedence over auto-discovery."""
    args = mock_args.copy()
    args["directory"] = temp_test_directory
    args["gitignore"] = '/explicit/path/.gitignore'
    args["auto_gitignore"] = True
    
    mock_args_obj = MagicMock()
    for key, value in args.items():
        setattr(mock_args_obj, key, value)
    
    mock_parse_args.return_value = mock_args_obj
    
    with patch('builtins.open', create=True) as mock_open:
        # Avoid actually writing files
        mock_open.return_value.__enter__.return_value.write = lambda x: None
        
        with patch('summarizeGPT.summarizeGPT.discover_gitignore') as mock_discover:
            with patch('summarizeGPT.summarizeGPT.print_summary'):
                main()
                # Verify discover_gitignore was not called because explicit path was provided
                mock_discover.assert_not_called()


@patch('subprocess.run')
@patch('argparse.ArgumentParser.parse_args')
def test_basic_integration(mock_parse_args, mock_run, mock_args, temp_test_directory, 
                           sample_file, silence_logging, clean_output_dir):
    """Test basic command-line integration."""
    args = mock_args.copy()
    args["directory"] = temp_test_directory
    args["verbose"] = True
    
    mock_args_obj = MagicMock()
    for key, value in args.items():
        setattr(mock_args_obj, key, value)
    
    mock_parse_args.return_value = mock_args_obj
    
    with patch('summarizeGPT.summarizeGPT.print_summary'):
        with patch('builtins.print'):
            main()
    
    # Check that output file was created
    output_path = os.path.join(temp_test_directory, output_file)
    assert os.path.exists(output_path)
    
    # Verify content
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert os.path.basename(temp_test_directory) in content
        assert "test.txt" in content
        assert "test content" in content