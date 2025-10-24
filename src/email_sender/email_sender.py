import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import Config

def send_email_sendgrid(new_jobs):
    """Send email using SendGrid API (recommended)"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        if not Config.SENDGRID_API_KEY:
            logging.warning("SendGrid API key not configured, falling back to Gmail")
            return send_email_gmail(new_jobs)
        
        # Create email content
        subject = f"🔥 {len(new_jobs)} New Job Alerts!"
        
        html_content = create_html_email_content(new_jobs)
        text_content = create_text_email_content(new_jobs)
        
        message = Mail(
            from_email=Config.EMAIL_SENDER,
            to_emails=Config.EMAIL_RECIPIENT,
            subject=subject,
            html_content=html_content,
            plain_text_content=text_content
        )
        
        sg = SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
        response = sg.send(message)
        
        logging.info(f"Email sent successfully via SendGrid. Status: {response.status_code}")
        return True
        
    except Exception as e:
        logging.error(f"SendGrid email failed: {str(e)}")
        logging.info("Falling back to Gmail...")
        return send_email_gmail(new_jobs)

def send_email_gmail(new_jobs):
    """Fallback email using Gmail SMTP"""
    try:
        sender_email = Config.EMAIL_SENDER
        password = Config.EMAIL_PASSWORD
        recipient_email = Config.EMAIL_RECIPIENT

        if not all([sender_email, password, recipient_email]):
            logging.error("Gmail credentials not configured")
            return False

        msg = MIMEMultipart()
        msg["Subject"] = f"🔥 {len(new_jobs)} New Job Alerts!"
        msg["From"] = sender_email
        msg["To"] = recipient_email

        body = create_text_email_content(new_jobs)
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        
        logging.info("Email sent successfully via Gmail")
        return True
        
    except Exception as e:
        logging.error(f"Gmail email failed: {str(e)}")
        return False

def create_html_email_content(new_jobs):
    """Create rich HTML email content"""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .job-card {{ 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 10px 0; 
                background-color: #f9f9f9;
            }}
            .job-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
            .company {{ color: #7f8c8d; font-size: 14px; }}
            .location {{ color: #95a5a6; font-size: 12px; }}
            .apply-btn {{ 
                background-color: #3498db; 
                color: white; 
                padding: 8px 16px; 
                text-decoration: none; 
                border-radius: 4px; 
                display: inline-block;
                margin-top: 10px;
            }}
            .stats {{ background-color: #ecf0f1; padding: 10px; border-radius: 4px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h2>🚀 New Job Alerts!</h2>
        <div class="stats">
            <strong>Found {len(new_jobs)} new opportunities</strong><br>
            Sources: {', '.join(set(job.get('source', 'Unknown') for job in new_jobs))}
        </div>
    """
    
    for job in new_jobs:
        salary_info = f"💰 {job.get('salary', 'Salary not specified')}" if job.get('salary') else ""
        experience = f"📈 {job.get('experience', 'Experience not specified')}" if job.get('experience') else ""
        
        html += f"""
        <div class="job-card">
            <div class="job-title">📢 {job['title']}</div>
            <div class="company">🏢 {job['company']}</div>
            <div class="location">📍 {job['location']}</div>
            {f'<div>{salary_info}</div>' if salary_info else ''}
            {f'<div>{experience}</div>' if experience else ''}
            <a href="{job['url']}" class="apply-btn">Apply Now</a>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    return html

def create_text_email_content(new_jobs):
    """Create plain text email content"""
    body = f"🚀 New Job Alerts!\n\nFound {len(new_jobs)} new opportunities\n"
    body += f"Sources: {', '.join(set(job.get('source', 'Unknown') for job in new_jobs))}\n\n"
    
    for job in new_jobs:
        body += f"📢 {job['title']}\n"
        body += f"🏢 {job['company']}\n"
        body += f"📍 {job['location']}\n"
        
        if job.get('salary'):
            body += f"💰 {job['salary']}\n"
        if job.get('experience'):
            body += f"📈 {job['experience']}\n"
            
        body += f"🔗 Apply here: {job['url']}\n\n"
    
    return body

def send_email(new_jobs):
    """Main email sending function with fallback support"""
    if not new_jobs:
        logging.info("No new jobs to send")
        return True
    
    # Try SendGrid first, fallback to Gmail
    return send_email_sendgrid(new_jobs)