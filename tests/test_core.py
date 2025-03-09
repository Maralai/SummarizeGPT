"""
Core functionality tests for summarizeGPT.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from summarizeGPT.summarizeGPT import (
    summarize_directory,
    get_tree_view,
    get_file_contents,
    setup_logging,
    discover_gitignore,
    output_file,
    logger
)


def test_summarize_directory_basic(temp_test_directory, sample_file):
    """Test basic directory summarization."""
    result = summarize_directory(temp_test_directory)
    assert os.path.basename(temp_test_directory) in result
    assert "test.txt" in result
    assert "test content" in result


def test_get_tree_view_basic(temp_test_directory, sample_file):
    """Test basic tree view generation."""
    tree = get_tree_view(temp_test_directory)
    assert os.path.basename(temp_test_directory) in tree
    assert "test.txt" in tree


def test_get_file_contents_basic(temp_test_directory, sample_file):
    """Test basic file contents retrieval."""
    contents = get_file_contents(temp_test_directory)
    assert "test content" in contents


def test_tree_view_depth_limiting(nested_directory_structure):
    """Test tree view depth limiting."""
    base_dir = os.path.basename(nested_directory_structure)
    
    # Test with depth=1 (only root)
    tree = get_tree_view(nested_directory_structure, max_depth=1)
    assert f"{base_dir}/" in tree
    assert "root.txt" in tree
    assert "level1.txt" not in tree
    assert "level2.txt" not in tree
    
    # Test with depth=2 (root and level1)
    tree = get_tree_view(nested_directory_structure, max_depth=2)
    assert f"{base_dir}/" in tree
    assert "root.txt" in tree
    assert "level1/" in tree
    assert "level1.txt" in tree
    assert "level2.txt" not in tree
    
    # Test with unlimited depth
    tree = get_tree_view(nested_directory_structure, max_depth=None)
    assert f"{base_dir}/" in tree
    assert "root.txt" in tree
    assert "level1/" in tree
    assert "level1.txt" in tree
    assert "level2/" in tree
    assert "level2.txt" in tree


def test_file_contents_depth_limiting(nested_directory_structure):
    """Test file contents depth limiting."""
    # Test with depth=1 (only root)
    contents = get_file_contents(nested_directory_structure, max_depth=1)
    assert "root content" in contents
    assert "level1 content" not in contents
    assert "level2 content" not in contents
    
    # Test with depth=2 (root and level1)
    contents = get_file_contents(nested_directory_structure, max_depth=2)
    assert "root content" in contents
    assert "level1 content" in contents
    assert "level2 content" not in contents


def test_discover_gitignore_current_dir(gitignore_in_root):
    """Test discovering .gitignore in current directory."""
    temp_dir = os.path.dirname(gitignore_in_root)
    
    with patch('logging.Logger.info') as mock_logger:
        result = discover_gitignore(temp_dir)
        assert result == gitignore_in_root
        mock_logger.assert_called_with(f"Found .gitignore in current directory: {gitignore_in_root}")


def test_discover_gitignore_parent_dir(gitignore_in_root):
    """Test discovering .gitignore in parent directory."""
    temp_dir = os.path.dirname(gitignore_in_root)
    child_dir = os.path.join(temp_dir, "nested")
    os.makedirs(child_dir, exist_ok=True)
    
    with patch('logging.Logger.info') as mock_logger:
        result = discover_gitignore(child_dir)
        assert result == gitignore_in_root
        mock_logger.assert_called_with(f"Found .gitignore in parent directory: {gitignore_in_root}")


def test_discover_gitignore_child_dir(gitignore_in_child):
    """Test discovering .gitignore in child directory."""
    # The parent directory of the .gitignore file in level1
    parent_dir = os.path.dirname(os.path.dirname(gitignore_in_child))
    
    with patch('logging.Logger.info') as mock_logger:
        with patch('os.walk') as mock_walk:
            level1_dir = os.path.dirname(gitignore_in_child)
            mock_walk.return_value = [
                (parent_dir, ["level1"], []),
                (level1_dir, ["level2"], [".gitignore"])
            ]
            result = discover_gitignore(parent_dir)
            assert result == gitignore_in_child
            mock_logger.assert_called_with(f"Found .gitignore in child directory: {gitignore_in_child}")


def test_discover_gitignore_not_found(temp_test_directory):
    """Test behavior when no .gitignore is found."""
    with patch('logging.Logger.info') as mock_logger:
        with patch('os.path.isfile', return_value=False):
            with patch('os.walk', return_value=[(temp_test_directory, [], [])]):
                result = discover_gitignore(temp_test_directory)
                assert result is None
                mock_logger.assert_called_with("No .gitignore file found.")


def test_setup_logging_verbose():
    """Test logging configuration with verbose mode."""
    # Save original logger state
    original_level = logger.level
    original_handlers = logger.handlers.copy()
    
    try:
        # Clear handlers
        logger.handlers = []
        
        setup_logging(True)  # Verbose mode
        assert logger.level == pytest.approx(10)  # DEBUG level
        assert len(logger.handlers) == 1
        assert logger.handlers[0].level == pytest.approx(10)  # DEBUG level
    finally:
        # Restore logger state
        logger.level = original_level
        logger.handlers = original_handlers


def test_setup_logging_non_verbose():
    """Test logging configuration without verbose mode."""
    # Save original logger state
    original_level = logger.level
    original_handlers = logger.handlers.copy()
    
    try:
        # Clear handlers
        logger.handlers = []
        
        setup_logging(False)  # Non-verbose mode
        assert logger.level == pytest.approx(30)  # WARNING level
        assert len(logger.handlers) == 1
        assert logger.handlers[0].level == pytest.approx(30)  # WARNING level
    finally:
        # Restore logger state
        logger.level = original_level
        logger.handlers = original_handlers