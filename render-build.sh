#!/bin/bash
set -e

# Create directory for Chromium
mkdir -p /opt/render/project/.chromium

# Download prebuilt Chromium & Chromedriver (Render-compatible)
echo "Downloading Chromium..."
wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" -O /opt/render/project/.chromium/chrome.deb
dpkg -x /opt/render/project/.chromium/chrome.deb /opt/render/project/.chromium/

echo "Downloading Chromedriver..."
wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" -O /opt/render/project/.chromium/chromedriver.zip
unzip /opt/render/project/.chromium/chromedriver.zip -d /opt/render/project/.chromium/
chmod +x /opt/render/project/.chromium/chromedriver

# Install dependencies
pip install -r requirements.txt
