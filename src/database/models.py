from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    # Basic Information
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    company = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    url = Column(String(300), unique=True, nullable=False)
    source = Column(String(50), nullable=False)  # LinkedIn, Glassdoor, etc.
    
    # Enhanced Information
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="INR")
    salary_text = Column(String(100), nullable=True)  # "₹8-12 LPA"
    
    experience_min = Column(Integer, nullable=True)  # years
    experience_max = Column(Integer, nullable=True)
    experience_text = Column(String(50), nullable=True)  # "2-5 years"
    
    job_type = Column(String(50), nullable=True)  # Full-time, Contract, Remote
    employment_type = Column(String(50), nullable=True)  # Permanent, Contract, Internship
    
    # Job Details
    description = Column(Text, nullable=True)
    skills_required = Column(Text, nullable=True)  # JSON string of skills
    benefits = Column(Text, nullable=True)
    
    # Company Information
    company_size = Column(String(50), nullable=True)  # Startup, Mid-size, Enterprise
    company_industry = Column(String(100), nullable=True)
    company_website = Column(String(200), nullable=True)
    
    # Metadata
    posted_date = Column(DateTime, nullable=True)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_remote = Column(Boolean, default=False)
    
    # Quality Metrics
    job_score = Column(Float, default=0.0)  # AI-generated job quality score
    match_score = Column(Float, default=0.0)  # Match with user preferences
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"
    
    def to_dict(self):
        """Convert job to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'url': self.url,
            'source': self.source,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_text': self.salary_text,
            'experience_min': self.experience_min,
            'experience_max': self.experience_max,
            'experience_text': self.experience_text,
            'job_type': self.job_type,
            'employment_type': self.employment_type,
            'is_remote': self.is_remote,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'scraped_date': self.scraped_date.isoformat(),
            'job_score': self.job_score,
            'match_score': self.match_score
        }