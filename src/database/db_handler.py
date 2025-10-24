from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from .models import Base, Job
from .user_profile import Base as UserProfileBase
from config.config import Config
import logging
from datetime import datetime, timedelta
import json

engine = create_engine(Config.DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def init_db():
    """Initialize database and create tables"""
    try:
        # Create all tables from both models
        Base.metadata.create_all(engine)
        UserProfileBase.metadata.create_all(engine)
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise

def save_job(job_data):
    """Save job with enhanced data model and duplicate detection"""
    try:
        # Check if job already exists
        existing_job = session.query(Job).filter(Job.url == job_data["url"]).first()
        
        if existing_job:
            # Update existing job if it's been more than 7 days
            if existing_job.scraped_date < datetime.utcnow() - timedelta(days=7):
                update_existing_job(existing_job, job_data)
                logging.info(f"Updated existing job: {job_data['title']} at {job_data['company']}")
            return False  # Not a new job
        
        # Create new job
        new_job = Job(
            # Basic Information
            title=job_data.get("title", "Unknown Title"),
            company=job_data.get("company", "Unknown Company"),
            location=job_data.get("location", "Unknown Location"),
            url=job_data["url"],
            source=job_data.get("source", "Unknown"),
            
            # Enhanced Information
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            salary_currency=job_data.get("salary_currency", "INR"),
            salary_text=job_data.get("salary_text"),
            
            experience_min=job_data.get("experience_min"),
            experience_max=job_data.get("experience_max"),
            experience_text=job_data.get("experience_text"),
            
            job_type=job_data.get("job_type"),
            employment_type=job_data.get("employment_type"),
            
            # Job Details
            description=job_data.get("description"),
            skills_required=json.dumps(job_data.get("skills_required", [])) if job_data.get("skills_required") else None,
            benefits=job_data.get("benefits"),
            
            # Company Information
            company_size=job_data.get("company_size"),
            company_industry=job_data.get("company_industry"),
            company_website=job_data.get("company_website"),
            
            # Metadata
            posted_date=job_data.get("posted_date"),
            is_remote=job_data.get("is_remote", False),
            
            # Quality Metrics
            job_score=job_data.get("job_score", 0.0),
            match_score=job_data.get("match_score", 0.0)
        )
        
        session.add(new_job)
        session.commit()
        logging.info(f"Saved new job: {job_data['title']} at {job_data['company']}")
        return True
        
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to save job: {e}")
        return False

def update_existing_job(existing_job, job_data):
    """Update existing job with new data"""
    try:
        # Update fields that might have changed
        existing_job.title = job_data.get("title", existing_job.title)
        existing_job.company = job_data.get("company", existing_job.company)
        existing_job.location = job_data.get("location", existing_job.location)
        existing_job.scraped_date = datetime.utcnow()
        
        # Update enhanced fields if provided
        if job_data.get("salary_min"):
            existing_job.salary_min = job_data["salary_min"]
        if job_data.get("salary_max"):
            existing_job.salary_max = job_data["salary_max"]
        if job_data.get("salary_text"):
            existing_job.salary_text = job_data["salary_text"]
            
        session.commit()
        
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to update job: {e}")

def get_recent_jobs(days=7):
    """Get jobs from the last N days"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        jobs = session.query(Job).filter(
            Job.scraped_date >= cutoff_date,
            Job.is_active == True
        ).order_by(Job.scraped_date.desc()).all()
        
        return [job.to_dict() for job in jobs]
    except Exception as e:
        logging.error(f"Failed to get recent jobs: {e}")
        return []

def get_jobs_by_source(source):
    """Get jobs from a specific source"""
    try:
        jobs = session.query(Job).filter(
            Job.source == source,
            Job.is_active == True
        ).order_by(Job.scraped_date.desc()).all()
        
        return [job.to_dict() for job in jobs]
    except Exception as e:
        logging.error(f"Failed to get jobs by source: {e}")
        return []

def get_job_stats():
    """Get job statistics"""
    try:
        total_jobs = session.query(Job).filter(Job.is_active == True).count()
        
        # Jobs by source
        sources = session.query(Job.source, session.query(Job).filter(Job.source == Job.source).count()).group_by(Job.source).all()
        
        # Recent jobs (last 7 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_jobs = session.query(Job).filter(Job.scraped_date >= recent_cutoff).count()
        
        return {
            "total_jobs": total_jobs,
            "recent_jobs": recent_jobs,
            "jobs_by_source": dict(sources)
        }
    except Exception as e:
        logging.error(f"Failed to get job stats: {e}")
        return {}

def cleanup_old_jobs(days=30):
    """Mark old jobs as inactive"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_jobs = session.query(Job).filter(Job.scraped_date < cutoff_date).update({"is_active": False})
        session.commit()
        
        logging.info(f"Marked {old_jobs} old jobs as inactive")
        return old_jobs
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to cleanup old jobs: {e}")
        return 0