![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Maralai/SummarizeGPT/Test%20Summarize%20GPT)

# Code Summarization Tool

This tool generates a summary of a directory's contents, including a tree view of its subdirectories and files, and the contents of each file. It can optionally exclude files listed in a .gitignore file, exclude or include Docker files, or filter files based on their extensions.

## Installation

This tool can be run directly from the command line without installation. Just ensure you have Python installed and can run Python scripts.

## Usage

To use this tool, run the following command:

```
python summarize_directory.py <directory_path> [--gitignore <gitignore_path>] [--include <file_extensions>] [--exclude <file_extensions>] [-d|--show_docker] [-o|--show_only_docker]
```

Where:

* `<directory_path>` is the path to the directory to summarize.
* `<gitignore_path>` is the path to the .gitignore file to use.
* `<file_extensions>` is a comma-separated list of file extensions to include or exclude.
* `--show_docker` includes Docker files.
* `--show_only_docker` shows only Docker files.

## Examples

Summarize the contents of the current directory:

```
python summarize_directory.py .
```

Summarize the contents of a directory and exclude files listed in a .gitignore file:

```
python summarize_directory.py /path/to/directory --gitignore /path/to/.gitignore
```

Summarize the contents of a directory and include only .py and .txt files:

```
python summarize_directory.py /path/to/directory --include py,txt
```

Exclude .xml and .js files from the summary:

```
python summarize_directory.py /path/to/directory --exclude xml,js
```

Summarize the contents of a directory and include Docker files:

```
python summarize_directory.py /path/to/directory -d
```

Summarize the contents of a directory and show only Docker files:

```
python summarize_directory.py /path/to/directory -o
```

## Output

The tool generates a file called `Context_for_ChatGPT.md` in the specified directory with the summary of the directory's contents. The file includes a tree view of the directory's subdirectories and files, as well as the contents of each file. The tool also outputs a summary of the generated markdown, including the total number of lines, characters, and bytes.

# More Examples with AI Assistance

## ChatGPT Prompt for Command:
-------
```
Given this:
SummarizeGPT /path/to/directory --gitignore /path/to/.gitignore

Can you write me a prompt that implements these:
C:\dev\edge\plugins\storage_local
C:\dev\edge\.gitignore
```
-------
> Sure! Here's a prompt that implements those arguments:
> 
> ```
> python summarize_directory.py C:/dev/edge/plugins/storage_local --gitignore C:/dev/edge/.gitignore
> ```
> 
> This prompt summarizes the contents of the `C:/dev/edge/plugins/storage_local` directory and excludes files listed in the `C:/dev/edge/.gitignore` file. The output will be saved in a file called `Context_for_ChatGPT.md` in the `C:/dev/edge/plugins/storage_local` directory.
> 
> -ChatGPT

## Copilot Prompt for Command:
-------
The pattern below is great if you have copilot, you litterly can build off of what is below and just simply add your conditions and provide an empty line.  Copilot will do the rest.
```
# Given This:
SummarizeGPT /path/to/directory --gitignore /path/to/.gitignore

# Your Conditions
C:\dev\edge\plugins\inference_resource_alert
C:\dev\edge\.gitignore

SummarizeGPT C:/dev/edge/Edge/plugins/storage_local --gitignore C:\dev\edge\Edge\.gitignore
```

> Just add your conditions in the code block above and provide an empty line.  Copilot will do the rest.

## Limitations

This tool does not interpret the contents of the files. It simply displays the file structure and raw contents. If you have large files or numerous files in your directory, the summary file can become quite large. 

The tool also does not handle symbolic links, so it will not follow links to directories or files outside of the specified directory. 

## Contributions

Contributions are welcome! Feel free to submit a pull request if you've made an improvement or fixed a bug.

Certainly, here's a proposed update to your README that includes a section on future enhancements and a call for contributions:

## Future Enhancements

TODO Could you assist with implementing the following?

Maybe an argument, that when used instead of including the raw content of each file, an AI could generate an ai-readable summary of the code. This could dramatically reduce the output file size for large directories or files and make the summary more useful for quickly understanding the purpose and function of each file in the directory.

Perhaps this is something that can be cowritten with open.ai or copilot.

> For example: when using this tool, on this tool and the above Future Enhancement in a ChatGPT 4 chat prompt it yielded the below section. -MSH

-------

Here's a conceptual approach for implementing your request:

1. Include a new argument in your argument parser named `--ai_summary` (or something similar) which, when used, will trigger generating AI-readable summaries instead of including the raw content of each file.

2. In your `get_file_contents` function, add a condition to check if the `--ai_summary` argument is enabled. If it is, instead of adding the raw content of the file to `file_contents`, you would call an AI model to generate a summary of the file content, and then append that summary to `file_contents`.

To implement AI code summarization, you can use OpenAI's GPT-3 or GPT-4 API. Keep in mind that there will be some limitations due to the length of the text you can input to the API (for GPT-3, the maximum token limit is 4096 as of my knowledge cutoff in September 2021), so you might need to extract meaningful parts of the code or truncate it to fit within this limit.

Here is a rough skeleton of how you could modify your script:

```python
import openai

# Set up OpenAI API
openai.api_key = 'your-api-key'

def summarize_code(code):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Or whichever engine you want to use
        prompt=code,
        max_tokens=100,  # Adjust as needed
        temperature=0.3
    )
    return response.choices[0].text.strip()

def get_file_contents(directory, gitignore_file=None, include_exts=None, exclude_exts=None, show_docker=False, show_only_docker=False, ai_summary=False):
    # ... existing code ...

    for file in files:
        # ... existing code ...

        if ai_summary:
            # Generate AI summary instead of including raw content
            contents = summarize_code(contents)
        file_contents += f"## {file_path}\n\n```\n{remove_empty_lines(contents)}\n```\n\n"

    # ... existing code ...

def main():
    parser = argparse.ArgumentParser(description='Code summarization tool.')
    # ... existing arguments ...
    parser.add_argument('-ai', '--ai_summary', action='store_true', help='Generate AI summary of
```
---

> Pretty cool, huh? Now someone just needs to implement it! -MSH

## Contribute

Contributions are welcome! Feel free to submit a pull request if you've made an improvement or fixed a bug.

## License

This project is licensed under the terms of the GPLv3 license.
