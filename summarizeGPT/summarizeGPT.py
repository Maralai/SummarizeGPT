import argparse
import os
import sys
import logging
import gitignore_parser
import tiktoken

output_file = "Context_for_ChatGPT.md"

# Setup logging
logger = logging.getLogger('SummarizeGPT')

def discover_gitignore(directory):
    """
    Auto-discover the nearest .gitignore file with the following search priority:
    1. Current directory
    2. Parent directories (up the tree)
    3. Child directories (down the tree)
    
    Args:
        directory (str): The starting directory for the search
        
    Returns:
        str or None: Path to the discovered .gitignore file, or None if not found
    """
    # Normalize directory path
    directory = os.path.abspath(directory)
    
    # 1. Check current directory
    current_gitignore = os.path.join(directory, '.gitignore')
    if os.path.isfile(current_gitignore):
        logger.info(f"Found .gitignore in current directory: {current_gitignore}")
        return current_gitignore
    
    # 2. Check parent directories (up)
    parent_dir = os.path.dirname(directory)
    while parent_dir and parent_dir != directory:
        parent_gitignore = os.path.join(parent_dir, '.gitignore')
        if os.path.isfile(parent_gitignore):
            logger.info(f"Found .gitignore in parent directory: {parent_gitignore}")
            return parent_gitignore
        directory = parent_dir  # Move up one level
        parent_dir = os.path.dirname(directory)
    
    # 3. Check child directories (down)
    for root, dirs, files in os.walk(directory):
        if '.gitignore' in files:
            child_gitignore = os.path.join(root, '.gitignore')
            logger.info(f"Found .gitignore in child directory: {child_gitignore}")
            return child_gitignore
    
    logger.info("No .gitignore file found.")
    return None

def setup_logging(verbose):
    """Configure logging based on verbosity level"""
    level = logging.DEBUG if verbose else logging.WARNING
    logger.setLevel(level)

    # Clear any existing handlers
    logger.handlers = []
    
    # Create console handler with appropriate formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def summarize_directory(directory, gitignore_file=None, include_exts=None, 
                       exclude_exts=None, show_docker=False, show_only_docker=False, 
                       max_lines=None, tree_depth=None, file_depth=None):
    directory = directory.replace("\\", "/")
    prompt_md = f"# Summary of directory: {directory}\n\n"
    tree_view = get_tree_view(directory, gitignore_file=gitignore_file, max_depth=tree_depth)
    prompt_md += "```\n" + tree_view + "\n```\n\n"
    file_contents = get_file_contents(directory, gitignore_file, include_exts, 
                                    exclude_exts, show_docker=show_docker,
                                    show_only_docker=show_only_docker, 
                                    max_lines=max_lines, max_depth=file_depth)
    prompt_md += file_contents
    return prompt_md

def get_tree_view(directory, gitignore_file=None, max_depth=None):
    tree_view = ""
    if gitignore_file:
        gitignore = gitignore_parser.parse_gitignore(gitignore_file)
    else:
        gitignore = None

    for root, dirs, files in os.walk(directory):
        if '.git' in root:
            continue
            
        level = root.replace(directory, '').count(os.sep) + 1  # +1 because root is level 1
        
        # Skip if we've exceeded the maximum depth
        if max_depth is not None and level > max_depth:
            dirs[:] = []  # Clear dirs to prevent further recursion
            continue
            
        if gitignore:
            dirs[:] = [d for d in dirs if not gitignore(os.path.join(root, d))]
            files = [f for f in files if not gitignore(os.path.join(root, f))]
            
        indent = ' ' * 4 * (level - 1)  # Adjust indent because level starts at 1
        tree_view += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = ' ' * 4 * level
        for file in files:
            if file == output_file:
                continue
            tree_view += f"{sub_indent}{file}\n"
    return tree_view

def get_file_contents(directory, gitignore_file=None, include_exts=None, 
                     exclude_exts=None, show_docker=False, show_only_docker=False, 
                     max_lines=None, max_depth=None):
    file_contents = ""
    excluded_files = ['docker', 'Dockerfile']
    if gitignore_file:
        gitignore = gitignore_parser.parse_gitignore(gitignore_file)
    else:
        gitignore = None

    for root, _, files in os.walk(directory):
        if '.git' in root:
            continue
        level = root.replace(directory, '').count(os.sep) + 1  # +1 because root is level 1
        # Skip if we've exceeded the maximum depth
        if max_depth is not None and level > max_depth:
            continue
        if gitignore:
            files = [f for f in files if not gitignore(os.path.join(root, f))]
        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower()  # Make the check case-insensitive
            if include_exts is not None and ext not in include_exts:
                continue
            if exclude_exts is not None and ext in exclude_exts:
                continue
            if not show_docker and not show_only_docker:
                if file.lower().endswith(('.env', 'license', 'gitignore', 'setup.py', '__init__.py', 'test_summarize_gpt.py')) or any(substring in file.lower() for substring in excluded_files):
                    continue
            elif show_only_docker:
                if not any(substring in file.lower() for substring in ['docker', 'Dockerfile', 'requirements.txt']):
                    continue

            if file == output_file:
                continue
            file_path = os.path.join(root, file).replace("\\", "/")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    contents = f.readlines()
                    if max_lines is not None:
                        contents = contents[:max_lines]
                    contents = ''.join(contents)
                    file_contents += f"## {file_path}\n\n```\n{remove_empty_lines(contents)}\n```\n\n"
            except UnicodeDecodeError:
                logger.warning(f"Skipping file {file_path}: unable to decode with UTF-8 encoding.")
    return file_contents

def remove_empty_lines(text):
    return "\n".join([line for line in text.split("\n") if line.strip()])

def print_summary(summary, encoding_name="cl100k_base"):
    # Get token count using tiktoken
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        token_count = len(encoding.encode(summary))
    except Exception as e:
        logger.error(f"Could not count tokens: {str(e)}")
        token_count = None

    total_lines = summary.count('\n')
    total_chars = len(summary)
    total_bytes = sys.getsizeof(summary.encode('utf-8'))
    
    print("\nSummary Statistics:")
    print(f"Total Lines: {total_lines}")
    print(f"Total Characters: {total_chars}")
    print(f"Total Bytes: {total_bytes}")
    
    if token_count is not None:
        print(f"Approximate Tokens ({encoding_name}): {token_count}")
    
    print()  # Empty line for spacing

def main():
    parser = argparse.ArgumentParser(description='Code summarization tool.')
    parser.add_argument('directory', type=str, help='Path to the directory to summarize')
    parser.add_argument('--gitignore', type=str, help='Path to the gitignore file')
    parser.add_argument('-ig', '--auto-gitignore', action='store_true', 
                       help='Auto-discover and use nearest .gitignore file')
    parser.add_argument('--include', type=str, help='Comma-separated list of file extensions to include')
    parser.add_argument('--exclude', type=str, help='Comma-separated list of file extensions to exclude')
    parser.add_argument('-d', '--show_docker', action='store_true', help='Include docker files')
    parser.add_argument('-o', '--show_only_docker', action='store_true', help='Show only docker files')
    parser.add_argument('-n', '--max-lines', type=int, default=None, help='Maximum number of lines to include from each file')
    parser.add_argument('--encoding', type=str, 
                       choices=['cl100k_base', 'p50k_base', 'r50k_base'], 
                       default='cl100k_base',
                       help='Tiktoken encoding to use for token counting (default: cl100k_base)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-L', '--max-depth', type=int, default=None,
                       help='Maximum directory depth to traverse for both tree and files (root=1)')
    parser.add_argument('-Lt', '--tree-depth', type=int, default=None,
                       help='Maximum directory depth for tree view (root=1)')
    parser.add_argument('-Lf', '--file-depth', type=int, default=None,
                       help='Maximum directory depth for file contents (root=1)')
    
    args = parser.parse_args()
    
    # Setup logging based on verbosity
    setup_logging(args.verbose)
    
    if args.show_docker and args.show_only_docker:
        logger.error("Cannot use both show_docker and show_only_docker options.")
        sys.exit(1)
    
    # Handle gitignore auto-discovery
    gitignore_path = args.gitignore
    if args.auto_gitignore and not gitignore_path:
        gitignore_path = discover_gitignore(args.directory)
        if gitignore_path:
            logger.info(f"Using auto-discovered .gitignore: {gitignore_path}")
        else:
            logger.info("No .gitignore file found.")

    include_exts = [".{}".format(ext.lower()) for ext in args.include.split(',')] if args.include else None
    exclude_exts = [".{}".format(ext.lower()) for ext in args.exclude.split(',')] if args.exclude else None
    
    tree_depth = args.tree_depth if args.tree_depth is not None else args.max_depth
    file_depth = args.file_depth if args.file_depth is not None else args.max_depth
    
    prompt_md = summarize_directory(args.directory, gitignore_path, include_exts,
                                  exclude_exts, show_docker=args.show_docker,
                                  show_only_docker=args.show_only_docker,
                                  max_lines=args.max_lines,
                                  tree_depth=tree_depth,
                                  file_depth=file_depth)
    prompt_file = os.path.join(args.directory, output_file)
    
    try:
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt_md)
    except IOError as e:
        logger.error(f"Failed to write output file: {str(e)}")
        sys.exit(1)
        
    print_summary(prompt_md, encoding_name=args.encoding)
    print(prompt_file)

if __name__ == '__main__':
    main()