#!/bin/bash

# GitHub Deployment Script for LinkedIn Auto Connect Bot
# Run this script on your EC2 instance to deploy from GitHub

set -e

# Configuration - Update these variables
GITHUB_REPO="https://github.com/yourusername/linkedin-auto-connect-bot.git"
BRANCH="main"
APP_DIR="/opt/linkedin-bot"

echo "🚀 Deploying LinkedIn Auto Connect Bot from GitHub..."

# Navigate to app directory
cd $APP_DIR

# Check if it's already a git repository
if [ -d ".git" ]; then
    echo "🔄 Updating existing repository..."
    git fetch origin
    git reset --hard origin/$BRANCH
    git pull origin $BRANCH
else
    echo "📥 Cloning repository..."
    # Remove any existing files
    sudo rm -rf * .* 2>/dev/null || true
    git clone $GITHUB_REPO .
    git checkout $BRANCH
fi

# Set proper ownership
sudo chown -R $USER:$USER $APP_DIR

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "🐍 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install fabric
fab install

# Create logs directory
mkdir -p logs

# Set proper permissions for config files
if [ -f "config/credentials.json" ]; then
    chmod 600 config/credentials.json
fi

if [ -f "config/cookies.pkl" ]; then
    chmod 600 config/cookies.pkl
fi

echo "✅ GitHub deployment complete!"
echo ""
echo "Next steps:"
echo "1. Add your Google Sheets credentials: nano config/credentials.json"
echo "2. Create systemd service: fab ec2_service"
echo "3. Start the service: fab ec2_start" 