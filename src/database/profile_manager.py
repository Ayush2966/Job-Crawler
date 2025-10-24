"""
User Profile Management Functions
"""
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from .models import Base
from .user_profile import UserProfile
from config.config import Config
from sqlalchemy import create_engine

# Use the same engine as the main database
engine = create_engine(Config.DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def init_user_profiles():
    """Initialize user profiles table"""
    try:
        Base.metadata.create_all(engine)
        logging.info("User profiles table initialized")
    except Exception as e:
        logging.error(f"Failed to initialize user profiles: {e}")

def create_default_profile(email, name="Job Seeker"):
    """Create a default user profile"""
    try:
        # Check if profile already exists
        existing_profile = session.query(UserProfile).filter(UserProfile.email == email).first()
        if existing_profile:
            logging.info(f"Profile already exists for {email}")
            return existing_profile
        
        # Create default profile
        profile = UserProfile(
            name=name,
            email=email,
            current_role="Software Engineer",
            experience_years=3,
            expected_salary_min=8.0,
            expected_salary_max=20.0,
            primary_skills=["Python", "JavaScript", "React"],
            secondary_skills=["Docker", "AWS", "SQL"],
            programming_languages=["Python", "JavaScript", "Java"],
            frameworks=["Django", "React", "Spring"],
            databases=["PostgreSQL", "MongoDB"],
            cloud_platforms=["AWS", "Azure"],
            preferred_locations=["Bangalore", "Mumbai", "Remote"],
            preferred_job_types=["Full-time", "Remote"],
            preferred_company_sizes=["Startup", "Mid-size", "Enterprise"],
            preferred_industries=["Technology", "Finance"],
            blacklisted_companies=[],
            whitelisted_companies=[],
            email_notifications=True,
            slack_notifications=False,
            discord_notifications=False,
            notification_frequency="daily",
            min_job_score=50.0,
            min_match_score=60.0
        )
        
        session.add(profile)
        session.commit()
        
        logging.info(f"Created default profile for {email}")
        return profile
        
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to create profile: {e}")
        return None

def get_user_profile(email):
    """Get user profile by email"""
    try:
        profile = session.query(UserProfile).filter(UserProfile.email == email).first()
        return profile
    except Exception as e:
        logging.error(f"Failed to get profile: {e}")
        return None

def update_user_profile(email, **kwargs):
    """Update user profile"""
    try:
        profile = session.query(UserProfile).filter(UserProfile.email == email).first()
        if not profile:
            logging.warning(f"Profile not found for {email}")
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.utcnow()
        session.commit()
        
        logging.info(f"Updated profile for {email}")
        return profile
        
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to update profile: {e}")
        return None

def get_all_active_profiles():
    """Get all active user profiles"""
    try:
        profiles = session.query(UserProfile).filter(UserProfile.is_active == True).all()
        return profiles
    except Exception as e:
        logging.error(f"Failed to get profiles: {e}")
        return []

def filter_jobs_for_user(jobs, user_profile):
    """Filter jobs based on user profile"""
    if not user_profile:
        return jobs
    
    filtered_jobs = []
    for job in jobs:
        if user_profile.should_receive_job(job):
            # Calculate match score
            job['match_score'] = user_profile.calculate_job_match_score(job)
            filtered_jobs.append(job)
    
    # Sort by match score
    filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    return filtered_jobs

def get_user_preferences_summary():
    """Get summary of all user preferences for system-wide filtering"""
    try:
        profiles = get_all_active_profiles()
        
        if not profiles:
            return {
                'preferred_locations': Config.PREFERRED_LOCATIONS,
                'min_salary': Config.MIN_SALARY,
                'max_salary': Config.MAX_SALARY,
                'blacklisted_companies': Config.BLACKLISTED_COMPANIES
            }
        
        # Aggregate preferences from all users
        all_locations = set()
        all_blacklisted = set()
        min_salaries = []
        max_salaries = []
        
        for profile in profiles:
            if profile.preferred_locations:
                all_locations.update(profile.preferred_locations)
            if profile.blacklisted_companies:
                all_blacklisted.update(profile.blacklisted_companies)
            if profile.expected_salary_min:
                min_salaries.append(profile.expected_salary_min)
            if profile.expected_salary_max:
                max_salaries.append(profile.expected_salary_max)
        
        return {
            'preferred_locations': list(all_locations) if all_locations else Config.PREFERRED_LOCATIONS,
            'min_salary': min(min_salaries) if min_salaries else Config.MIN_SALARY,
            'max_salary': max(max_salaries) if max_salaries else Config.MAX_SALARY,
            'blacklisted_companies': list(all_blacklisted) if all_blacklisted else Config.BLACKLISTED_COMPANIES
        }
        
    except Exception as e:
        logging.error(f"Failed to get user preferences summary: {e}")
        return {
            'preferred_locations': Config.PREFERRED_LOCATIONS,
            'min_salary': Config.MIN_SALARY,
            'max_salary': Config.MAX_SALARY,
            'blacklisted_companies': Config.BLACKLISTED_COMPANIES
        }
