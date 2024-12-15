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
* `--include <file_extensions>`: Comma-separated list of file extensions to include
* `--exclude <file_extensions>`: Comma-separated list of file extensions to exclude
* `-d, --show_docker`: Include docker files
* `-o, --show_only_docker`: Show only docker files
* `-n, --max-lines <number>`: Maximum number of lines to include from each file
* `--encoding {cl100k_base,p50k_base,r50k_base}`: Tiktoken encoding to use for token counting (default: cl100k_base)
* `-v, --verbose`: Enable verbose output

> Note: On Windows the command can be case insensitive (try 'summarizegpt'), but on Linux it must be 'SummarizeGPT'.

## Examples
Basic usage:
```bash
SummarizeGPT .
```

With gitignore:
```bash
SummarizeGPT /path/to/directory --gitignore /path/to/.gitignore
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

## License
This project is licensed under the terms of the GPLv3 license.