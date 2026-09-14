"""
Hybrid Scraper for CareerCrawl.
Orchestrates between RequestsScraper (primary) and SeleniumScraper (fallback).
"""

import json
import sys
import os
from rich.console import Console

from scraper.requests_scraper import RequestsScraper
from scraper.selenium_scraper import SeleniumScraper

# Fix Windows console encoding for emoji/unicode
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

console = Console(force_terminal=True)


class HybridScraper:
    """
    Hybrid scraping system that tries BeautifulSoup first,
    then falls back to Selenium if the primary method fails.
    """

    def __init__(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)

        self.requests_scraper = RequestsScraper(self.config)
        self.selenium_scraper = None  # Lazy-loaded

    def scrape(self, keyword, job_type="internship", location=None):
        """
        Scrape listings using the hybrid approach.
        
        Args:
            keyword: Search keyword (e.g., 'Python', 'Data Science')
            job_type: 'internship' or 'job'
            location: Optional location filter
            
        Returns:
            Tuple of (results_list, method_used_string)
        """
        # Try primary method first: requests + BeautifulSoup
        try:
            console.print("[dim]>> Attempting scrape with requests + BeautifulSoup...[/dim]")
            results = self.requests_scraper.scrape(keyword, job_type, location)

            if results:
                console.print(f"[green][OK] Successfully scraped {len(results)} listings with BeautifulSoup[/green]")
                return results, "BeautifulSoup"

        except Exception as e:
            console.print(f"[yellow][!] BeautifulSoup failed: {e}[/yellow]")
            console.print("[dim]>> Switching to Selenium fallback...[/dim]")

        # Fallback to Selenium
        try:
            if self.selenium_scraper is None:
                self.selenium_scraper = SeleniumScraper(self.config)

            results = self.selenium_scraper.scrape(keyword, job_type, location)

            if results:
                console.print(f"[green][OK] Successfully scraped {len(results)} listings with Selenium[/green]")
                return results, "Selenium"

        except ImportError as e:
            console.print(f"[red][X] Selenium not available: {e}[/red]")
        except Exception as e:
            console.print(f"[red][X] Selenium also failed: {e}[/red]")

        # Both methods failed
        return [], "Failed"