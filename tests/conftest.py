import os
import tempfile
import shutil
import pytest
import logging
from pathlib import Path


@pytest.fixture
def temp_test_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_file(temp_test_directory):
    """Create a sample text file in the test directory."""
    file_path = os.path.join(temp_test_directory, "test.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("test content")
    return file_path


@pytest.fixture
def nested_directory_structure(temp_test_directory):
    """Create a nested directory structure with files at different levels."""
    # Create nested structure with files
    level1_dir = os.path.join(temp_test_directory, "level1")
    level2_dir = os.path.join(level1_dir, "level2")
    os.makedirs(level2_dir)
    
    # Create files at different levels
    with open(os.path.join(temp_test_directory, "root.txt"), "w") as f:
        f.write("root content")
    with open(os.path.join(level1_dir, "level1.txt"), "w") as f:
        f.write("level1 content")
    with open(os.path.join(level2_dir, "level2.txt"), "w") as f:
        f.write("level2 content")
    
    return temp_test_directory


@pytest.fixture
def gitignore_in_root(temp_test_directory):
    """Create a .gitignore file in the root directory."""
    gitignore_path = os.path.join(temp_test_directory, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write("*.tmp\n*.log\n")
    return gitignore_path


@pytest.fixture
def gitignore_in_child(nested_directory_structure):
    """Create a .gitignore file in a child directory."""
    level1_dir = os.path.join(nested_directory_structure, "level1")
    gitignore_path = os.path.join(level1_dir, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write("*.cache\n")
    return gitignore_path


@pytest.fixture
def clean_output_dir():
    """Ensure the output directory is clean before and after tests."""
    # Store current working dir
    cwd = os.getcwd()
    
    # Clean up existing output files if they exist
    output_paths = [
        os.path.join(cwd, "Context_for_ChatGPT.md"),
        os.path.join(cwd, "test_ig")
    ]
    
    for path in output_paths:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    
    yield
    
    # Clean up after test
    for path in output_paths:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


@pytest.fixture
def silence_logging():
    """Silence logging during tests."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)