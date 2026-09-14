"""
Filtering module for CareerCrawl.
Provides functions to filter saved listing data by various criteria.
"""

from utils.helpers import parse_stipend


def filter_by_job_type(data, job_type):
    """Filter listings by job type (Internship/Job)."""
    return [item for item in data if item.get("job_type", "").lower() == job_type.lower()]


def filter_by_skills(data, skills):
    """
    Filter listings that contain ANY of the specified skills.
    Args:
        data: List of listing dicts
        skills: List of skill strings to match (case-insensitive)
    """
    skills_lower = [s.lower() for s in skills]
    filtered = []
    for item in data:
        item_skills = [s.lower() for s in item.get("skills", [])]
        if any(s in item_skills for s in skills_lower):
            filtered.append(item)
    return filtered


def filter_by_location(data, location):
    """Filter listings by location (case-insensitive, partial match)."""
    location_lower = location.lower()
    return [
        item for item in data
        if location_lower in item.get("location", "").lower()
    ]


def filter_by_stipend_range(data, min_stipend=0, max_stipend=float('inf')):
    """
    Filter listings by stipend range.
    Parses the stipend_salary field and filters by min/max values.
    """
    filtered = []
    for item in data:
        stipend_value = parse_stipend(item.get("stipend_salary", ""))
        if min_stipend <= stipend_value <= max_stipend:
            filtered.append(item)
    return filtered


def filter_by_title_keyword(data, keyword):
    """Filter listings where the title contains the keyword (case-insensitive)."""
    keyword_lower = keyword.lower()
    return [
        item for item in data
        if keyword_lower in item.get("title", "").lower()
    ]


def filter_by_source(data, source):
    """Filter listings by source website."""
    return [
        item for item in data
        if item.get("source", "").lower() == source.lower()
    ]


def apply_filters(data, filters_dict):
    """
    Apply multiple filters at once.
    Args:
        data: List of listing dicts
        filters_dict: Dict with optional keys:
            - job_type: str
            - skills: list of str
            - location: str
            - min_stipend: int
            - max_stipend: int
            - title_keyword: str
            - source: str
    Returns:
        Filtered list of listings
    """
    result = data

    if "job_type" in filters_dict and filters_dict["job_type"]:
        result = filter_by_job_type(result, filters_dict["job_type"])

    if "skills" in filters_dict and filters_dict["skills"]:
        result = filter_by_skills(result, filters_dict["skills"])

    if "location" in filters_dict and filters_dict["location"]:
        result = filter_by_location(result, filters_dict["location"])

    if "min_stipend" in filters_dict or "max_stipend" in filters_dict:
        min_s = filters_dict.get("min_stipend", 0)
        max_s = filters_dict.get("max_stipend", float('inf'))
        result = filter_by_stipend_range(result, min_s, max_s)

    if "title_keyword" in filters_dict and filters_dict["title_keyword"]:
        result = filter_by_title_keyword(result, filters_dict["title_keyword"])

    if "source" in filters_dict and filters_dict["source"]:
        result = filter_by_source(result, filters_dict["source"])

    return result
