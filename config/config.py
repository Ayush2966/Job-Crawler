import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URI = "sqlite:///jobs.db"
    
    # Email Configuration - SendGrid (more reliable than Gmail)
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    
    # Fallback to Gmail if SendGrid not configured
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    # Enhanced User Agent with rotation
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    REQUEST_DELAY = 2
    
    # Proxy Configuration
    PROXY_LIST = os.getenv("PROXY_LIST", "").split(",") if os.getenv("PROXY_LIST") else []
    USE_PROXY_ROTATION = os.getenv("USE_PROXY_ROTATION", "false").lower() == "true"
    
    # Selenium Configuration
    SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
    SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", "30"))
    
    # Job Filtering
    MIN_SALARY = int(os.getenv("MIN_SALARY", "0"))
    MAX_SALARY = int(os.getenv("MAX_SALARY", "9999999"))
    PREFERRED_LOCATIONS = os.getenv("PREFERRED_LOCATIONS", "Bangalore,Mumbai,Delhi,Hyderabad,Chennai,Pune").split(",")
    BLACKLISTED_COMPANIES = os.getenv("BLACKLISTED_COMPANIES", "").split(",") if os.getenv("BLACKLISTED_COMPANIES") else []
    
    # Multi-Channel Notifications
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Scheduling
    ENABLE_SCHEDULING = os.getenv("ENABLE_SCHEDULING", "false").lower() == "true"
    DEFAULT_NOTIFICATION_FREQUENCY = os.getenv("DEFAULT_NOTIFICATION_FREQUENCY", "daily")
    
    # Advanced Features
    ENABLE_USER_PROFILES = os.getenv("ENABLE_USER_PROFILES", "true").lower() == "true"
    ENABLE_JOB_SCORING = os.getenv("ENABLE_JOB_SCORING", "true").lower() == "true"
    ENABLE_MULTI_CHANNEL = os.getenv("ENABLE_MULTI_CHANNEL", "true").lower() == "true"