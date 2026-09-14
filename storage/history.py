"""
Search history logger for CareerCrawl.
Maintains a local log of all searches performed.
"""

import json
import os
from datetime import datetime


class SearchHistory:
    """Manages the search history log."""

    HISTORY_FILE = os.path.join("saved", "search_history.json")

    @staticmethod
    def log_search(keyword, job_type, location, result_count, method_used):
        """
        Log a search to the history file.
        
        Args:
            keyword: Search keyword used
            job_type: 'Internship' or 'Job'
            location: Location filter used (or None)
            result_count: Number of results found
            method_used: 'BeautifulSoup', 'Selenium', or 'Failed'
        """
        entry = {
            "keyword": keyword,
            "job_type": job_type,
            "location": location or "Any",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result_count": result_count,
            "method_used": method_used,
        }

        history = SearchHistory.load_history()
        history.append(entry)

        # Ensure directory exists
        os.makedirs(os.path.dirname(SearchHistory.HISTORY_FILE), exist_ok=True)

        with open(SearchHistory.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    @staticmethod
    def load_history():
        """Load the search history from file."""
        if not os.path.exists(SearchHistory.HISTORY_FILE):
            return []

        try:
            with open(SearchHistory.HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    @staticmethod
    def get_recent(count=10):
        """Get the most recent N search history entries."""
        history = SearchHistory.load_history()
        return history[-count:] if len(history) > count else history

    @staticmethod
    def clear_history():
        """Clear all search history."""
        if os.path.exists(SearchHistory.HISTORY_FILE):
            os.remove(SearchHistory.HISTORY_FILE)
