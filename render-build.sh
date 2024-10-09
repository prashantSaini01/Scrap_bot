#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  # Use Chrome 108.0.5359.125 from the archive
  wget -P ./ https://commondatastorage.googleapis.com/chromium-browser-official/chromium-108.0.5359.125.tar.xz
  tar -xf ./chromium-108.0.5359.125.tar.xz --strip-components=1
  rm ./chromium-108.0.5359.125.tar.xz
  cd $HOME/project/src # Make sure we return to where we were
else
  echo "...Using Chrome from cache"
fi

# Add Chrome's location to the PATH
export PATH="${PATH}:/opt/render/project/.render/chrome"

# Continue with your build commands...
