"""
Statistics module for CareerCrawl.
Computes summary statistics on scraped listing data.
"""

from collections import Counter
from utils.helpers import parse_stipend, is_remote


def compute_statistics(data):
    """
    Compute comprehensive statistics for a list of listings.
    Returns a dict with all computed stats.
    """
    if not data:
        return {"total": 0}

    stats = {
        "total": len(data),
        "most_common_skills": get_most_common_skills(data),
        "average_stipend": get_average_stipend(data),
        "location_distribution": get_location_distribution(data),
        "remote_vs_onsite": get_remote_vs_onsite(data),
    }
    return stats


def get_most_common_skills(data, top_n=10):
    """Return the top N most common skills across all listings."""
    all_skills = []
    for item in data:
        skills = item.get("skills", [])
        if isinstance(skills, list):
            all_skills.extend([s.strip() for s in skills if s.strip()])
        elif isinstance(skills, str):
            all_skills.extend([s.strip() for s in skills.split(",") if s.strip()])

    if not all_skills:
        return []

    counter = Counter(all_skills)
    return counter.most_common(top_n)


def get_average_stipend(data):
    """Calculate the average stipend from listings (ignoring unpaid/N/A)."""
    stipends = []
    for item in data:
        value = parse_stipend(item.get("stipend_salary", ""))
        if value > 0:
            stipends.append(value)

    if not stipends:
        return "N/A"

    avg = sum(stipends) / len(stipends)
    return f"₹{avg:,.0f}/month (from {len(stipends)} paid listings)"


def get_location_distribution(data, top_n=8):
    """Return the distribution of locations across listings."""
    locations = []
    for item in data:
        loc = item.get("location", "N/A").strip()
        if loc:
            locations.append(loc)

    if not locations:
        return []

    counter = Counter(locations)
    return counter.most_common(top_n)


def get_remote_vs_onsite(data):
    """Count remote vs onsite listings."""
    remote_count = 0
    onsite_count = 0

    for item in data:
        location = item.get("location", "")
        if is_remote(location):
            remote_count += 1
        else:
            onsite_count += 1

    return {"remote": remote_count, "onsite": onsite_count}
