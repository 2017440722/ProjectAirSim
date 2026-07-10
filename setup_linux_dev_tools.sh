#!/bin/bash
# Copyright (C) Microsoft Corporation.
# Copyright (C) 2025 IAMAI CONSULTING CORP
# MIT License.

set -e

# Inform the user that the environment variable UE_ROOT is not set.
if [ -z "$UE_ROOT" ]; then
    echo "Warning: The UE_ROOT environment variable is not set." >&2
fi

sudo apt-get update

# Install lsb_release to check Ubuntu version
sudo apt-get -y install --no-install-recommends lsb-release git wget gnupg ca-certificates

# Get raw system version & codename
RAW_VERSION=$(lsb_release -rs)
RAW_CODENAME=$(lsb_release -cs)

echo "Raw system version: $RAW_VERSION, Raw codename: $RAW_CODENAME"

# ========== 关键修复：Pop!OS resolute 映射为 Ubuntu jammy 22.04 ==========
if [[ "$RAW_CODENAME" == "resolute" ]]; then
    # Pop!OS resolute base on Ubuntu 22.04 jammy
    CODENAME="jammy"
    VERSION="22.04"
else
    CODENAME="$RAW_CODENAME"
    VERSION="$RAW_VERSION"
fi

echo "Mapped Ubuntu version: $VERSION, Mapped codename for LLVM: $CODENAME"

# Define the LLVM version corresponding to different Ubuntu versions.
# Ubuntu 18.04 -> LLVM 11
# Ubuntu 20.04 22.04 24.04 -> LLVM 13
declare -A LLVM_VERSION_MAP=(
    ["18.04"]="11"
    ["20.04"]="13"
    ["22.04"]="13"
    ["24.04"]="13"
)

# Obtain the LLVM version that should be installed on the current system.
TARGET_LLVM_VERSION=${LLVM_VERSION_MAP[$VERSION]}

# LLVM sources.list file
LLVM_SOURCES_LIST_FILE="/etc/apt/sources.list.d/llvm.list"
# LLVM gpg key file
LLVM_GPG_KEY_FILE="/etc/apt/trusted.gpg.d/llvm.gpg"

# support ubuntu 18.04 20.04 22.04 24.04
if [ "$VERSION" == "18.04" ]; then
    # Add Kitware's APT repository to get cmake 3.15 or newer on Ubuntu 18.04 following https://apt.kitware.com/
    sudo apt-get -y install \
        apt-transport-https \
        software-properties-common

    wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
    sudo apt-add-repository -y "deb https://apt.kitware.com/ubuntu/ ${CODENAME} main"
    
    # Add the official Vulkan PPA repository to support vulkan-tools on Ubuntu 18.04.
    sudo add-apt-repository -y ppa:graphics-drivers/ppa
fi

# Add LLVM official APT repo
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key  2>/dev/null | sudo gpg --dearmor - | sudo tee ${LLVM_GPG_KEY_FILE} >/dev/null 
echo "deb [signed-by=${LLVM_GPG_KEY_FILE}] http://apt.llvm.org/${CODENAME}/ llvm-toolchain-${CODENAME}-${TARGET_LLVM_VERSION} main" | sudo tee ${LLVM_SOURCES_LIST_FILE}

# Update package lists
sudo apt-get update

# Install prerequisites
sudo apt-get -y install --no-install-recommends \
    lsb-release \
    build-essential \
    rsync \
    make \
    cmake \
    clang-${TARGET_LLVM_VERSION} \
    libc++-${TARGET_LLVM_VERSION}-dev \
    libc++abi-${TARGET_LLVM_VERSION}-dev \
    ninja-build \
    libvulkan1 \
    vulkan-tools
