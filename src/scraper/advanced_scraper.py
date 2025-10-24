"""
Advanced Job Scraper with Selenium and Anti-Detection Features
"""
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from config.config import Config
import re
from datetime import datetime

class AdvancedScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with anti-detection features"""
        try:
            chrome_options = Options()
            
            # Anti-detection settings
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            user_agent = self.ua.random
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Headless mode if configured
            if Config.SELENIUM_HEADLESS:
                chrome_options.add_argument("--headless")
            
            # Window size randomization
            chrome_options.add_argument(f"--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}")
            
            # Additional stealth options
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            
            # Setup driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logging.info("Selenium driver initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to setup Selenium driver: {e}")
            raise
    
    def human_like_delay(self, min_delay=1, max_delay=3):
        """Add human-like delays"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def scroll_page(self, scrolls=3):
        """Scroll page to load dynamic content"""
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.human_like_delay(1, 2)
    
    def extract_salary_info(self, text):
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
                        'salary_text': match.group(0)
                    }
                elif len(groups) == 1:
                    return {
                        'salary_min': float(groups[0]),
                        'salary_max': None,
                        'salary_text': match.group(0)
                    }
        
        return None
    
    def extract_experience_info(self, text):
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
    
    def extract_job_type(self, text):
        """Extract job type from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['remote', 'work from home', 'wfh']):
            return 'Remote'
        elif any(word in text_lower for word in ['contract', 'contractor', 'freelance']):
            return 'Contract'
        elif any(word in text_lower for word in ['intern', 'internship']):
            return 'Internship'
        else:
            return 'Full-time'
    
    def scrape_glassdoor_advanced(self):
        """Advanced Glassdoor scraper using Selenium"""
        logging.info("Starting advanced Glassdoor scraper...")
        
        jobs = []
        try:
            # Navigate to Glassdoor
            url = "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=software+engineer&locT=N&locId=115"
            self.driver.get(url)
            self.human_like_delay(3, 5)
            
            # Handle potential popups/cookies
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]"))
                )
                cookie_button.click()
                self.human_like_delay(1, 2)
            except:
                logging.info("No cookie popup found or already handled")
            
            # Scroll to load content
            self.scroll_page(3)
            
            # Find job listings
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-test='job-listing']")
            
            if not job_elements:
                # Try alternative selectors
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".react-job-listing")
            
            logging.info(f"Found {len(job_elements)} job elements")
            
            for job_element in job_elements[:20]:  # Limit to first 20 jobs
                try:
                    job_data = self.extract_job_data_glassdoor(job_element)
                    if job_data and self.is_india_job(job_data['location']):
                        jobs.append(job_data)
                        logging.info(f"Extracted: {job_data['title']} at {job_data['company']}")
                    
                except Exception as e:
                    logging.warning(f"Error extracting job data: {e}")
                    continue
            
            logging.info(f"Successfully extracted {len(jobs)} jobs from Glassdoor")
            
        except Exception as e:
            logging.error(f"Glassdoor scraping error: {e}")
        
        return jobs
    
    def extract_job_data_glassdoor(self, job_element):
        """Extract job data from Glassdoor job element"""
        try:
            # Title
            title_elem = job_element.find_element(By.CSS_SELECTOR, "[data-test='job-title']")
            title = title_elem.text.strip()
            
            # Company
            company_elem = job_element.find_element(By.CSS_SELECTOR, "[data-test='employer-name']")
            company = company_elem.text.strip()
            
            # Location
            location_elem = job_element.find_element(By.CSS_SELECTOR, "[data-test='job-location']")
            location = location_elem.text.strip()
            
            # URL
            url_elem = job_element.find_element(By.CSS_SELECTOR, "a")
            url = url_elem.get_attribute('href')
            
            # Try to get salary info
            salary_info = None
            try:
                salary_elem = job_element.find_element(By.CSS_SELECTOR, "[data-test='detailSalary']")
                salary_info = self.extract_salary_info(salary_elem.text)
            except:
                pass
            
            # Try to get experience info
            experience_info = None
            try:
                # Look for experience in job description or other elements
                desc_elem = job_element.find_element(By.CSS_SELECTOR, "[data-test='jobDescription']")
                experience_info = self.extract_experience_info(desc_elem.text)
            except:
                pass
            
            # Determine job type
            job_type = self.extract_job_type(title + " " + company)
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'source': 'Glassdoor',
                'job_type': job_type,
                'is_remote': 'remote' in job_type.lower(),
                'scraped_date': datetime.utcnow()
            }
            
            # Add salary info if found
            if salary_info:
                job_data.update(salary_info)
            
            # Add experience info if found
            if experience_info:
                job_data.update(experience_info)
            
            return job_data
            
        except Exception as e:
            logging.warning(f"Error extracting job data from element: {e}")
            return None
    
    def scrape_indeed_advanced(self):
        """Advanced Indeed scraper using Selenium"""
        logging.info("Starting advanced Indeed scraper...")
        
        jobs = []
        try:
            # Navigate to Indeed
            url = "https://www.indeed.com/jobs?q=software+engineer&l=India"
            self.driver.get(url)
            self.human_like_delay(3, 5)
            
            # Scroll to load content
            self.scroll_page(2)
            
            # Find job listings
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
            
            logging.info(f"Found {len(job_elements)} job elements on Indeed")
            
            for job_element in job_elements[:15]:  # Limit to first 15 jobs
                try:
                    job_data = self.extract_job_data_indeed(job_element)
                    if job_data and self.is_india_job(job_data['location']):
                        jobs.append(job_data)
                        logging.info(f"Extracted: {job_data['title']} at {job_data['company']}")
                    
                except Exception as e:
                    logging.warning(f"Error extracting Indeed job data: {e}")
                    continue
            
            logging.info(f"Successfully extracted {len(jobs)} jobs from Indeed")
            
        except Exception as e:
            logging.error(f"Indeed scraping error: {e}")
        
        return jobs
    
    def extract_job_data_indeed(self, job_element):
        """Extract job data from Indeed job element"""
        try:
            # Title
            title_elem = job_element.find_element(By.CSS_SELECTOR, ".jobTitle a")
            title = title_elem.text.strip()
            
            # Company
            company_elem = job_element.find_element(By.CSS_SELECTOR, ".companyName")
            company = company_elem.text.strip()
            
            # Location
            location_elem = job_element.find_element(By.CSS_SELECTOR, ".companyLocation")
            location = location_elem.text.strip()
            
            # URL
            url_elem = job_element.find_element(By.CSS_SELECTOR, ".jobTitle a")
            url = url_elem.get_attribute('href')
            
            # Try to get salary info
            salary_info = None
            try:
                salary_elem = job_element.find_element(By.CSS_SELECTOR, ".salary-snippet")
                salary_info = self.extract_salary_info(salary_elem.text)
            except:
                pass
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'source': 'Indeed',
                'job_type': 'Full-time',
                'is_remote': False,
                'scraped_date': datetime.utcnow()
            }
            
            # Add salary info if found
            if salary_info:
                job_data.update(salary_info)
            
            return job_data
            
        except Exception as e:
            logging.warning(f"Error extracting Indeed job data: {e}")
            return None
    
    def is_india_job(self, location):
        """Check if job is India-based"""
        india_cities = [
            "Bangalore", "Bengaluru", "Mumbai", "Delhi", "Hyderabad", 
            "Chennai", "Pune", "Kolkata", "Noida", "Gurgaon", 
            "Gurugram", "Ahmedabad", "India", "Remote"
        ]
        
        location_lower = location.lower()
        return any(city.lower() in location_lower for city in india_cities)
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed")

# Convenience functions for backward compatibility
def scrape_glassdoor_advanced():
    """Scrape Glassdoor using advanced Selenium methods"""
    scraper = AdvancedScraper()
    try:
        jobs = scraper.scrape_glassdoor_advanced()
        return jobs
    finally:
        scraper.close()

def scrape_indeed_advanced():
    """Scrape Indeed using advanced Selenium methods"""
    scraper = AdvancedScraper()
    try:
        jobs = scraper.scrape_indeed_advanced()
        return jobs
    finally:
        scraper.close()

# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Glassdoor scraper
    print("Testing Glassdoor scraper...")
    glassdoor_jobs = scrape_glassdoor_advanced()
    print(f"Found {len(glassdoor_jobs)} jobs from Glassdoor")
    
    # Test Indeed scraper
    print("Testing Indeed scraper...")
    indeed_jobs = scrape_indeed_advanced()
    print(f"Found {len(indeed_jobs)} jobs from Indeed")
