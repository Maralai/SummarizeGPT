FROM python:3.10-slim

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo git bash-completion \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    curl \
    build-essential \
    git \
    procps \
    gnupg \
    wget \
    jq \
    vim \
    bash-completion \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set up Python development environment
WORKDIR /workspace

# Install core Python packages
RUN pip install --upgrade pip && \
    pip install setuptools wheel build twine pytest pytest-cov

# Install claude-cli (simulate, actual installation would be done if available via package manager)
RUN echo "# Installing claude-cli would go here" > /usr/local/bin/claude && \
    chmod +x /usr/local/bin/claude

# Configure git to use main as default branch
RUN git config --system init.defaultBranch main

# Add a script to be executed every time the container starts
COPY .devcontainer/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Add a simple alias for claude-code interactions
RUN echo 'alias claudec="claude -h"' >> /home/$USERNAME/.bashrc && \
    echo 'alias claude-help="claude -h"' >> /home/$USERNAME/.bashrc

# Make all the scripts executable (will be done after container starts)
RUN mkdir -p /tmp/scripts

# Setup default shell
ENV SHELL /bin/bash

# Switch back to dialog for apt
ENV DEBIAN_FRONTEND=dialog

USER $USERNAME

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]