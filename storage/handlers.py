"""
Data handlers for CareerCrawl.
Handles saving, loading, and listing of scraped data in JSON and Excel formats.
"""

import json
import os
from datetime import datetime

import pandas as pd


class DataHandler:
    """Handles all data persistence operations."""

    SAVE_DIR = "saved"

    @staticmethod
    def save_data(data, job_type):
        """
        Save scraped data to JSON and Excel files with timestamped filenames.
        
        Args:
            data: List of listing dicts
            job_type: 'internship' or 'job'
            
        Returns:
            Tuple of (json_path, excel_path) or None if no data
        """
        if not data:
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = os.path.join(DataHandler.SAVE_DIR, job_type.lower())
        os.makedirs(folder, exist_ok=True)

        # Timestamped filenames per PRD
        json_path = os.path.join(folder, f"{job_type.lower()}_{timestamp}.json")
        excel_path = os.path.join(folder, f"{job_type.lower()}_{timestamp}.xlsx")

        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Save Excel
        df = pd.DataFrame(data)
        # Convert skills list to comma-separated string for Excel
        if 'skills' in df.columns:
            df['skills'] = df['skills'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x
            )
        df.to_excel(excel_path, index=False)

        return json_path, excel_path

    @staticmethod
    def load_data(file_path):
        """
        Load data from a saved JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of listing dicts
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load data from {file_path}: {e}")

    @staticmethod
    def list_saved_files(job_type=None):
        """
        List all saved files, optionally filtered by job type.
        
        Args:
            job_type: 'internship', 'job', or None for all
            
        Returns:
            Dict with keys 'internship' and/or 'job', values are lists of
            dicts with 'filename', 'path', 'created', 'size' info
        """
        result = {}

        types_to_check = [job_type.lower()] if job_type else ["internship", "job"]

        for jtype in types_to_check:
            folder = os.path.join(DataHandler.SAVE_DIR, jtype)
            files = []

            if os.path.exists(folder):
                for filename in sorted(os.listdir(folder), reverse=True):
                    if filename.endswith('.json'):
                        filepath = os.path.join(folder, filename)
                        stat = os.stat(filepath)
                        files.append({
                            "filename": filename,
                            "path": filepath,
                            "size_kb": round(stat.st_size / 1024, 1),
                            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        })

            result[jtype] = files

        return result

    @staticmethod
    def get_file_count():
        """Get total count of saved files per type."""
        counts = {"internship": 0, "job": 0}
        for jtype in counts:
            folder = os.path.join(DataHandler.SAVE_DIR, jtype)
            if os.path.exists(folder):
                counts[jtype] = len([f for f in os.listdir(folder) if f.endswith('.json')])
        return counts