# app/data_handler.py

import fastf1
from fastf1 import get_event_schedule
import pandas as pd
from typing import List, Dict, Optional
import requests

class DataFetchError(Exception):
    """Custom exception for data fetching errors"""
    pass

def get_lap_data(year: int, grand_prix: str) -> Optional[fastf1.core.Session]:
    """
    Fetches lap data for a specific F1 race using FastF1
    
    Args:
        year: The year of the race
        grand_prix: The name of the Grand Prix
        
    Returns:
        FastF1 session data
        
    Raises:
        DataFetchError: If data cannot be fetched
    """
    try:
        # Enable FastF1 cache
        fastf1.Cache.enable_cache('cache')
        
        # Get event schedule to validate GP name
        schedule = get_event_schedule(year)
        if grand_prix not in schedule['EventName'].values:
            raise DataFetchError(f"Grand Prix '{grand_prix}' not found in {year} schedule")
        
        # Load the race session
        session = fastf1.get_session(year, grand_prix, 'R')
        session.load()
        
        if not session or not session.laps:
            raise DataFetchError(f"No lap data found for {grand_prix} {year}")
            
        return session
        
    except fastf1.exceptions.SessionNotAvailableError:
        raise DataFetchError(f"Session data not available for {grand_prix} {year}")
    except Exception as e:
        raise DataFetchError(f"Failed to fetch data: {str(e)}")

url = "http://localhost:8000/predict"
data = {
    "year": 2023,
    "grand_prix": "British Grand Prix"
}

response = requests.post(url, json=data)
print(response.json())
