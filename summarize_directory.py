import argparse
import os
import sys
import gitignore_parser

output_file = "Context_for_ChatGPT.md"

def summarize_directory(directory, gitignore_file=None, show_docker=False, show_only_docker=False):
    # Replace backslashes and forward slashes with os.path.sep
    directory = directory.replace("\\", "/")
    prompt_md = f"# Summary of directory: {directory}\n\n"
    tree_view = get_tree_view(directory, gitignore_file=gitignore_file)
    prompt_md += "```\n" + tree_view + "\n```\n\n"
    file_contents = get_file_contents(directory, gitignore_file, show_docker=show_docker, show_only_docker=show_only_docker)
    prompt_md += file_contents
    return prompt_md

def get_tree_view(directory, gitignore_file=None):
    tree_view = ""
    if gitignore_file:
        gitignore = gitignore_parser.parse_gitignore(gitignore_file)
    else:
        gitignore = None

    for root, dirs, files in os.walk(directory):
        if gitignore:
            dirs[:] = [d for d in dirs if not gitignore(os.path.join(root, d))]
            files = [f for f in files if not gitignore(os.path.join(root, f))]
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree_view += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            if file == output_file:
                continue
            tree_view += f"{sub_indent}{file}\n"
    return tree_view

def get_file_contents(directory, gitignore_file=None, show_docker=False, show_only_docker=False):
    file_contents = ""
    excluded_files = ['docker', 'Dockerfile', 'requirements.txt', '.env', 'prompt.md']
    if gitignore_file:
        gitignore = gitignore_parser.parse_gitignore(gitignore_file)
    else:
        gitignore = None

    for root, _, files in os.walk(directory):
        if gitignore:
            files = [f for f in files if not gitignore(os.path.join(root, f))]
        for file in files:
            if not show_docker and not show_only_docker:
                if file.lower().endswith(('.env')) or any(substring in file.lower() for substring in excluded_files):
                    continue
            elif show_only_docker:
                if not any(substring in file.lower() for substring in ['docker', 'Dockerfile', 'requirements.txt']):
                    continue

            if file == output_file:
                continue
            file_path = os.path.join(root, file).replace("\\", "/")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    contents = f.read()
                    file_contents += f"## {file_path}\n\n```\n{remove_empty_lines(contents)}\n```\n\n"
            except UnicodeDecodeError:
                print(f"Skipping file {file_path}: unable to decode with UTF-8 encoding.")
    return file_contents



def remove_empty_lines(text):
    return "\n".join([line for line in text.split("\n") if line.strip()])

def print_summary(summary):
    total_lines = summary.count('\n')
    total_chars = len(summary)
    total_bytes = sys.getsizeof(summary.encode('utf-8'))
    print(f"\nTotal Lines: {total_lines}\nTotal Characters: {total_chars}\nTotal Bytes: {total_bytes}\n")

def main():
    parser = argparse.ArgumentParser(description='Code summarization tool.')
    parser.add_argument('directory', type=str, help='Path to the directory to summarize')
    parser.add_argument('--gitignore', type=str, help='Path to the gitignore file')
    parser.add_argument('-d', '--show_docker', action='store_true', help='Include docker files')
    parser.add_argument('-o', '--show_only_docker', action='store_true', help='Show only docker files')
    args = parser.parse_args()

    print("show_docker: ", args.show_docker, "\nshow_only_docker: ", args.show_only_docker)

    if args.show_docker and args.show_only_docker:
        print("Error: Cannot use both show_docker and show_only_docker options.")
        sys.exit()

    prompt_md = summarize_directory(args.directory, args.gitignore, show_docker=args.show_docker, show_only_docker=args.show_only_docker)

    prompt_file = os.path.join(args.directory, output_file)
    with open(prompt_file, "w") as f:
        f.write(prompt_md)

    print_summary(prompt_md)
    print(prompt_file)


if __name__ == '__main__':
    main()
