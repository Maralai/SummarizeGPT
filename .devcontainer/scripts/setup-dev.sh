#!/bin/bash
set -e

# This script sets up development tools and configuration files
# It can be customized by setting environment variables:
# - CONFIG_DIR: Directory containing config files (default: .devcontainer/config)
# - PROJECT_ROOT: Root directory of the project (default: current directory)

# Set default config directory
CONFIG_DIR=${CONFIG_DIR:-".devcontainer/config"}
PROJECT_ROOT=${PROJECT_ROOT:-"."}

echo "Setting up development environment..."

# Create symbolic links to config files if they exist
for config_file in "$CONFIG_DIR"/{.flake8,mypy.ini,.editorconfig}; do
    if [ -f "$config_file" ]; then
        base_name=$(basename "$config_file")
        target_path="$PROJECT_ROOT/$base_name"
        
        # Skip if the target already exists and is not a symlink
        if [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
            echo "Skipping $base_name: file already exists in project root"
            continue
        fi
        
        # Create symbolic link
        ln -sf "$(realpath "$config_file")" "$target_path"
        echo "Created symlink for $base_name"
    fi
done

# Handle pyproject.toml specially
if [ -f "$CONFIG_DIR/pyproject.toml" ]; then
    # Check if project already has a pyproject.toml
    if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
        echo "Skipping pyproject.toml: file already exists in project root"
    else
        # Create a combined pyproject.toml with build system from template and tool config from our file
        if [ -f "$CONFIG_DIR/pyproject-template.toml" ]; then
            cat "$CONFIG_DIR/pyproject-template.toml" > "$PROJECT_ROOT/pyproject.toml"
            # Extract tool sections from our config and append to the project file
            grep -A 1000 "\[tool\." "$CONFIG_DIR/pyproject.toml" >> "$PROJECT_ROOT/pyproject.toml"
            echo "Created combined pyproject.toml"
        else
            # Just copy our file
            cp "$CONFIG_DIR/pyproject.toml" "$PROJECT_ROOT/pyproject.toml"
            echo "Created pyproject.toml"
        fi
    fi
fi

# Make scripts executable
chmod +x "$CONFIG_DIR"/../scripts/*.sh

# Create symlinks to scripts in project root
mkdir -p "$PROJECT_ROOT/scripts"
for script in "$CONFIG_DIR"/../scripts/*.sh; do
    base_name=$(basename "$script")
    target_path="$PROJECT_ROOT/scripts/$base_name"
    
    # Skip if the target already exists and is not a symlink
    if [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
        echo "Skipping $base_name: script already exists in project scripts directory"
        continue
    fi
    
    # Create symbolic link
    ln -sf "$(realpath "$script")" "$target_path"
    echo "Created symlink for $base_name in scripts directory"
done

echo "Development environment setup complete!"