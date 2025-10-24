"""
User Profile Management System
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    
    # Basic Information
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    
    # Professional Information
    current_role = Column(String(100), nullable=True)
    experience_years = Column(Integer, nullable=True)
    current_salary = Column(Float, nullable=True)
    expected_salary_min = Column(Float, nullable=True)
    expected_salary_max = Column(Float, nullable=True)
    
    # Skills and Technologies
    primary_skills = Column(JSON, nullable=True)  # ["Python", "React", "AWS"]
    secondary_skills = Column(JSON, nullable=True)  # ["Docker", "Kubernetes"]
    programming_languages = Column(JSON, nullable=True)  # ["Python", "JavaScript", "Java"]
    frameworks = Column(JSON, nullable=True)  # ["Django", "React", "Spring"]
    databases = Column(JSON, nullable=True)  # ["PostgreSQL", "MongoDB", "Redis"]
    cloud_platforms = Column(JSON, nullable=True)  # ["AWS", "Azure", "GCP"]
    
    # Preferences
    preferred_locations = Column(JSON, nullable=True)  # ["Bangalore", "Mumbai", "Remote"]
    preferred_job_types = Column(JSON, nullable=True)  # ["Full-time", "Remote", "Contract"]
    preferred_company_sizes = Column(JSON, nullable=True)  # ["Startup", "Mid-size", "Enterprise"]
    preferred_industries = Column(JSON, nullable=True)  # ["Technology", "Finance", "Healthcare"]
    
    # Blacklists and Whitelists
    blacklisted_companies = Column(JSON, nullable=True)  # ["Company A", "Company B"]
    whitelisted_companies = Column(JSON, nullable=True)  # ["Google", "Microsoft"]
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    slack_notifications = Column(Boolean, default=False)
    discord_notifications = Column(Boolean, default=False)
    notification_frequency = Column(String(20), default="daily")  # hourly, daily, weekly
    
    # Job Matching Preferences
    min_job_score = Column(Float, default=50.0)  # Minimum job quality score
    min_match_score = Column(Float, default=60.0)  # Minimum match score
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'current_role': self.current_role,
            'experience_years': self.experience_years,
            'current_salary': self.current_salary,
            'expected_salary_min': self.expected_salary_min,
            'expected_salary_max': self.expected_salary_max,
            'primary_skills': self.primary_skills or [],
            'secondary_skills': self.secondary_skills or [],
            'programming_languages': self.programming_languages or [],
            'frameworks': self.frameworks or [],
            'databases': self.databases or [],
            'cloud_platforms': self.cloud_platforms or [],
            'preferred_locations': self.preferred_locations or [],
            'preferred_job_types': self.preferred_job_types or [],
            'preferred_company_sizes': self.preferred_company_sizes or [],
            'preferred_industries': self.preferred_industries or [],
            'blacklisted_companies': self.blacklisted_companies or [],
            'whitelisted_companies': self.whitelisted_companies or [],
            'email_notifications': self.email_notifications,
            'slack_notifications': self.slack_notifications,
            'discord_notifications': self.discord_notifications,
            'notification_frequency': self.notification_frequency,
            'min_job_score': self.min_job_score,
            'min_match_score': self.min_match_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def calculate_job_match_score(self, job):
        """Calculate how well a job matches this user profile"""
        score = 0.0
        max_score = 100.0
        
        # Location match (25 points)
        if self.preferred_locations:
            job_location = job.get('location', '').lower()
            for preferred_loc in self.preferred_locations:
                if preferred_loc.lower() in job_location:
                    score += 25
                    break
        
        # Salary match (20 points)
        if self.expected_salary_min and self.expected_salary_max:
            job_salary_min = job.get('salary_min')
            job_salary_max = job.get('salary_max')
            
            if job_salary_min and job_salary_max:
                avg_job_salary = (job_salary_min + job_salary_max) / 2
                avg_expected_salary = (self.expected_salary_min + self.expected_salary_max) / 2
                
                # Calculate salary match percentage
                if avg_job_salary >= self.expected_salary_min:
                    if avg_job_salary <= self.expected_salary_max:
                        score += 20  # Perfect match
                    else:
                        # Job pays more than expected (good!)
                        score += 15
                else:
                    # Job pays less than expected
                    salary_diff = (self.expected_salary_min - avg_job_salary) / self.expected_salary_min
                    if salary_diff <= 0.2:  # Within 20%
                        score += 10
        
        # Job type match (15 points)
        if self.preferred_job_types:
            job_type = job.get('job_type', '').lower()
            for preferred_type in self.preferred_job_types:
                if preferred_type.lower() in job_type:
                    score += 15
                    break
        
        # Company size match (10 points)
        if self.preferred_company_sizes:
            company_size = job.get('company_size', '').lower()
            for preferred_size in self.preferred_company_sizes:
                if preferred_size.lower() in company_size:
                    score += 10
                    break
        
        # Skills match (20 points)
        if self.primary_skills:
            job_title = job.get('title', '').lower()
            job_description = job.get('description', '').lower()
            job_text = f"{job_title} {job_description}"
            
            matched_skills = 0
            for skill in self.primary_skills:
                if skill.lower() in job_text:
                    matched_skills += 1
            
            if matched_skills > 0:
                skill_match_ratio = matched_skills / len(self.primary_skills)
                score += skill_match_ratio * 20
        
        # Experience match (10 points)
        if self.experience_years and job.get('experience_min') and job.get('experience_max'):
            if self.experience_years >= job['experience_min'] and self.experience_years <= job['experience_max']:
                score += 10
        
        return min(score, max_score)
    
    def should_receive_job(self, job):
        """Determine if user should receive this job notification"""
        # Check minimum scores
        if job.get('job_score', 0) < self.min_job_score:
            return False
        
        match_score = self.calculate_job_match_score(job)
        if match_score < self.min_match_score:
            return False
        
        # Check blacklisted companies
        if self.blacklisted_companies:
            company_name = job.get('company', '').lower()
            for blacklisted in self.blacklisted_companies:
                if blacklisted.lower() in company_name:
                    return False
        
        # Check whitelisted companies (if any)
        if self.whitelisted_companies:
            company_name = job.get('company', '').lower()
            for whitelisted in self.whitelisted_companies:
                if whitelisted.lower() in company_name:
                    return True  # Always send whitelisted companies
        
        return True
