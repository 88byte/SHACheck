#!/bin/bash

# Install Chromium manually
echo "Installing Chromium..."
mkdir -p /opt/render/.local/chrome
wget -qO- https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > /opt/render/.local/chrome/chrome.deb
dpkg -x /opt/render/.local/chrome/chrome.deb /opt/render/.local/chrome/
mv /opt/render/.local/chrome/opt/google/chrome/* /opt/render/.local/chrome/

# Install Chromedriver
echo "Installing Chromedriver..."
mkdir -p /opt/render/.local/chromedriver
wget -qO- https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip > /opt/render/.local/chromedriver/chromedriver.zip
unzip /opt/render/.local/chromedriver/chromedriver.zip -d /opt/render/.local/chromedriver/

# Make executable
chmod +x /opt/render/.local/chrome/chrome
chmod +x /opt/render/.local/chromedriver/chromedriver

echo "Chromium and Chromedriver installation complete!"

