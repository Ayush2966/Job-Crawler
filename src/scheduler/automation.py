"""
Job Crawler Scheduling and Automation
"""
import schedule
import time
import logging
import threading
from datetime import datetime, timedelta
from src.main import main as run_crawler
from src.database.profile_manager import get_all_active_profiles
from config.config import Config

class JobCrawlerScheduler:
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.last_run_time = None
        self.run_count = 0
        
    def start_scheduler(self):
        """Start the automated scheduler"""
        if self.is_running:
            logging.warning("Scheduler is already running")
            return
        
        self.is_running = True
        logging.info("🚀 Starting Job Crawler Scheduler...")
        
        # Schedule jobs based on user preferences
        self.setup_schedules()
        
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logging.info("✅ Scheduler started successfully")
    
    def stop_scheduler(self):
        """Stop the automated scheduler"""
        if not self.is_running:
            logging.warning("Scheduler is not running")
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logging.info("🛑 Scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logging.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def setup_schedules(self):
        """Setup scheduled jobs based on user preferences"""
        # Clear existing schedules
        schedule.clear()
        
        # Get user preferences
        profiles = get_all_active_profiles()
        
        if not profiles:
            # Default schedule if no profiles
            self.setup_default_schedule()
            return
        
        # Schedule based on user preferences
        for profile in profiles:
            frequency = profile.notification_frequency.lower()
            
            if frequency == "hourly":
                schedule.every().hour.do(self._run_crawler_for_profile, profile.email)
            elif frequency == "daily":
                schedule.every().day.at("09:00").do(self._run_crawler_for_profile, profile.email)
                schedule.every().day.at("18:00").do(self._run_crawler_for_profile, profile.email)
            elif frequency == "weekly":
                schedule.every().monday.at("09:00").do(self._run_crawler_for_profile, profile.email)
            else:
                # Default to daily
                schedule.every().day.at("09:00").do(self._run_crawler_for_profile, profile.email)
        
        # Add system maintenance schedules
        schedule.every().day.at("02:00").do(self._cleanup_old_jobs)
        schedule.every().week.do(self._generate_weekly_report)
        
        logging.info(f"📅 Scheduled {len(schedule.jobs)} jobs")
    
    def setup_default_schedule(self):
        """Setup default schedule when no user profiles exist"""
        schedule.every().day.at("09:00").do(self._run_crawler_default)
        schedule.every().day.at("18:00").do(self._run_crawler_default)
        schedule.every().day.at("02:00").do(self._cleanup_old_jobs)
        
        logging.info("📅 Default schedule setup completed")
    
    def _run_crawler_for_profile(self, user_email):
        """Run crawler for a specific user profile"""
        try:
            logging.info(f"🔄 Running crawler for user: {user_email}")
            
            # Import here to avoid circular imports
            from src.database.profile_manager import get_user_profile, filter_jobs_for_user
            from src.database.db_handler import get_recent_jobs
            from src.notifications.multi_channel import send_multi_channel_notifications
            
            # Get user profile
            profile = get_user_profile(user_email)
            if not profile:
                logging.warning(f"Profile not found for {user_email}")
                return
            
            # Run the main crawler
            run_crawler()
            
            # Get recent jobs and filter for this user
            recent_jobs = get_recent_jobs(1)  # Last 24 hours
            filtered_jobs = filter_jobs_for_user(recent_jobs, profile)
            
            # Send notifications
            if filtered_jobs:
                send_multi_channel_notifications(filtered_jobs, profile)
            
            self.last_run_time = datetime.now()
            self.run_count += 1
            
            logging.info(f"✅ Crawler completed for {user_email}")
            
        except Exception as e:
            logging.error(f"Error running crawler for {user_email}: {e}")
    
    def _run_crawler_default(self):
        """Run crawler with default settings"""
        try:
            logging.info("🔄 Running crawler with default settings")
            run_crawler()
            
            self.last_run_time = datetime.now()
            self.run_count += 1
            
            logging.info("✅ Default crawler completed")
            
        except Exception as e:
            logging.error(f"Error running default crawler: {e}")
    
    def _cleanup_old_jobs(self):
        """Cleanup old jobs"""
        try:
            logging.info("🧹 Running job cleanup...")
            
            from src.database.db_handler import cleanup_old_jobs
            cleaned_count = cleanup_old_jobs(30)  # 30 days
            
            logging.info(f"✅ Cleaned up {cleaned_count} old jobs")
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
    
    def _generate_weekly_report(self):
        """Generate weekly job market report"""
        try:
            logging.info("📊 Generating weekly report...")
            
            from src.database.db_handler import get_job_stats
            stats = get_job_stats()
            
            # Create report message
            report = f"📈 Weekly Job Market Report\n\n"
            report += f"Total Jobs: {stats.get('total_jobs', 0)}\n"
            report += f"New Jobs This Week: {stats.get('recent_jobs', 0)}\n"
            report += f"Jobs by Source: {stats.get('jobs_by_source', {})}\n"
            
            # Send report to all users
            profiles = get_all_active_profiles()
            for profile in profiles:
                if profile.email_notifications:
                    from src.email_sender.email_sender import send_email
                    send_email([{
                        'title': 'Weekly Job Market Report',
                        'company': 'Job Crawler System',
                        'location': 'System Report',
                        'url': 'https://example.com/report',
                        'source': 'System',
                        'description': report
                    }])
            
            logging.info("✅ Weekly report generated and sent")
            
        except Exception as e:
            logging.error(f"Error generating weekly report: {e}")
    
    def get_scheduler_status(self):
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'last_run_time': self.last_run_time,
            'run_count': self.run_count,
            'scheduled_jobs': len(schedule.jobs),
            'next_run': schedule.next_run() if schedule.jobs else None
        }
    
    def run_now(self):
        """Run crawler immediately"""
        try:
            logging.info("🚀 Running crawler immediately...")
            run_crawler()
            
            self.last_run_time = datetime.now()
            self.run_count += 1
            
            logging.info("✅ Immediate crawler run completed")
            return True
            
        except Exception as e:
            logging.error(f"Error running immediate crawler: {e}")
            return False

# Global scheduler instance
scheduler = JobCrawlerScheduler()

def start_automated_crawling():
    """Start automated job crawling"""
    scheduler.start_scheduler()

def stop_automated_crawling():
    """Stop automated job crawling"""
    scheduler.stop_scheduler()

def run_crawler_now():
    """Run crawler immediately"""
    return scheduler.run_now()

def get_crawler_status():
    """Get crawler status"""
    return scheduler.get_scheduler_status()

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            start_automated_crawling()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_automated_crawling()
                
        elif command == "run":
            run_crawler_now()
            
        elif command == "status":
            status = get_crawler_status()
            print(f"Scheduler Status: {status}")
            
        else:
            print("Usage: python scheduler.py [start|run|status]")
    else:
        print("Usage: python scheduler.py [start|run|status]")

