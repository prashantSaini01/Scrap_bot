#!/usr/bin/env bash
# Exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

# Check if Chrome directory exists
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  # Download specific Chrome version (108.0.5359.125)
  wget -P ./ https://commondatastorage.googleapis.com/chromium-browser-official/chromium-108.0.5359.125.tar.xz
  tar -xf ./chromium-108.0.5359.125.tar.xz --strip-components=1
  rm ./chromium-108.0.5359.125.tar.xz
else
  echo "...Using Chrome from cache"
fi

# Install Chromedriver
if [[ ! -d $STORAGE_DIR/chromedriver ]]; then
  echo "...Downloading Chromedriver"
  mkdir -p $STORAGE_DIR/chromedriver
  cd $STORAGE_DIR/chromedriver
  # Download the matching Chromedriver version
  wget -P ./ https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip
  unzip chromedriver_linux64.zip
  rm chromedriver_linux64.zip
else
  echo "...Using Chromedriver from cache"
fi

# Add Chrome and Chromedriver's location to the PATH
export PATH="${PATH}:${STORAGE_DIR}/chrome:${STORAGE_DIR}/chromedriver"

# Return to the project directory to continue the build process
cd $HOME/project/src

# Logging to check that Chrome and Chromedriver are installed correctly
echo "Chrome and Chromedriver setup complete, proceeding with Flask app deployment."
