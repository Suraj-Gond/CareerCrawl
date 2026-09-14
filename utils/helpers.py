"""
Utility helpers for CareerCrawl.
Contains User-Agent rotation, stipend parser, URL shortener, and console utilities.
"""

import random
import re

# Pool of realistic User-Agent strings for rotation (anti-blocking measure)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
]


def get_random_user_agent():
    """Return a random User-Agent string from the pool."""
    return random.choice(USER_AGENTS)


def get_realistic_headers():
    """Return a complete set of realistic browser headers with a rotated UA."""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def parse_stipend(stipend_str):
    """
    Parse stipend string like '₹10,000/month' or '₹5,000-10,000/month' into a numeric value.
    Returns the average for ranges, or the single value. Returns 0 if unparseable.
    """
    if not stipend_str or stipend_str in ("N/A", "Unpaid", ""):
        return 0

    # Remove currency symbol, commas, spaces
    cleaned = stipend_str.replace("₹", "").replace(",", "").replace(" ", "")

    # Try to find range like '5000-10000'
    range_match = re.search(r'(\d+)\s*-\s*(\d+)', cleaned)
    if range_match:
        low = int(range_match.group(1))
        high = int(range_match.group(2))
        return (low + high) // 2

    # Try single number
    single_match = re.search(r'(\d+)', cleaned)
    if single_match:
        return int(single_match.group(1))

    return 0


def shorten_url(url, max_length=40):
    """Shorten a URL for display purposes."""
    if not url or url == "N/A":
        return "N/A"
    if len(url) <= max_length:
        return url
    return url[:max_length - 3] + "..."


def build_internshala_url(keyword, job_type="internship", location=None):
    """Build the Internshala search URL from keyword, job type, and optional location."""
    keyword_slug = keyword.lower().replace(" ", "-")

    if job_type.lower() == "job":
        base = f"https://internshala.com/jobs/keywords-{keyword_slug}/"
    else:
        base = f"https://internshala.com/internships/keywords-{keyword_slug}/"

    if location and location.lower() not in ("", "any", "all"):
        location_slug = location.lower().replace(" ", "-")
        # Internshala uses 'in-<location>' in URL
        base = base.rstrip("/") + f"/in-{location_slug}/"

    return base


def is_remote(location_str):
    """Check if a location string indicates remote work."""
    if not location_str:
        return False
    remote_keywords = ["remote", "work from home", "wfh", "virtual", "anywhere"]
    return any(kw in location_str.lower() for kw in remote_keywords)
