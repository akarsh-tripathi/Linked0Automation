#!/bin/bash

# EC2 Setup Script for LinkedIn Auto Connect Bot
# Run this script on your EC2 instance after initial setup

set -e

echo "🚀 Setting up LinkedIn Auto Connect Bot on EC2..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3 and pip
echo "🐍 Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv git

# Install Chrome and ChromeDriver
echo "🌐 Installing Chrome browser..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Install Xvfb for headless display
echo "🖥️ Installing virtual display..."
sudo apt-get install -y xvfb

# Install other dependencies
echo "📚 Installing system dependencies..."
sudo apt-get install -y curl wget unzip build-essential

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/linkedin-bot
sudo chown $USER:$USER /opt/linkedin-bot

echo "✅ EC2 setup complete!"
echo ""
echo "Next steps - Choose one deployment method:"
echo ""
echo "🔹 Option 1: Deploy from GitHub (Recommended)"
echo "   1. Download GitHub deployment script:"
echo "      wget https://raw.githubusercontent.com/your-repo/main/deploy/github_deploy.sh"
echo "   2. Edit the script to set your GitHub repository URL"
echo "   3. Run: chmod +x github_deploy.sh && ./github_deploy.sh"
echo ""
echo "🔹 Option 2: Manual file copy"
echo "   1. Copy your application files to /opt/linkedin-bot/"
echo "   2. Run: cd /opt/linkedin-bot"
echo "   3. Run: python3 -m venv venv && source venv/bin/activate"
echo "   4. Run: pip install fabric && fab install"
echo "   5. Configure your credentials and cookies"
echo "   6. Run: fab setup" 