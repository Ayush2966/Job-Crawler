#!/usr/bin/env python3
"""
Job Crawler Setup and Installation Script
"""
import os
import sys
import subprocess
import logging

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    print("⚙️ Setting up environment configuration...")
    
    if not os.path.exists(".env"):
        if os.path.exists("env_template.txt"):
            print("📝 Creating .env file from template...")
            with open("env_template.txt", "r") as template:
                content = template.read()
            
            with open(".env", "w") as env_file:
                env_file.write(content)
            
            print("✅ .env file created. Please edit it with your configuration.")
            print("📋 Required configurations:")
            print("   - EMAIL_SENDER: Your email address")
            print("   - EMAIL_RECIPIENT: Where to send job alerts")
            print("   - SENDGRID_API_KEY: Get from sendgrid.com (recommended)")
            print("   - Or EMAIL_PASSWORD: Gmail app password (fallback)")
        else:
            print("❌ env_template.txt not found")
            return False
    else:
        print("ℹ️ .env file already exists")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["logs", "data"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ Created {directory}/")
    
    return True

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    try:
        # Test imports
        sys.path.insert(0, os.path.abspath('.'))
        from src.database.db_handler import init_db
        from src.scraper.linkedin_scraper import scrape_linkedin_software_jobs
        from src.email_sender.email_sender import send_email
        
        print("✅ All imports successful")
        
        # Test database initialization
        init_db()
        print("✅ Database initialization successful")
        
        return True
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Job Crawler Setup")
    print("=" * 50)
    
    steps = [
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Testing installation", test_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your email configuration")
    print("2. Get SendGrid API key from sendgrid.com (recommended)")
    print("3. Or setup Gmail app password")
    print("4. Run: python src/main.py")
    print("\n🔧 Optional configurations:")
    print("- Adjust salary range (MIN_SALARY, MAX_SALARY)")
    print("- Set preferred locations (PREFERRED_LOCATIONS)")
    print("- Add blacklisted companies (BLACKLISTED_COMPANIES)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
