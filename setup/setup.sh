#!/usr/bin/env bash

set -e  # Exit on error

echo "Checking for Python..."

if ! command -v python3 &>/dev/null; then
    echo "WARNING: Python3 not found. Installing..."

    if command -v apt &>/dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip
    else
        echo "ERROR: Unsupported package manager. Install Python manually."
        exit 1
    fi
else
    echo "Python3 is already installed."
fi

echo "Checking for Make / build tools..."

if ! command -v make &>/dev/null; then
    echo "WARNING: make not found. Installing build tools..."

    if command -v apt &>/dev/null; then
        sudo apt install -y make build-essential
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y make gcc gcc-c++
    elif command -v yum &>/dev/null; then
        sudo yum install -y make gcc gcc-c++
    else
        echo "ERROR: Unsupported package manager. Install make manually."
        exit 1
    fi
else
    echo "Make is already installed."
fi

echo "Upgrading pip..."
python3 -m pip install --upgrade pip

echo "Installing NumPy..."
python3 -m pip install numpy

echo "Installing SciPy..."
python3 -m pip install scipy

echo "NOTE: Setup complete."
