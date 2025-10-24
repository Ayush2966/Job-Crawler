"""
Multi-Channel Notification System
"""
import logging
import requests
import json
from config.config import Config

def send_slack_notification(new_jobs, webhook_url=None):
    """Send job alerts to Slack channel"""
    try:
        if not webhook_url:
            webhook_url = Config.SLACK_WEBHOOK_URL
        
        if not webhook_url:
            logging.warning("Slack webhook URL not configured")
            return False
        
        # Create Slack message
        message = create_slack_message(new_jobs)
        
        # Send to Slack
        response = requests.post(webhook_url, json=message, timeout=10)
        
        if response.status_code == 200:
            logging.info(f"✅ Slack notification sent successfully for {len(new_jobs)} jobs")
            return True
        else:
            logging.error(f"❌ Slack notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Slack notification error: {e}")
        return False

def create_slack_message(new_jobs):
    """Create formatted Slack message"""
    message = {
        "text": f"🚀 *{len(new_jobs)} New Job Alerts!*",
        "attachments": []
    }
    
    # Add summary attachment
    sources = set(job.get('source', 'Unknown') for job in new_jobs)
    summary_text = f"Found {len(new_jobs)} new opportunities from: {', '.join(sources)}"
    
    summary_attachment = {
        "color": "good",
        "fields": [
            {
                "title": "📊 Summary",
                "value": summary_text,
                "short": False
            }
        ]
    }
    message["attachments"].append(summary_attachment)
    
    # Add job attachments (limit to 10 to avoid message length limits)
    for job in new_jobs[:10]:
        job_attachment = create_slack_job_attachment(job)
        message["attachments"].append(job_attachment)
    
    # Add footer if there are more jobs
    if len(new_jobs) > 10:
        footer_attachment = {
            "color": "warning",
            "text": f"... and {len(new_jobs) - 10} more jobs! Check your email for the complete list.",
            "mrkdwn_in": ["text"]
        }
        message["attachments"].append(footer_attachment)
    
    return message

def create_slack_job_attachment(job):
    """Create Slack attachment for a single job"""
    # Determine color based on job score
    job_score = job.get('job_score', 0)
    if job_score >= 80:
        color = "good"  # Green
    elif job_score >= 60:
        color = "warning"  # Yellow
    else:
        color = "danger"  # Red
    
    # Create fields
    fields = [
        {
            "title": "📢 Job Title",
            "value": job['title'],
            "short": False
        },
        {
            "title": "🏢 Company",
            "value": job['company'],
            "short": True
        },
        {
            "title": "📍 Location",
            "value": job['location'],
            "short": True
        }
    ]
    
    # Add salary if available
    if job.get('salary_text'):
        fields.append({
            "title": "💰 Salary",
            "value": job['salary_text'],
            "short": True
        })
    
    # Add experience if available
    if job.get('experience_text'):
        fields.append({
            "title": "📈 Experience",
            "value": job['experience_text'],
            "short": True
        })
    
    # Add job score
    if job.get('job_score'):
        fields.append({
            "title": "⭐ Job Score",
            "value": f"{job['job_score']:.1f}/100",
            "short": True
        })
    
    # Add match score
    if job.get('match_score'):
        fields.append({
            "title": "🎯 Match Score",
            "value": f"{job['match_score']:.1f}/100",
            "short": True
        })
    
    attachment = {
        "color": color,
        "fields": fields,
        "actions": [
            {
                "type": "button",
                "text": "Apply Now",
                "url": job['url'],
                "style": "primary"
            }
        ],
        "footer": f"Source: {job.get('source', 'Unknown')}",
        "ts": int(job.get('scraped_date', 0).timestamp()) if job.get('scraped_date') else None
    }
    
    return attachment

def send_discord_notification(new_jobs, webhook_url=None):
    """Send job alerts to Discord channel"""
    try:
        if not webhook_url:
            webhook_url = Config.DISCORD_WEBHOOK_URL
        
        if not webhook_url:
            logging.warning("Discord webhook URL not configured")
            return False
        
        # Create Discord message
        message = create_discord_message(new_jobs)
        
        # Send to Discord
        response = requests.post(webhook_url, json=message, timeout=10)
        
        if response.status_code == 204:  # Discord returns 204 for success
            logging.info(f"✅ Discord notification sent successfully for {len(new_jobs)} jobs")
            return True
        else:
            logging.error(f"❌ Discord notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Discord notification error: {e}")
        return False

def create_discord_message(new_jobs):
    """Create formatted Discord message"""
    # Create embed
    embed = {
        "title": f"🚀 {len(new_jobs)} New Job Alerts!",
        "color": 0x00ff00,  # Green color
        "fields": [],
        "footer": {
            "text": "Job Crawler Bot"
        },
        "timestamp": new_jobs[0].get('scraped_date').isoformat() if new_jobs and new_jobs[0].get('scraped_date') else None
    }
    
    # Add summary
    sources = set(job.get('source', 'Unknown') for job in new_jobs)
    embed["fields"].append({
        "name": "📊 Summary",
        "value": f"Found {len(new_jobs)} new opportunities from: {', '.join(sources)}",
        "inline": False
    })
    
    # Add top jobs (limit to 5 for Discord)
    for i, job in enumerate(new_jobs[:5]):
        job_text = f"**{job['title']}** at {job['company']}\n"
        job_text += f"📍 {job['location']}\n"
        
        if job.get('salary_text'):
            job_text += f"💰 {job['salary_text']}\n"
        if job.get('experience_text'):
            job_text += f"📈 {job['experience_text']}\n"
        if job.get('job_score'):
            job_text += f"⭐ Score: {job['job_score']:.1f}/100\n"
        
        job_text += f"[Apply Here]({job['url']})"
        
        embed["fields"].append({
            "name": f"Job {i+1}",
            "value": job_text,
            "inline": False
        })
    
    # Add footer if there are more jobs
    if len(new_jobs) > 5:
        embed["fields"].append({
            "name": "ℹ️ More Jobs",
            "value": f"... and {len(new_jobs) - 5} more jobs! Check your email for the complete list.",
            "inline": False
        })
    
    message = {
        "embeds": [embed]
    }
    
    return message

def send_telegram_notification(new_jobs, bot_token=None, chat_id=None):
    """Send job alerts to Telegram channel"""
    try:
        if not bot_token:
            bot_token = Config.TELEGRAM_BOT_TOKEN
        if not chat_id:
            chat_id = Config.TELEGRAM_CHAT_ID
        
        if not bot_token or not chat_id:
            logging.warning("Telegram bot token or chat ID not configured")
            return False
        
        # Create Telegram message
        message = create_telegram_message(new_jobs)
        
        # Send to Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            logging.info(f"✅ Telegram notification sent successfully for {len(new_jobs)} jobs")
            return True
        else:
            logging.error(f"❌ Telegram notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Telegram notification error: {e}")
        return False

def create_telegram_message(new_jobs):
    """Create formatted Telegram message"""
    message = f"🚀 *{len(new_jobs)} New Job Alerts!*\n\n"
    
    # Add summary
    sources = set(job.get('source', 'Unknown') for job in new_jobs)
    message += f"📊 Found {len(new_jobs)} new opportunities from: {', '.join(sources)}\n\n"
    
    # Add top jobs (limit to 8 for Telegram)
    for i, job in enumerate(new_jobs[:8]):
        message += f"*{i+1}. {job['title']}*\n"
        message += f"🏢 {job['company']}\n"
        message += f"📍 {job['location']}\n"
        
        if job.get('salary_text'):
            message += f"💰 {job['salary_text']}\n"
        if job.get('experience_text'):
            message += f"📈 {job['experience_text']}\n"
        if job.get('job_score'):
            message += f"⭐ Score: {job['job_score']:.1f}/100\n"
        
        message += f"[Apply Here]({job['url']})\n\n"
    
    # Add footer if there are more jobs
    if len(new_jobs) > 8:
        message += f"ℹ️ ... and {len(new_jobs) - 8} more jobs! Check your email for the complete list."
    
    return message

def send_multi_channel_notifications(new_jobs, user_profile=None):
    """Send notifications to all configured channels"""
    if not new_jobs:
        logging.info("No new jobs to send notifications for")
        return True
    
    results = {}
    
    # Email notification (always try)
    try:
        from src.email_sender.email_sender import send_email
        results['email'] = send_email(new_jobs)
    except Exception as e:
        logging.error(f"Email notification failed: {e}")
        results['email'] = False
    
    # Slack notification
    if user_profile and user_profile.slack_notifications:
        try:
            results['slack'] = send_slack_notification(new_jobs)
        except Exception as e:
            logging.error(f"Slack notification failed: {e}")
            results['slack'] = False
    
    # Discord notification
    if user_profile and user_profile.discord_notifications:
        try:
            results['discord'] = send_discord_notification(new_jobs)
        except Exception as e:
            logging.error(f"Discord notification failed: {e}")
            results['discord'] = False
    
    # Telegram notification (if configured globally)
    try:
        results['telegram'] = send_telegram_notification(new_jobs)
    except Exception as e:
        logging.error(f"Telegram notification failed: {e}")
        results['telegram'] = False
    
    # Log results
    successful_channels = [channel for channel, success in results.items() if success]
    failed_channels = [channel for channel, success in results.items() if not success]
    
    if successful_channels:
        logging.info(f"✅ Notifications sent successfully via: {', '.join(successful_channels)}")
    if failed_channels:
        logging.warning(f"⚠️ Notifications failed via: {', '.join(failed_channels)}")
    
    return any(results.values())  # Return True if at least one channel succeeded

# For testing
if __name__ == "__main__":
    # Test with sample job data
    sample_jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "Bangalore",
            "url": "https://example.com/job1",
            "source": "LinkedIn",
            "salary_text": "₹12-18 LPA",
            "experience_text": "3-5 years",
            "job_score": 85.0,
            "match_score": 90.0,
            "scraped_date": datetime.now()
        }
    ]
    
    print("Testing multi-channel notifications...")
    send_multi_channel_notifications(sample_jobs)

