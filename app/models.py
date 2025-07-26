# app/model.py

import numpy as np
import pandas as pd
from typing import List, Dict
import fastf1
fastf1.Cache.enable_cache('cache')  # Enable caching for faster subsequent loads

class PredictionError(Exception):
    """Custom exception for prediction errors"""
    pass

def predict_winner(session_data: fastf1.core.Session) -> str:
    """
    Predicts the winner of a race based on session data
    
    Args:
        session_data: FastF1 session data
        
    Returns:
        str: Predicted winner's name
        
    Raises:
        PredictionError: If prediction cannot be made
    """
    try:
        if not session_data:
            raise PredictionError("No session data available")

        # Load lap data
        laps_data = session_data.laps
        
        if laps_data.empty:
            raise PredictionError("No lap data available for prediction")
        
        # Calculate key metrics for each driver
        driver_stats = {}
        for driver in laps_data['Driver'].unique():
            driver_laps = laps_data[laps_data['Driver'] == driver]
            
            # Skip if driver has too few laps
            if len(driver_laps) < 3:
                continue
                
            # Calculate metrics
            driver_stats[driver] = {
                'avg_lap_time': driver_laps['LapTime'].mean(),
                'consistent_score': driver_laps['LapTime'].std(),  # Lower is better
                'fastest_lap': driver_laps['LapTime'].min(),
                'lap_count': len(driver_laps)
            }
        
        if not driver_stats:
            raise PredictionError("No valid driver statistics available")
            
        # Simple scoring system
        scores = {}
        for driver, stats in driver_stats.items():
            score = (
                1/stats['avg_lap_time'] * 0.4 +  # Faster average is better
                1/stats['consistent_score'] * 0.3 +  # More consistent is better
                1/stats['fastest_lap'] * 0.3  # Faster best lap is better
            )
            scores[driver] = score
            
        # Return driver with highest score
        predicted_winner = max(scores.items(), key=lambda x: x[1])[0]
        return predicted_winner
        
    except Exception as e:
        raise PredictionError(f"Failed to make prediction: {str(e)}")
