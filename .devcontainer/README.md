# Python Development Container with Claude Code

This directory contains a reusable development environment setup for Python projects using VS Code's Dev Containers feature with Claude Code integration.

## Features

- Python 3.10 development environment
- Claude Code integration for AI-assisted development
- Automatic package installation in development mode
- Code quality tools (black, flake8, mypy, isort)
- Testing framework (pytest with coverage)
- VS Code extensions and settings for Python development
- Reusable scripts for linting and testing
- Support for both containerized and local development
- Git and GitHub CLI integration

## Structure

- `config/` - Configuration files for development tools
  - `requirements-dev.txt` - Development dependencies
  - `.flake8` - Flake8 configuration
  - `mypy.ini` - Mypy configuration
  - `.editorconfig` - EditorConfig settings
  - `pyproject.toml` - Pytest, Black, and isort configuration
  
- `scripts/` - Reusable scripts for development tasks
  - `lint.sh` - Runs all linting tools
  - `test.sh` - Runs tests with pytest
  - `setup-dev.sh` - Sets up the development environment

- `Dockerfile` - Defines the development container
- `docker-compose.yml` - Service configuration
- `devcontainer.json` - VS Code Dev Container configuration
- `entrypoint.sh` - Container startup script

## Companion .vscode Directory

This setup includes a companion `.vscode` directory with:

- `settings.json` - VS Code settings for use both inside and outside containers
- `extensions.json` - Recommended VS Code extensions
- `launch.json` - Debug configurations for Python
- `tasks.json` - Common development tasks

## Claude Code Integration

The container automatically sets up Claude Code for AI-assisted development:

- Creates a CLAUDE.md file with project-specific information
- Installs the Claude CLI if available
- Configures VS Code for optimal use with Claude Code
- Sets up environment variables for Claude integration

## Usage in Another Project

To use this setup in another Python project:

1. Copy both the `.devcontainer` and `.vscode` directories to your project
2. Modify the following project-specific items:
   - Update `PACKAGE_NAME` and `SOURCE_DIRS` in `docker-compose.yml`
   - Update launch configurations in `.vscode/launch.json` if needed
   - Customize the CLAUDE.md template in `entrypoint.sh`
3. Open your project in VS Code and use the "Reopen in Container" option

The environment will automatically set itself up when you open the project in VS Code with the Dev Containers extension.

## Environment Variables

The scripts support various environment variables for customization:

- `PACKAGE_NAME` - Name of your Python package (for testing coverage)
- `SOURCE_DIRS` - Space-separated list of source directories to lint
- `TEST_DIRS` - Space-separated list of test directories
- `CONFIG_DIR` - Directory containing config files
- `PYTEST_ARGS` - Additional arguments to pass to pytest
- `CLAUDE_CLI_ENABLED` - Set to "true" to enable Claude CLI integration
- `SETUP_VENV` - Set to "false" to skip virtual environment setup

See the script headers for more configuration options.

## Security Features

- Non-root user by default
- Volume-based credential sharing
- Secure container isolation
- Proper permissions for shared files

## Persistence

- Command history is preserved between container restarts
- Git configuration is shared from the host
- SSH keys can be securely shared from the host
- Claude configuration is preserved between sessions