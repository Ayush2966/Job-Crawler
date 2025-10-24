"""
Indian Job Boards Scrapers
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
from datetime import datetime
from config.config import Config

def scrape_naukri_jobs():
    """Scrape jobs from Naukri.com"""
    logging.info("Starting Naukri.com scraper...")
    
    headers = {
        "User-Agent": Config.USER_AGENT,
        "Referer": "https://www.naukri.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    jobs = []
    base_url = "https://www.naukri.com/software-engineer-jobs"
    
    try:
        response = requests.get(base_url, headers=headers)
        logging.info(f"Naukri.com response status: {response.status_code}")
        
        if response.status_code != 200:
            logging.warning(f"Naukri returned non-200 status: {response.status_code}")
            return jobs
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find job listings
        job_listings = soup.find_all("div", class_="jobTuple")
        
        if not job_listings:
            # Try alternative selectors
            job_listings = soup.find_all("div", {"data-job-id": True})
        
        logging.info(f"Found {len(job_listings)} job listings on Naukri")
        
        for job in job_listings[:20]:  # Limit to first 20 jobs
            try:
                job_data = extract_naukri_job_data(job)
                if job_data:
                    jobs.append(job_data)
                    logging.info(f"Extracted Naukri job: {job_data['title']} at {job_data['company']}")
            except Exception as e:
                logging.warning(f"Error extracting Naukri job: {e}")
                continue
        
        logging.info(f"Successfully extracted {len(jobs)} jobs from Naukri")
        
    except Exception as e:
        logging.error(f"Naukri scraping error: {e}")
    
    return jobs

def extract_naukri_job_data(job_element):
    """Extract job data from Naukri job element"""
    try:
        # Title
        title_elem = job_element.find("a", class_="title")
        if not title_elem:
            title_elem = job_element.find("a", {"data-test": "jobTitle"})
        title = title_elem.text.strip() if title_elem else "Unknown Title"
        
        # Company
        company_elem = job_element.find("a", class_="subTitle")
        if not company_elem:
            company_elem = job_element.find("div", class_="companyName")
        company = company_elem.text.strip() if company_elem else "Unknown Company"
        
        # Location
        location_elem = job_element.find("span", class_="ellipsis")
        if not location_elem:
            location_elem = job_element.find("span", {"data-test": "location"})
        location = location_elem.text.strip() if location_elem else "Unknown Location"
        
        # URL
        url_elem = job_element.find("a", class_="title")
        url = url_elem["href"] if url_elem and "href" in url_elem.attrs else ""
        
        # Salary
        salary_info = None
        salary_elem = job_element.find("span", class_="ellipsis")
        if salary_elem:
            salary_text = salary_elem.text.strip()
            salary_info = extract_salary_from_text(salary_text)
        
        # Experience
        experience_info = None
        exp_elem = job_element.find("span", {"data-test": "experience"})
        if exp_elem:
            exp_text = exp_elem.text.strip()
            experience_info = extract_experience_from_text(exp_text)
        
        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "source": "Naukri",
            "job_type": "Full-time",
            "is_remote": "remote" in location.lower(),
            "scraped_date": datetime.utcnow()
        }
        
        if salary_info:
            job_data.update(salary_info)
        if experience_info:
            job_data.update(experience_info)
        
        return job_data
        
    except Exception as e:
        logging.warning(f"Error extracting Naukri job data: {e}")
        return None

def scrape_monster_india_jobs():
    """Scrape jobs from Monster India"""
    logging.info("Starting Monster India scraper...")
    
    headers = {
        "User-Agent": Config.USER_AGENT,
        "Referer": "https://www.monsterindia.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    jobs = []
    base_url = "https://www.monsterindia.com/search/software-engineer-jobs"
    
    try:
        response = requests.get(base_url, headers=headers)
        logging.info(f"Monster India response status: {response.status_code}")
        
        if response.status_code != 200:
            logging.warning(f"Monster India returned non-200 status: {response.status_code}")
            return jobs
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find job listings
        job_listings = soup.find_all("div", class_="card-apply")
        
        if not job_listings:
            job_listings = soup.find_all("div", {"data-job-id": True})
        
        logging.info(f"Found {len(job_listings)} job listings on Monster India")
        
        for job in job_listings[:15]:  # Limit to first 15 jobs
            try:
                job_data = extract_monster_job_data(job)
                if job_data:
                    jobs.append(job_data)
                    logging.info(f"Extracted Monster job: {job_data['title']} at {job_data['company']}")
            except Exception as e:
                logging.warning(f"Error extracting Monster job: {e}")
                continue
        
        logging.info(f"Successfully extracted {len(jobs)} jobs from Monster India")
        
    except Exception as e:
        logging.error(f"Monster India scraping error: {e}")
    
    return jobs

def extract_monster_job_data(job_element):
    """Extract job data from Monster job element"""
    try:
        # Title
        title_elem = job_element.find("h3", class_="medium")
        if not title_elem:
            title_elem = job_element.find("a", {"data-test": "jobTitle"})
        title = title_elem.text.strip() if title_elem else "Unknown Title"
        
        # Company
        company_elem = job_element.find("span", class_="company")
        if not company_elem:
            company_elem = job_element.find("div", class_="companyName")
        company = company_elem.text.strip() if company_elem else "Unknown Company"
        
        # Location
        location_elem = job_element.find("span", class_="loc")
        if not location_elem:
            location_elem = job_element.find("span", {"data-test": "location"})
        location = location_elem.text.strip() if location_elem else "Unknown Location"
        
        # URL
        url_elem = job_element.find("a", {"data-test": "jobTitle"})
        url = url_elem["href"] if url_elem and "href" in url_elem.attrs else ""
        
        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "source": "Monster India",
            "job_type": "Full-time",
            "is_remote": "remote" in location.lower(),
            "scraped_date": datetime.utcnow()
        }
        
        return job_data
        
    except Exception as e:
        logging.warning(f"Error extracting Monster job data: {e}")
        return None

def scrape_timesjobs_jobs():
    """Scrape jobs from TimesJobs"""
    logging.info("Starting TimesJobs scraper...")
    
    headers = {
        "User-Agent": Config.USER_AGENT,
        "Referer": "https://www.timesjobs.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    jobs = []
    base_url = "https://www.timesjobs.com/jobsearch/software-engineer-jobs"
    
    try:
        response = requests.get(base_url, headers=headers)
        logging.info(f"TimesJobs response status: {response.status_code}")
        
        if response.status_code != 200:
            logging.warning(f"TimesJobs returned non-200 status: {response.status_code}")
            return jobs
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find job listings
        job_listings = soup.find_all("li", class_="clearfix job-bx wht-shd-bx")
        
        if not job_listings:
            job_listings = soup.find_all("div", {"data-job-id": True})
        
        logging.info(f"Found {len(job_listings)} job listings on TimesJobs")
        
        for job in job_listings[:15]:  # Limit to first 15 jobs
            try:
                job_data = extract_timesjobs_job_data(job)
                if job_data:
                    jobs.append(job_data)
                    logging.info(f"Extracted TimesJobs job: {job_data['title']} at {job_data['company']}")
            except Exception as e:
                logging.warning(f"Error extracting TimesJobs job: {e}")
                continue
        
        logging.info(f"Successfully extracted {len(jobs)} jobs from TimesJobs")
        
    except Exception as e:
        logging.error(f"TimesJobs scraping error: {e}")
    
    return jobs

def extract_timesjobs_job_data(job_element):
    """Extract job data from TimesJobs job element"""
    try:
        # Title
        title_elem = job_element.find("h2")
        if not title_elem:
            title_elem = job_element.find("a", {"data-test": "jobTitle"})
        title = title_elem.text.strip() if title_elem else "Unknown Title"
        
        # Company
        company_elem = job_element.find("h3", class_="joblist-comp-name")
        if not company_elem:
            company_elem = job_element.find("div", class_="companyName")
        company = company_elem.text.strip() if company_elem else "Unknown Company"
        
        # Location
        location_elem = job_element.find("span", class_="joblist-comp-name")
        if not location_elem:
            location_elem = job_element.find("span", {"data-test": "location"})
        location = location_elem.text.strip() if location_elem else "Unknown Location"
        
        # URL
        url_elem = job_element.find("a", {"data-test": "jobTitle"})
        url = url_elem["href"] if url_elem and "href" in url_elem.attrs else ""
        
        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "source": "TimesJobs",
            "job_type": "Full-time",
            "is_remote": "remote" in location.lower(),
            "scraped_date": datetime.utcnow()
        }
        
        return job_data
        
    except Exception as e:
        logging.warning(f"Error extracting TimesJobs job data: {e}")
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

# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Naukri scraper...")
    naukri_jobs = scrape_naukri_jobs()
    print(f"Found {len(naukri_jobs)} jobs from Naukri")
    
    print("Testing Monster India scraper...")
    monster_jobs = scrape_monster_india_jobs()
    print(f"Found {len(monster_jobs)} jobs from Monster India")
    
    print("Testing TimesJobs scraper...")
    timesjobs_jobs = scrape_timesjobs_jobs()
    print(f"Found {len(timesjobs_jobs)} jobs from TimesJobs")

