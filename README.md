[![Test Summarize GPT](https://github.com/Maralai/SummarizeGPT/actions/workflows/python-app.yml/badge.svg)](https://github.com/Maralai/SummarizeGPT/actions/workflows/python-app.yml)

# Code Summarization Tool
This tool generates a summary of a directory's contents, including a tree view of its subdirectories and files, and the contents of each file. It can optionally exclude files listed in a .gitignore file, exclude or include Docker files, or filter files based on their extensions.

## Installation
This tool can be run directly from the command line without installation. Just ensure you have Python installed and can run Python scripts.
Otherwise, you can install this tool as a package using pip:
```bash
pip install summarizeGPT
```

## Usage
To use this tool, run the following command:
```
SummarizeGPT <directory_path> [options]
```

### Options:
* `<directory_path>`: Path to the directory to summarize
* `--gitignore <gitignore_path>`: Path to the gitignore file
* `-ig, --auto-gitignore`: Auto-discover and use nearest .gitignore file
* `--include <file_extensions>`: Comma-separated list of file extensions to include
* `--exclude <file_extensions>`: Comma-separated list of file extensions to exclude
* `-d, --show_docker`: Include docker files
* `-o, --show_only_docker`: Show only docker files
* `-n, --max-lines <number>`: Maximum number of lines to include from each file
* `--encoding {cl100k_base,p50k_base,r50k_base}`: Tiktoken encoding to use for token counting (default: cl100k_base)
* `-v, --verbose`: Enable verbose output
* `-L, --max-depth <number>`: Maximum directory depth to traverse for both tree and files (root=1)
* `-Lt, --tree-depth <number>`: Maximum directory depth for tree view (root=1)
* `-Lf, --file-depth <number>`: Maximum directory depth for file contents (root=1)

> Note: On Windows the command can be case insensitive (try 'summarizegpt'), but on Linux it must be 'SummarizeGPT'.

## Examples
Basic usage:
```bash
SummarizeGPT .
```

With gitignore:
```bash
SummarizeGPT /path/to/directory --gitignore /path/to/.gitignore
SummarizeGPT /path/to/directory -ig  # Auto-discover and use nearest .gitignore
```

Filter by file extensions:
```bash
SummarizeGPT /path/to/directory --include py,txt
SummarizeGPT /path/to/directory --exclude xml,js
```

Docker-related files:
```bash
SummarizeGPT /path/to/directory -d  # Include Docker files
SummarizeGPT /path/to/directory -o  # Show only Docker files
```

Limit output and enable verbose logging:
```bash
SummarizeGPT /path/to/directory -n 100 -v
```

Limit directory depth:
```bash
SummarizeGPT /path/to/directory -L 2  # Limit both tree and file depth to 2 levels
SummarizeGPT /path/to/directory -Lt 3 -Lf 2  # Tree depth of 3, file depth of 2
```

## Output
The tool generates a file called `Context_for_ChatGPT.md` in the specified directory containing:
- A tree view of the directory structure
- Contents of included files
- Summary statistics including:
  - Total lines
  - Total characters
  - Total bytes
  - Approximate token count (using specified tiktoken encoding)

## Limitations
- Does not interpret file contents
- Does not handle symbolic links
- Large directories or files can result in large output files
- Token counting is approximate and depends on the chosen encoding

## Future Enhancements
- AI-powered code summarization to reduce output size and improve readability
- Support for additional file types and encodings
- Improved handling of large files and directories

## Contributing
Contributions are welcome! Feel free to submit a pull request if you've made an improvement or fixed a bug.

### Development with Claude Code
This project provides a complete, reusable development environment using Visual Studio Code's Dev Containers feature with Claude Code integration. To use it:

1. Install [Docker](https://www.docker.com/get-started) and [Visual Studio Code](https://code.visualstudio.com/)
2. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code
3. Install the [Claude Code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) extension in VS Code
4. Clone this repository
5. Open the repository in VS Code
6. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Dev Containers: Reopen in Container"

The environment includes:
- Python 3.10 development environment
- Claude Code integration for AI-assisted development
- Automated dependency installation
- Comprehensive testing framework (pytest with coverage)
- Code quality tools (black, flake8, mypy, isort)
- VS Code extensions and tasks for Python development
- Support for both containerized and local development
- Git and GitHub CLI integration

#### Reusing the Development Setup

The `.devcontainer` and `.vscode` configuration is designed to be reusable for other Python projects:

1. Copy both the `.devcontainer` and `.vscode` directories to your project
2. Modify the following project-specific items:
   - Update `PACKAGE_NAME` and `SOURCE_DIRS` in `docker-compose.yml`
   - Update launch configurations in `.vscode/launch.json` if needed
   - Customize the CLAUDE.md template in `entrypoint.sh`
3. Open your project in VS Code and select "Reopen in Container"

The setup automatically:
- Installs your package in development mode
- Sets up Claude Code integration
- Configures all development tools
- Creates a Makefile with common commands
- Provides scripts for testing and linting
- Generates a CLAUDE.md file with project information for Claude Code

#### Working with Claude Code

The environment is pre-configured to work with Claude Code:
- A CLAUDE.md file is generated with project-specific information
- VS Code settings are optimized for AI-assisted development
- Claude CLI is available in the terminal
- Claude Code extension is pre-installed in the container

### Development Commands
This project uses a Makefile to simplify common development tasks:

```bash
make help        # Show available commands
make install     # Install the package
make dev         # Install development dependencies
make lint        # Run linting checks
make test        # Run tests
make clean       # Clean build artifacts
make build       # Build package
make publish     # Upload package to PyPI
```

### Testing
Run the tests with pytest:

```bash
pytest
```

Or use the Makefile:

```bash
make test
```

## License
This project is licensed under the terms of the GPLv3 license.