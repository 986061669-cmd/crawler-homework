"""
storage.py - Data storage module.
Saves parsed movie data to CSV files using pandas.
"""

import os
import pandas as pd
from typing import List, Dict
from datetime import datetime


class CSVStorage:
    """Store scraped data to CSV files."""

    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def save(self, data: List[Dict], filename: str = None) -> str:
        """
        Save a list of dicts to a CSV file.

        Args:
            data: list of movie dicts
            filename: optional custom filename (auto-generated if None)

        Returns:
            The full path of the saved CSV file.
        """
        if not data:
            print("[Storage] No data to save.")
            return ""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"douban_top250_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)
        df = pd.DataFrame(data)

        # Rename columns for readability
        column_map = {
            "rank": "Rank",
            "title": "Title",
            "title_other": "Title (Other)",
            "info": "Info",
            "rating": "Rating",
            "rating_count": "Rating Count",
            "quote": "Quote",
            "detail_url": "Detail URL",
        }
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"[Storage] Saved {len(data)} records -> {filepath}")
        return filepath

    def append(self, data: List[Dict], filepath: str) -> str:
        """
        Append data to an existing CSV file, or create new if not exists.

        Returns:
            The filepath used.
        """
        if not data:
            return filepath

        if os.path.exists(filepath):
            existing = pd.read_csv(filepath)
            new_df = pd.DataFrame(data)
            combined = pd.concat([existing, new_df], ignore_index=True)
            combined.to_csv(filepath, index=False, encoding="utf-8-sig")
            print(f"[Storage] Appended {len(data)} records -> {filepath} (total: {len(combined)})")
        else:
            self.save(data, os.path.basename(filepath))

        return filepath
