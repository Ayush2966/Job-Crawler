import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
from datetime import datetime
from config.config import Config

def scrape_linkedin_software_jobs():
    """Enhanced LinkedIn scraper with better data extraction"""
    headers = {
        "User-Agent": Config.USER_AGENT,
        "Referer": "https://www.linkedin.com/jobs/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    jobs = []
    search_query = "software engineer"
    location_query = "India"
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    
    try:
        logging.info("Starting LinkedIn scraper...")
        
        for page in range(0, 3):  # Scrape first 3 pages (75 jobs)
            params = {
                "keywords": search_query,
                "location": location_query,
                "start": page * 25,
                "position": 1,
                "pageNum": 0
            }
            
            logging.info(f"Scraping LinkedIn page {page + 1}")
            response = requests.get(base_url, headers=headers, params=params)
            
            if response.status_code != 200:
                logging.warning(f"LinkedIn returned status {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for job in soup.find_all("li"):
                try:
                    job_data = extract_linkedin_job_data(job)
                    if job_data and is_india_job(job_data['location']):
                        jobs.append(job_data)
                        logging.info(f"Found LinkedIn job: {job_data['title']} at {job_data['company']}")
                except Exception as e:
                    logging.warning(f"Error processing LinkedIn job: {e}")
                    continue
            
            # Random delay between pages
            time.sleep(random.uniform(2, 4))
        
        logging.info(f"LinkedIn scraper found {len(jobs)} jobs")
        return jobs
    
    except Exception as e:
        logging.error(f"LinkedIn Scraping Error: {str(e)}")
        return []

def extract_linkedin_job_data(job_element):
    """Extract enhanced job data from LinkedIn job element"""
    try:
        # Basic elements
        title_elem = job_element.find("h3", class_="base-search-card__title")
        company_elem = job_element.find("h4", class_="base-search-card__subtitle")
        location_elem = job_element.find("span", class_="job-search-card__location")
        url_elem = job_element.find("a", class_="base-card__full-link")
        
        if not all([title_elem, company_elem, location_elem, url_elem]):
            return None
        
        title = title_elem.text.strip()
        company = company_elem.text.strip()
        location = location_elem.text.strip()
        url = url_elem["href"].split('?')[0]
        
        # Enhanced data extraction
        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "source": "LinkedIn",
            "scraped_date": datetime.utcnow()
        }
        
        # Try to extract salary information
        salary_info = extract_salary_from_text(title + " " + company)
        if salary_info:
            job_data.update(salary_info)
        
        # Try to extract experience information
        experience_info = extract_experience_from_text(title + " " + company)
        if experience_info:
            job_data.update(experience_info)
        
        # Determine job type
        job_type = determine_job_type(title, company, location)
        job_data["job_type"] = job_type
        job_data["is_remote"] = "remote" in job_type.lower()
        
        # Try to extract company size/industry from company name
        company_info = extract_company_info(company)
        if company_info:
            job_data.update(company_info)
        
        return job_data
        
    except Exception as e:
        logging.warning(f"Error extracting LinkedIn job data: {e}")
        return None

def extract_salary_from_text(text):
    """Extract salary information from text"""
    salary_patterns = [
        r'₹\s*(\d+(?:\.\d+)?)\s*-\s*₹\s*(\d+(?:\.\d+)?)\s*(?:LPA|Lakh|Lac)',
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:LPA|Lakh|Lac)',
        r'₹\s*(\d+(?:\.\d+)?)\s*(?:LPA|Lakh|Lac)',
        r'(\d+(?:\.\d+)?)\s*(?:LPA|Lakh|Lac)'
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return {
                    'salary_min': float(groups[0]),
                    'salary_max': float(groups[1]),
                    'salary_text': match.group(0),
                    'salary_currency': 'INR'
                }
            elif len(groups) == 1:
                return {
                    'salary_min': float(groups[0]),
                    'salary_max': None,
                    'salary_text': match.group(0),
                    'salary_currency': 'INR'
                }
    
    return None

def extract_experience_from_text(text):
    """Extract experience information from text"""
    exp_patterns = [
        r'(\d+)\s*-\s*(\d+)\s*years?',
        r'(\d+)\+?\s*years?',
        r'(\d+)\s*to\s*(\d+)\s*years?'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return {
                    'experience_min': int(groups[0]),
                    'experience_max': int(groups[1]),
                    'experience_text': match.group(0)
                }
            elif len(groups) == 1:
                return {
                    'experience_min': int(groups[0]),
                    'experience_max': None,
                    'experience_text': match.group(0)
                }
    
    return None

def determine_job_type(title, company, location):
    """Determine job type based on title, company, and location"""
    text = f"{title} {company} {location}".lower()
    
    if any(word in text for word in ['remote', 'work from home', 'wfh']):
        return 'Remote'
    elif any(word in text for word in ['contract', 'contractor', 'freelance']):
        return 'Contract'
    elif any(word in text for word in ['intern', 'internship']):
        return 'Internship'
    elif any(word in text for word in ['part-time', 'part time']):
        return 'Part-time'
    else:
        return 'Full-time'

def extract_company_info(company_name):
    """Extract company information based on company name"""
    company_lower = company_name.lower()
    
    # Determine company size based on name patterns
    if any(word in company_lower for word in ['startup', 'tech', 'innovations', 'solutions']):
        company_size = 'Startup'
    elif any(word in company_lower for word in ['corp', 'corporation', 'enterprise', 'global']):
        company_size = 'Enterprise'
    else:
        company_size = 'Mid-size'
    
    # Determine industry based on company name
    if any(word in company_lower for word in ['tech', 'software', 'it', 'digital']):
        industry = 'Technology'
    elif any(word in company_lower for word in ['bank', 'finance', 'fintech']):
        industry = 'Finance'
    elif any(word in company_lower for word in ['health', 'medical', 'pharma']):
        industry = 'Healthcare'
    else:
        industry = 'Technology'  # Default for software jobs
    
    return {
        'company_size': company_size,
        'company_industry': industry
    }

def is_india_job(location):
    """Check if job is India-based"""
    india_cities = [
        "Bangalore", "Bengaluru", "Mumbai", "Delhi", "Hyderabad", 
        "Chennai", "Pune", "Kolkata", "Noida", "Gurgaon", 
        "Gurugram", "Ahmedabad", "India", "Remote"
    ]
    
    location_lower = location.lower()
    return any(city.lower() in location_lower for city in india_cities)

# For backward compatibility
scrape_linkedin_software_jobs_india = scrape_linkedin_software_jobs