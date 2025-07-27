#!/bin/bash

# Create systemd service for LinkedIn Auto Connect Bot

echo "🔧 Creating systemd service..."

# Create the service file
sudo tee /etc/systemd/system/linkedin-bot.service > /dev/null <<EOF
[Unit]
Description=LinkedIn Auto Connect Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/linkedin-bot
Environment=PATH=/opt/linkedin-bot/venv/bin
Environment=DISPLAY=:99
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset
ExecStart=/opt/linkedin-bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable linkedin-bot.service

echo "✅ Systemd service created!"
echo ""
echo "Service commands:"
echo "- Start: sudo systemctl start linkedin-bot"
echo "- Stop: sudo systemctl stop linkedin-bot"
echo "- Status: sudo systemctl status linkedin-bot"
echo "- Logs: sudo journalctl -u linkedin-bot -f" 