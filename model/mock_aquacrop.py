#!/usr/bin/env python3
"""
Mock AquaCrop implementation for demonstration purposes.
This simulates the AquaCrop behavior when the actual library is not available.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

class MockAquaCropModel:
    """Mock implementation of AquaCropModel for demonstration."""
    
    def __init__(self, sim_start_time, sim_end_time, weather_df, soil, crop, initial_water_content):
        self.sim_start_time = sim_start_time
        self.sim_end_time = sim_end_time
        self.weather_df = weather_df
        self.soil = soil
        self.crop = crop
        self.initial_water_content = initial_water_content
        self.results = None
        
    def run_model(self, till_termination=True):
        """Mock simulation run."""
        # Generate mock simulation results
        start_date = datetime.strptime(self.sim_start_time, "%Y/%m/%d")
        end_date = datetime.strptime(self.sim_end_time, "%Y/%m/%d")
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate mock yield data based on crop type and soil
        base_yield = self._get_base_yield()
        seasonal_variation = self._get_seasonal_variation(date_range)
        soil_multiplier = self._get_soil_multiplier()
        
        # Calculate daily yields (most will be 0, with peaks during harvest)
        daily_yields = np.zeros(len(date_range))
        
        # Add yield peaks during harvest season (spring for wheat)
        harvest_months = [4, 5, 6]  # April, May, June
        for i, date in enumerate(date_range):
            if date.month in harvest_months:
                # Add some yield during harvest season
                if np.random.random() < 0.1:  # 10% chance of yield on any given day
                    daily_yields[i] = base_yield * soil_multiplier * seasonal_variation[i] * np.random.uniform(0.8, 1.2)
        
        # Create results DataFrame
        self.results = pd.DataFrame({
            'Date': date_range,
            'Yield (tonne/ha)': daily_yields,
            'Biomass (tonne/ha)': daily_yields * 1.5,  # Biomass is typically higher than yield
            'Water Stress': np.random.uniform(0, 1, len(date_range)),
            'Temperature': np.random.uniform(15, 30, len(date_range)),
            'Precipitation': np.random.exponential(2, len(date_range))
        })
        
    def get_simulation_results(self):
        """Return simulation results."""
        return self.results
    
    def _get_base_yield(self):
        """Get base yield based on crop type."""
        crop_yields = {
            'Wheat': 3.5,
            'Maize': 4.2,
            'Rice': 3.8,
            'Barley': 2.8
        }
        return crop_yields.get(self.crop.crop_name, 3.0)
    
    def _get_soil_multiplier(self):
        """Get soil multiplier based on soil type."""
        soil_multipliers = {
            'SandyLoam': 1.0,
            'ClayLoam': 1.2,
            'SandyClay': 0.9,
            'Loam': 1.1,
            'Clay': 1.3
        }
        return soil_multipliers.get(self.soil.soil_type, 1.0)
    
    def _get_seasonal_variation(self, date_range):
        """Get seasonal variation factor."""
        variation = np.ones(len(date_range))
        for i, date in enumerate(date_range):
            # Higher variation in spring/summer
            if date.month in [3, 4, 5, 6, 7, 8]:
                variation[i] = np.random.uniform(0.8, 1.3)
            else:
                variation[i] = np.random.uniform(0.6, 1.1)
        return variation

class MockSoil:
    """Mock soil implementation."""
    def __init__(self, soil_type):
        self.soil_type = soil_type

class MockCrop:
    """Mock crop implementation."""
    def __init__(self, crop_name, planting_date):
        self.crop_name = crop_name
        self.planting_date = planting_date

class MockInitialWaterContent:
    """Mock initial water content implementation."""
    def __init__(self, value):
        self.value = value

def mock_prepare_weather(file_path):
    """Mock weather data preparation."""
    # Generate mock weather data
    start_date = datetime(1979, 1, 1)
    end_date = datetime(1985, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic weather patterns
    weather_data = []
    for date in date_range:
        # Seasonal temperature variation
        temp_base = 20 + 10 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
        temp = temp_base + np.random.normal(0, 3)
        
        # Seasonal precipitation (more in winter)
        precip_base = 2 + 1.5 * np.sin(2 * np.pi * (date.timetuple().tm_yday + 90) / 365)
        precip = max(0, precip_base + np.random.exponential(1))
        
        weather_data.append({
            'Date': date,
            'Temp': temp,
            'Precip': precip,
            'Humidity': np.random.uniform(40, 80),
            'Wind': np.random.uniform(0, 10)
        })
    
    return pd.DataFrame(weather_data)

def mock_get_filepath(filename):
    """Mock filepath function."""
    return f"mock_data/{filename}"

# Mock the AquaCrop modules
class MockAquaCropModules:
    """Mock AquaCrop modules for demonstration."""
    
    @staticmethod
    def get_modules():
        return {
            'AquaCropModel': MockAquaCropModel,
            'Soil': MockSoil,
            'Crop': MockCrop,
            'InitialWaterContent': MockInitialWaterContent,
            'prepare_weather': mock_prepare_weather,
            'get_filepath': mock_get_filepath
        }

def get_mock_aquacrop():
    """Get mock AquaCrop modules."""
    return MockAquaCropModules.get_modules()
