# 🚀 EC2 Deployment Guide for LinkedIn Auto Connect Bot

This guide will help you deploy the LinkedIn Auto Connect Bot to an AWS EC2 instance.

## 📋 Prerequisites

### AWS Setup
1. **EC2 Instance**: Launch an Ubuntu 20.04 or 22.04 LTS instance
   - Recommended: `t3.medium` or larger (2 vCPU, 4GB RAM)
   - Storage: At least 20GB
   - Security Group: Allow SSH (port 22) from your IP

2. **Key Pair**: Have your EC2 key pair (.pem file) ready

3. **Elastic IP** (Optional but recommended): Assign a static IP to your instance

### Local Setup
- SSH access to your EC2 instance
- Your LinkedIn credentials and Google Sheets service account key

## 🔧 Step-by-Step Deployment

### Step 1: Launch and Configure EC2 Instance

1. **Launch Instance**:
   ```bash
   # Connect to your instance
   ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip
   ```

2. **Run Initial Setup**:
   ```bash
   # Copy the setup script to your instance
   curl -O https://raw.githubusercontent.com/your-repo/deploy/ec2_setup.sh
   chmod +x ec2_setup.sh
   ./ec2_setup.sh
   ```

### Step 2: Deploy Application Code

1. **Update deployment script** (`deploy/deploy.sh`):
   ```bash
   # Edit these variables in deploy.sh
   EC2_HOST="your-ec2-ip-or-hostname"
   EC2_USER="ubuntu"
   KEY_PATH="~/.ssh/your-key.pem"
   ```

2. **Run deployment from your local machine**:
   ```bash
   chmod +x deploy/deploy.sh
   ./deploy/deploy.sh
   ```

### Step 3: Configure Application

1. **SSH to your EC2 instance**:
   ```bash
   ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip
   cd /opt/linkedin-bot
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Add Google Sheets credentials**:
   ```bash
   # Copy your service account JSON file
   nano config/credentials.json
   # Paste your Google Sheets service account credentials
   ```

4. **Configure LinkedIn cookies** (Optional):
   ```bash
   # If you have existing LinkedIn session cookies
   # Replace the empty pickle file with your cookies
   ```

### Step 4: Set Up System Service

1. **Create systemd service**:
   ```bash
   cd /opt/linkedin-bot
   chmod +x deploy/systemd_service.sh
   ./deploy/systemd_service.sh
   ```

2. **Start the service**:
   ```bash
   sudo systemctl start linkedin-bot
   sudo systemctl status linkedin-bot
   ```

### Step 5: Monitor and Manage

1. **View logs**:
   ```bash
   # System logs
   sudo journalctl -u linkedin-bot -f
   
   # Application logs (if configured)
   tail -f /opt/linkedin-bot/logs/*.log
   ```

2. **Service management**:
   ```bash
   # Start service
   sudo systemctl start linkedin-bot
   
   # Stop service
   sudo systemctl stop linkedin-bot
   
   # Restart service
   sudo systemctl restart linkedin-bot
   
   # Check status
   sudo systemctl status linkedin-bot
   ```

## 🔒 Security Considerations

### 1. Secure Your Instance
```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow from your-ip-address
```

### 2. Protect Sensitive Files
```bash
# Set proper permissions
chmod 600 config/credentials.json
chmod 600 config/cookies.pkl
```

### 3. Use IAM Roles (Recommended)
- Instead of storing credentials in files, use EC2 IAM roles
- Attach appropriate Google Cloud service account roles

## 📊 Monitoring and Alerts

### CloudWatch Integration
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

### Log Monitoring
```bash
# Monitor application logs
tail -f /opt/linkedin-bot/logs/*.log

# Monitor system resource usage
htop
```

## 🔄 Updates and Maintenance

### Updating the Application
1. **From local machine**:
   ```bash
   ./deploy/deploy.sh
   ```

2. **On EC2 instance**:
   ```bash
   sudo systemctl restart linkedin-bot
   ```

### Backup Important Data
```bash
# Backup configuration and logs
tar -czf backup-$(date +%Y%m%d).tar.gz config/ logs/

# Upload to S3 (optional)
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/
```

## 🐛 Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Issues**:
   ```bash
   # Reinstall Chrome
   sudo apt-get purge google-chrome-stable
   # Re-run ec2_setup.sh
   ```

2. **Permission Issues**:
   ```bash
   sudo chown -R $USER:$USER /opt/linkedin-bot
   chmod +x /opt/linkedin-bot/venv/bin/python
   ```

3. **Virtual Display Issues**:
   ```bash
   # Check if Xvfb is running
   ps aux | grep Xvfb
   
   # Restart display
   sudo pkill Xvfb
   Xvfb :99 -screen 0 1024x768x24 &
   ```

4. **Memory Issues**:
   ```bash
   # Check memory usage
   free -h
   
   # Add swap if needed
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Log Locations
- **System logs**: `sudo journalctl -u linkedin-bot`
- **Application logs**: `/opt/linkedin-bot/logs/`
- **Chrome logs**: Check application logs for browser errors

## 💰 Cost Optimization

### Instance Sizing
- **Development**: `t3.micro` (1 vCPU, 1GB RAM) - Free tier eligible
- **Production**: `t3.medium` (2 vCPU, 4GB RAM) - Recommended
- **High volume**: `t3.large` (2 vCPU, 8GB RAM)

### Scheduling
- Use EC2 Instance Scheduler to run only during business hours
- Consider Spot Instances for cost savings (with proper error handling)

## 📞 Support

For issues with deployment:
1. Check the troubleshooting section above
2. Review system and application logs
3. Ensure all prerequisites are met
4. Verify network connectivity and security groups

---

**⚠️ Important**: This bot interacts with LinkedIn. Ensure you comply with LinkedIn's Terms of Service and use appropriate rate limiting to avoid account restrictions. 