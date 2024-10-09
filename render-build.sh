#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_108.0.5359.125-1_amd64.deb
  dpkg -x ./google-chrome-stable_108.0.5359.125-1_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_108.0.5359.125-1_amd64.deb
  cd $HOME/project/src # Make sure we return to where we were
else
  echo "...Using Chrome from cache"
fi

# Add Chrome's location to the PATH
export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"

# Continue with your build commands...
