# 🚀 EC2 GitHub Deployment Summary

## Quick Deployment Steps

### 1. **Launch EC2 Instance**
- **AMI**: Ubuntu 20.04/22.04 LTS
- **Instance Type**: `t3.medium` (recommended)
- **Storage**: 20GB minimum
- **Security Group**: Allow SSH (port 22)

### 2. **Initial Setup on EC2**
```bash
# SSH to your instance
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip

# Run initial setup
chmod +x deploy/ec2_setup.sh
./deploy/ec2_setup.sh
```

### 3. **Deploy from GitHub**
```bash
# Edit the GitHub repository URL in the script
nano deploy/github_deploy.sh

# Update GITHUB_REPO to your repository URL
# GITHUB_REPO="https://github.com/yourusername/your-repo.git"

# Run deployment
chmod +x deploy/github_deploy.sh
./deploy/github_deploy.sh
```

### 4. **Configure and Start Service**
```bash
cd /opt/linkedin-bot
source venv/bin/activate

# Add your Google Sheets credentials
nano config/credentials.json

# Create and start systemd service
fab ec2_service
fab ec2_start
```

## 📊 Management Commands

```bash
# Check service status
fab ec2_status

# View real-time logs
fab ec2_logs

# Restart service
fab ec2_restart

# Update from GitHub
fab github_update
```

## 💰 Cost Estimate (US East)
- **t3.micro**: ~$8.50/month (Free tier eligible)
- **t3.medium**: ~$30/month (Recommended)
- **t3.large**: ~$60/month (High volume)

## 🔒 Security Setup
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow ssh

# Set proper file permissions
chmod 600 config/credentials.json
chmod 600 config/cookies.pkl
```

## 📞 Quick Troubleshooting
```bash
# Check service status
sudo systemctl status linkedin-bot

# View system logs
sudo journalctl -u linkedin-bot -f

# Check Chrome installation
google-chrome --version

# Check memory usage
free -h
```

---
**Ready to deploy from GitHub!** 🎉 