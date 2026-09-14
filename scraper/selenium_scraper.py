"""
Selenium scraper for Internshala.
Backup scraping method - used when BeautifulSoup fails.
Handles JavaScript-rendered content.
"""

import time
import random
import re
from bs4 import BeautifulSoup
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from utils.helpers import build_internshala_url


class SeleniumScraper:
    """Scrapes Internshala using Selenium (fallback method for JS-rendered content)."""

    def __init__(self, config):
        self.config = config
        self.method_name = "Selenium"

        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not installed. Install with: pip install selenium")

    def _create_driver(self):
        """Create a Chrome WebDriver with anti-detection options."""
        options = Options()

        if self.config.get("headless_mode", True):
            options.add_argument("--headless=new")

        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Random user agent
        from utils.helpers import get_random_user_agent
        options.add_argument(f"user-agent={get_random_user_agent()}")

        driver = webdriver.Chrome(options=options)

        # Hide webdriver property
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        return driver

    def scrape(self, keyword, job_type="internship", location=None):
        """
        Scrape listings from Internshala using Selenium.
        
        Args:
            keyword: Search keyword
            job_type: 'internship' or 'job'
            location: Optional location filter
            
        Returns:
            List of listing dicts matching the PRD data schema
            
        Raises:
            Exception if Selenium scraping also fails
        """
        url = build_internshala_url(keyword, job_type, location)
        driver = None

        try:
            driver = self._create_driver()
            driver.get(url)

            # Wait for listings to load
            time.sleep(random.uniform(3, 5))

            # Try to wait for listing cards
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "individual_internship"))
                )
            except Exception:
                pass  # Continue even if wait times out

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            max_results = self.config.get("results_per_search", 5)
            cards = soup.find_all('div', class_='individual_internship', limit=max_results)

            if not cards:
                raise ValueError("No listing cards found with Selenium either.")

            return self._extract_data(cards, keyword, job_type)

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _extract_data(self, cards, keyword, job_type):
        """Extract structured data from listing cards (same logic as RequestsScraper)."""
        results = []

        for index, card in enumerate(cards):
            try:
                data = self._extract_single_card(card, index, keyword, job_type)
                results.append(data)
            except Exception:
                continue

        if not results:
            raise ValueError("Failed to extract data from any listing card via Selenium.")

        return results

    def _extract_single_card(self, card, index, keyword, job_type):
        """Extract data from a single listing card."""

        # Title and Apply Link
        title = "N/A"
        apply_link = "N/A"
        title_elem = card.find('a', class_='job-title-href')
        if not title_elem:
            title_elem = card.find('h3', class_='heading_4_5')
            if title_elem and title_elem.find('a'):
                title_elem = title_elem.find('a')

        if title_elem:
            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            if href:
                apply_link = f"https://internshala.com{href}" if href.startswith('/') else href

        # Company Name
        company = "N/A"
        company_elem = card.find('p', class_='company-name')
        if not company_elem:
            company_elem = card.find('div', class_='company_name')
        if company_elem:
            company = company_elem.get_text(strip=True)

        # Location
        location = "N/A"
        loc_elem = card.find('div', class_='locations')
        if not loc_elem:
            loc_elem = card.find('a', class_='location_link')
        if not loc_elem:
            loc_elem = card.find(id='location_names')
        if loc_elem:
            location = loc_elem.get_text(strip=True)

        # Stipend / Salary
        stipend = "N/A"
        stipend_elem = card.find('span', class_='stipend')
        if not stipend_elem:
            stipend_elem = card.find('span', class_='salary')
        if stipend_elem:
            stipend = stipend_elem.get_text(strip=True)

        # Duration
        duration = "N/A"
        for item in card.find_all('div', class_='row-1-item'):
            txt = item.get_text(strip=True)
            if re.search(r'\d+\s*(Month|Week|Year|Day)', txt, re.IGNORECASE):
                duration = txt
                break
        if duration == "N/A":
            for item in card.find_all('div', class_='other_detail_item'):
                txt = item.get_text(strip=True)
                if re.search(r'\d+\s*(Month|Week|Year|Day)', txt, re.IGNORECASE):
                    duration = txt
                    break

        # Skills
        skills = [s.get_text(strip=True) for s in card.find_all('div', class_='job_skill') if s.get_text(strip=True)]
        if not skills:
            skills = [s.get_text(strip=True) for s in card.find_all('div', class_='round_tabs') if s.get_text(strip=True)]
        if not skills:
            skills = [keyword]

        # Posted On / Status
        posted_on = "N/A"
        status_elem = card.find('div', class_='status-info')
        if not status_elem:
            status_elem = card.find('div', class_='detail-row-2')
        if not status_elem:
            status_elem = card.find('span', class_='status-small')
        if status_elem:
            posted_on = status_elem.get_text(strip=True)

        # Description / Short Summary
        description = "N/A"
        desc_elem = card.find('div', class_='about_job')
        if not desc_elem:
            desc_elem = card.find('div', class_='internship_details')
        if desc_elem:
            description = desc_elem.get_text(strip=True)[:200]

        data = {
            "id": f"CC_{int(time.time())}_{index}",
            "title": title,
            "company": company,
            "location": location,
            "job_type": job_type.capitalize(),
            "stipend_salary": stipend,
            "duration": duration,
            "skills": skills,
            "posted_on": posted_on,
            "apply_link": apply_link,
            "description": description,
            "source": "Internshala",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method_used": self.method_name,
        }
        return data
