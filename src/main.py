import sys
import os
import logging
from datetime import datetime

# Add this before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules
from src.database.db_handler import init_db, save_job, get_job_stats, cleanup_old_jobs
from src.database.profile_manager import init_user_profiles, create_default_profile, get_user_preferences_summary
from src.scraper.linkedin_scraper import scrape_linkedin_software_jobs
from src.scraper.glassdoor_scraper import scrape_glassdoor_software_jobs
from src.scraper.indeed_scraper import scrape_indeed
from src.scraper.advanced_scraper import scrape_glassdoor_advanced, scrape_indeed_advanced
from src.scraper.indian_job_boards import scrape_naukri_jobs, scrape_monster_india_jobs, scrape_timesjobs_jobs
from src.notifications.multi_channel import send_multi_channel_notifications
from src.email_sender.email_sender import send_email
from config.config import Config

# Create logs directory if missing
os.makedirs("logs", exist_ok=True)

# Enhanced logging configuration
logging.basicConfig(
    filename="logs/crawler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/crawler.log"),
        logging.StreamHandler()  # Also log to console
    ]
)

def scrape_all_sources():
    """Scrape jobs from all available sources"""
    all_jobs = []
    
    # LinkedIn (most reliable)
    try:
        logging.info("Starting LinkedIn scraper...")
        linkedin_jobs = scrape_linkedin_software_jobs()
        all_jobs.extend(linkedin_jobs)
        logging.info(f"LinkedIn scraper found {len(linkedin_jobs)} jobs")
    except Exception as e:
        logging.error(f"LinkedIn scraper failed: {e}")
    
    # Glassdoor - try advanced scraper first, fallback to basic
    try:
        logging.info("Starting Glassdoor scraper (advanced)...")
        glassdoor_jobs = scrape_glassdoor_advanced()
        all_jobs.extend(glassdoor_jobs)
        logging.info(f"Glassdoor advanced scraper found {len(glassdoor_jobs)} jobs")
    except Exception as e:
        logging.warning(f"Glassdoor advanced scraper failed: {e}")
        try:
            logging.info("Falling back to basic Glassdoor scraper...")
            glassdoor_jobs = scrape_glassdoor_software_jobs()
            all_jobs.extend(glassdoor_jobs)
            logging.info(f"Glassdoor basic scraper found {len(glassdoor_jobs)} jobs")
        except Exception as e2:
            logging.error(f"Glassdoor basic scraper also failed: {e2}")
    
    # Indeed - try advanced scraper first, fallback to basic
    try:
        logging.info("Starting Indeed scraper (advanced)...")
        indeed_jobs = scrape_indeed_advanced()
        all_jobs.extend(indeed_jobs)
        logging.info(f"Indeed advanced scraper found {len(indeed_jobs)} jobs")
    except Exception as e:
        logging.warning(f"Indeed advanced scraper failed: {e}")
        try:
            logging.info("Falling back to basic Indeed scraper...")
            indeed_jobs = scrape_indeed()
            all_jobs.extend(indeed_jobs)
            logging.info(f"Indeed basic scraper found {len(indeed_jobs)} jobs")
        except Exception as e2:
            logging.error(f"Indeed basic scraper also failed: {e2}")
    
    # Indian Job Boards
    try:
        logging.info("Starting Naukri scraper...")
        naukri_jobs = scrape_naukri_jobs()
        all_jobs.extend(naukri_jobs)
        logging.info(f"Naukri scraper found {len(naukri_jobs)} jobs")
    except Exception as e:
        logging.error(f"Naukri scraper failed: {e}")
    
    try:
        logging.info("Starting Monster India scraper...")
        monster_jobs = scrape_monster_india_jobs()
        all_jobs.extend(monster_jobs)
        logging.info(f"Monster India scraper found {len(monster_jobs)} jobs")
    except Exception as e:
        logging.error(f"Monster India scraper failed: {e}")
    
    try:
        logging.info("Starting TimesJobs scraper...")
        timesjobs_jobs = scrape_timesjobs_jobs()
        all_jobs.extend(timesjobs_jobs)
        logging.info(f"TimesJobs scraper found {len(timesjobs_jobs)} jobs")
    except Exception as e:
        logging.error(f"TimesJobs scraper failed: {e}")
    
    return all_jobs

def filter_and_score_jobs(jobs):
    """Filter jobs based on user preferences and score them"""
    filtered_jobs = []
    
    for job in jobs:
        # Basic filtering
        if not job.get('title') or not job.get('company'):
            continue
        
        # Location filtering
        if Config.PREFERRED_LOCATIONS and not any(
            loc.lower() in job.get('location', '').lower() 
            for loc in Config.PREFERRED_LOCATIONS
        ):
            continue
        
        # Company blacklist filtering
        if Config.BLACKLISTED_COMPANIES and any(
            blacklisted.lower() in job.get('company', '').lower()
            for blacklisted in Config.BLACKLISTED_COMPANIES
        ):
            continue
        
        # Salary filtering
        if job.get('salary_min') and job.get('salary_min') < Config.MIN_SALARY:
            continue
        if job.get('salary_max') and job.get('salary_max') > Config.MAX_SALARY:
            continue
        
        # Calculate job score
        job['job_score'] = calculate_job_score(job)
        job['match_score'] = calculate_match_score(job)
        
        filtered_jobs.append(job)
    
    # Sort by match score
    filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    return filtered_jobs

def calculate_job_score(job):
    """Calculate job quality score"""
    score = 0.0
    
    # Salary score (0-30 points)
    if job.get('salary_min') and job.get('salary_max'):
        avg_salary = (job['salary_min'] + job['salary_max']) / 2
        if avg_salary >= 15:  # 15+ LPA
            score += 30
        elif avg_salary >= 10:  # 10-15 LPA
            score += 20
        elif avg_salary >= 5:   # 5-10 LPA
            score += 10
    
    # Company size score (0-20 points)
    company_size = job.get('company_size', '').lower()
    if 'enterprise' in company_size:
        score += 20
    elif 'mid-size' in company_size:
        score += 15
    elif 'startup' in company_size:
        score += 10
    
    # Job type score (0-15 points)
    job_type = job.get('job_type', '').lower()
    if 'full-time' in job_type:
        score += 15
    elif 'remote' in job_type:
        score += 12
    elif 'contract' in job_type:
        score += 8
    
    # Remote work bonus (0-10 points)
    if job.get('is_remote'):
        score += 10
    
    # Experience level score (0-15 points)
    if job.get('experience_min') and job.get('experience_max'):
        avg_exp = (job['experience_min'] + job['experience_max']) / 2
        if 2 <= avg_exp <= 5:  # Sweet spot
            score += 15
        elif avg_exp <= 2:
            score += 10
        else:
            score += 5
    
    # Source reliability score (0-10 points)
    source = job.get('source', '').lower()
    if source == 'linkedin':
        score += 10
    elif source == 'glassdoor':
        score += 8
    elif source == 'indeed':
        score += 6
    
    return min(score, 100.0)  # Cap at 100

def calculate_match_score(job):
    """Calculate match score based on user preferences"""
    score = 0.0
    
    # Location match (0-40 points)
    location = job.get('location', '').lower()
    for preferred_loc in Config.PREFERRED_LOCATIONS:
        if preferred_loc.lower() in location:
            score += 40
            break
    
    # Salary match (0-30 points)
    if job.get('salary_min') and Config.MIN_SALARY <= job['salary_min'] <= Config.MAX_SALARY:
        score += 30
    elif job.get('salary_max') and Config.MIN_SALARY <= job['salary_max'] <= Config.MAX_SALARY:
        score += 20
    
    # Remote work preference (0-20 points)
    if job.get('is_remote'):
        score += 20
    
    # Job type preference (0-10 points)
    if job.get('job_type') == 'Full-time':
        score += 10
    
    return min(score, 100.0)  # Cap at 100

def main():
    """Main application function"""
    start_time = datetime.now()
    logging.info("=" * 50)
    logging.info("Job Crawler Starting...")
    logging.info(f"Start time: {start_time}")
    
    try:
        # Initialize databases
        init_db()
        if Config.ENABLE_USER_PROFILES:
            init_user_profiles()
        
        # Create default profile if none exists
        if Config.ENABLE_USER_PROFILES and Config.EMAIL_RECIPIENT:
            create_default_profile(Config.EMAIL_RECIPIENT)
        
        # Scrape all sources
        all_jobs = scrape_all_sources()
        logging.info(f"Total jobs scraped: {len(all_jobs)}")
        
        # Filter and score jobs
        filtered_jobs = filter_and_score_jobs(all_jobs)
        logging.info(f"Jobs after filtering: {len(filtered_jobs)}")
        
        # Save jobs and detect new ones
        new_jobs = []
        for job in filtered_jobs:
            try:
                is_new = save_job(job)
                if is_new:
                    new_jobs.append(job)
            except Exception as e:
                logging.error(f"Failed to save job: {e}")
        
        # Send notifications
        if new_jobs:
            if Config.ENABLE_MULTI_CHANNEL:
                # Send multi-channel notifications
                success = send_multi_channel_notifications(new_jobs)
                if success:
                    logging.info(f"✅ Sent {len(new_jobs)} new jobs via multi-channel notifications")
                else:
                    logging.error("❌ Failed to send multi-channel notifications")
            else:
                # Fallback to email only
                success = send_email(new_jobs)
                if success:
                    logging.info(f"✅ Sent {len(new_jobs)} new jobs via email")
                else:
                    logging.error("❌ Failed to send email alerts")
        else:
            logging.info("ℹ️ No new jobs found across all platforms")
        
        # Get and log statistics
        stats = get_job_stats()
        logging.info(f"📊 Job Statistics: {stats}")
        
        # Cleanup old jobs
        cleaned = cleanup_old_jobs(30)  # Mark jobs older than 30 days as inactive
        if cleaned > 0:
            logging.info(f"🧹 Cleaned up {cleaned} old jobs")
        
    except Exception as e:
        logging.error(f"❌ Critical error: {str(e)}")
        raise
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"⏱️ Job Crawler completed in {duration}")
        logging.info("=" * 50)

if __name__ == "__main__":
    main()