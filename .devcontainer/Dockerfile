FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set the Python version you want
ARG PYTHON_VERSION=3.13

# Install essential development dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    git \
    vim \
    sudo \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Add deadsnakes PPA and install specific Python version
RUN add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-venv \
    && rm -rf /var/lib/apt/lists/*

# Set the specific Python version as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1

# Install pip using ensurepip instead of apt
RUN python3 -m ensurepip --upgrade --default-pip

# Upgrade pip to latest version using the new pip binary
RUN python3 -m pip install --upgrade pip

# Create a non-root user for development
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to the non-root user
USER $USERNAME

# Set working directory
WORKDIR /workspace

# Reset DEBIAN_FRONTEND
ENV DEBIAN_FRONTEND=dialog

# Default command
CMD ["/bin/bash"]