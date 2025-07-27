"""
Fabric deployment script for LinkedIn Auto Connect Bot
Usage: fab <task_name>
"""

from fabric import task
import os


@task
def install(c):
    """Install Python packages from requirements.txt"""
    print("Installing Python packages...")
    c.run("pip3 install -r requirements.txt")
    print("✅ Packages installed successfully!")


@task
def setup(c):
    """Complete setup: install packages and create necessary directories"""
    print("🚀 Setting up LinkedIn Auto Connect Bot...")
    
    # Install packages
    install(c)
    
    # Create logs directory
    if not os.path.exists("logs"):
        os.makedirs("logs")
        print("📁 Created logs directory")
    
    # Check if config files exist
    if not os.path.exists("config/credentials.json"):
        print("⚠️  Warning: config/credentials.json not found")
        print("   Please add your Google Sheets service account credentials")
    
    print("✅ Setup complete!")


@task
def status(c):
    """Check system status and dependencies"""
    print("🔍 Checking system status...")
    
    # Check Python version
    c.run("python3 --version")
    
    # Check if Chrome is installed
    try:
        c.run("google-chrome --version", hide=True)
        print("✅ Chrome browser found")
    except:
        print("⚠️  Warning: Chrome not found")
    
    # Check if chromedriver is available
    try:
        c.run("chromedriver --version", hide=True)
        print("✅ ChromeDriver found")
    except:
        print("⚠️  Warning: ChromeDriver not found")
    
    # Check key files
    files_to_check = [
        "requirements.txt",
        "config/cookies.pkl",
        "config/credentials.json"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"⚠️  {file_path} not found")


@task
def run_bot(c):
    """Run the bot once (without scheduler)"""
    print("🤖 Running bot...")
    c.run("python3 -c 'from bot.scraper import run_bot; run_bot()'")


# GitHub Deployment Tasks
@task
def github_update(c):
    """Update application from GitHub repository"""
    print("🔄 Updating from GitHub...")
    c.run("git fetch origin")
    c.run("git pull origin main")
    
    # Reinstall dependencies in case requirements changed
    install(c)
    
    # Set proper permissions
    c.run("chmod 600 config/credentials.json", warn=True)
    c.run("chmod 600 config/cookies.pkl", warn=True)
    
    print("✅ GitHub update complete!")


# EC2 Service Management
@task
def ec2_service(c):
    """Create systemd service for the bot on EC2"""
    print("🔧 Creating systemd service...")
    c.run("chmod +x deploy/systemd_service.sh")
    c.run("./deploy/systemd_service.sh")


@task
def ec2_status(c):
    """Check EC2 service status"""
    print("📊 Checking service status...")
    c.run("sudo systemctl status linkedin-bot", warn=True)


@task
def ec2_logs(c):
    """View EC2 service logs"""
    print("📋 Viewing service logs...")
    c.run("sudo journalctl -u linkedin-bot -f")


@task
def ec2_restart(c):
    """Restart the EC2 service"""
    print("🔄 Restarting service...")
    c.run("sudo systemctl restart linkedin-bot")
    c.run("sudo systemctl status linkedin-bot")


@task
def ec2_start(c):
    """Start the EC2 service"""
    print("▶️ Starting service...")
    c.run("sudo systemctl start linkedin-bot")


@task
def ec2_stop(c):
    """Stop the EC2 service"""
    print("⏹️ Stopping service...")
    c.run("sudo systemctl stop linkedin-bot") 