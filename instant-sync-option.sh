#!/bin/bash
# Optional: Ultra-fast Syncthing setup (< 1 second sync)

echo "Installing syncthing-inotify for instant sync..."

# Install on macOS
brew install fswatch
git clone https://github.com/syncthing/syncthing-inotify.git ~/syncthing-inotify
cd ~/syncthing-inotify && go build

# Install on GPU workstation  
ssh zerotier-remote "
wget https://github.com/syncthing/syncthing-inotify/releases/download/v0.8.7/syncthing-inotify-linux-amd64-v0.8.7.tar.gz
tar -xzf syncthing-inotify-linux-amd64-v0.8.7.tar.gz
mv syncthing-inotify-linux-amd64-v0.8.7/syncthing-inotify ~/bin/
"

echo "Run with: ~/syncthing-inotify/syncthing-inotify -folder=nt-workspace"
echo "This reduces sync delay from 10s to < 1s"