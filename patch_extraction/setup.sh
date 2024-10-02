#!/bin/bash

set -e

# Determine the OS
OS="$(uname)"
echo "Detected OS: $OS"

if [ "$OS" == "Darwin" ]; then
    # macOS
    echo "Installing dependencies on macOS..."

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."

        # Install Homebrew using curl
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Homebrew is already installed."
    fi

    echo "Updating Homebrew..."
    brew update

    echo "Installing packages..."
    brew install \
        openslide \
        libomp \
        pkg-config \
        cairo \
        openjpeg \
        tcl-tk

elif [ "$OS" == "Linux" ]; then
    # Linux
    echo "Installing dependencies on Linux..."

    # Check if apt is available
    if command -v apt &> /dev/null; then
        echo "Using apt package manager..."
        sudo apt update

        echo "Installing packages..."
        sudo apt install -y \
            libopenjp2-7-dev \
            libopenjp2-tools \
            openslide-tools \
            libpixman-1-dev \
            libglib2.0-0 \
            libgl1-mesa-glx \
            libsm6 \
            libxext6 \
            libxrender-dev \
            build-essential
    else
        echo "apt not found. Please install the required packages using your distribution's package manager."
        exit 1
    fi

else
    echo "Unsupported OS: $OS"
    exit 1
fi

# Set environment variables for libomp and openblas if installed
echo "Setting environment variables for libomp and openblas..."
export LDFLAGS="-L/usr/local/opt/libomp/lib -L/usr/local/opt/openblas/lib $LDFLAGS"
export CPPFLAGS="-I/usr/local/opt/libomp/include -I/usr/local/opt/openblas/include $CPPFLAGS"
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig:$PKG_CONFIG_PATH"

# Check if Conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda could not be found. Installing Miniconda..."

    # Download Miniconda using curl
    if [ "$OS" == "Darwin" ]; then
        # macOS installer
        curl -fsSL -o ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
    elif [ "$OS" == "Linux" ]; then
        # Linux installer
        curl -fsSL -o ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    fi

    # Install Miniconda 
    bash ~/miniconda.sh -b -p $HOME/miniconda
    rm ~/miniconda.sh
    export PATH="$HOME/miniconda/bin:$PATH"

    # Initialize Conda
    conda init "$(basename "${SHELL}")"
    source "$HOME/.bashrc"  # or "$HOME/.zshrc" depending on your shell

else
    echo "Conda is already installed."
    # Initialize Conda
    source "$(conda info --base)/etc/profile.d/conda.sh"
fi

# Remove existing environment if it exists
if conda env list | grep -q 'image-processing'; then
    echo "Removing existing 'image-processing' environment..."
    conda env remove -n image-processing
fi

# Create the Conda environment
echo "Creating Conda environment..."
conda env create -f environment.yml

echo "Setup is complete. Activate your environment with 'conda activate image-processing'."
