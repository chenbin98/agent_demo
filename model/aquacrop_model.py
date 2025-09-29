#!/usr/bin/env python3
"""
AquaCrop Wheat Yield Prediction Tool - Enhanced Version

This module provides a comprehensive tool for predicting wheat yield using the AquaCrop model.
It handles both real AquaCrop and mock implementations with full transparency.

Usage:
    python aquacrop_model_v2.py [crop_type] [planting_date] [soil_type] [sim_years]
    
Example:
    python aquacrop_model_v2.py Wheat 10/01 SandyLoam 6
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Fix for AquaCrop on macOS - ensure 'python' command is available
def setup_python_alias():
    """Set up python alias for AquaCrop compatibility."""
    try:
        # Check if python command exists
        subprocess.run(['python', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Create a temporary python alias
        python3_path = subprocess.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()
        if python3_path:
            # Add to PATH temporarily
            os.environ['PATH'] = f"{os.path.dirname(python3_path)}:{os.environ.get('PATH', '')}"
            # Create a temporary symlink in a writable directory
            temp_dir = Path.home() / '.local' / 'bin'
            temp_dir.mkdir(parents=True, exist_ok=True)
            python_link = temp_dir / 'python'
            if not python_link.exists():
                try:
                    python_link.symlink_to(python3_path)
                    os.environ['PATH'] = f"{temp_dir}:{os.environ.get('PATH', '')}"
                except (OSError, PermissionError):
                    pass  # If we can't create symlink, continue anyway

# Set up the python alias before importing AquaCrop
setup_python_alias()

def predict_yield(crop_type: str = "Wheat", 
                 planting_date: str = "10/01", 
                 soil_type: str = "SandyLoam", 
                 sim_years: int = 6) -> Dict[str, Any]:
    """
    Predict crop yield using AquaCrop model with transparent process logging.
    
    Args:
        crop_type: Type of crop (default: "Wheat")
        planting_date: Planting date in MM/DD format (default: "10/01")
        soil_type: Soil type for simulation (default: "SandyLoam")
        sim_years: Number of years to simulate (default: 6)
    
    Returns:
        Dictionary containing simulation results and yield predictions
    """
    try:
        # Try to import real AquaCrop modules
        use_mock = False
        try:
            from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
            from aquacrop.utils import prepare_weather, get_filepath
            import pandas as pd
            
            # Test if AquaCrop actually works by trying to create a simple object
            test_soil = Soil(soil_type='SandyLoam')
            print("✅ Real AquaCrop loaded successfully")
        except (ImportError, FileNotFoundError, OSError) as e:
            print(f"⚠️  Real AquaCrop not available ({e}), using mock implementation for demonstration")
            use_mock = True
            # Import mock implementation
            from mock_aquacrop import get_mock_aquacrop
            mock_modules = get_mock_aquacrop()
            AquaCropModel = mock_modules['AquaCropModel']
            Soil = mock_modules['Soil']
            Crop = mock_modules['Crop']
            InitialWaterContent = mock_modules['InitialWaterContent']
            prepare_weather = mock_modules['prepare_weather']
            get_filepath = mock_modules['get_filepath']
            import pandas as pd
        
        print(f"🌾 Starting AquaCrop {crop_type} yield simulation...")
        print(f"📅 Planting date: {planting_date}")
        print(f"🌱 Soil type: {soil_type}")
        print(f"⏱️  Simulation years: {sim_years}")
        print("-" * 50)
        
        # Step 1: Prepare weather data
        print("Step 1: Loading weather data from Tunis climate file")
        if use_mock:
            print("   Using mock weather data for demonstration")
            weather_df = prepare_weather('mock_tunis_climate.txt')
        else:
            weather_file_path = get_filepath('tunis_climate.txt')
            weather_df = prepare_weather(weather_file_path)
        print("✅ Weather data loaded successfully")
        
        # Step 2: Set up simulation parameters
        print("\nStep 2: Setting up simulation parameters")
        start_year = 1979
        end_year = start_year + sim_years - 1
        sim_start_time = f"{start_year}/10/01"
        sim_end_time = f"{end_year}/05/30"
        print(f"   Simulation period: {sim_start_time} to {sim_end_time}")
        
        # Step 3: Initialize AquaCrop model components
        print("\nStep 3: Initializing AquaCrop model components")
        
        # Create soil object
        soil = Soil(soil_type=soil_type)
        print(f"   ✅ Soil created: {soil_type}")
        
        # Create crop object
        crop = Crop(crop_type, planting_date=planting_date)
        print(f"   ✅ Crop created: {crop_type} with planting date {planting_date}")
        
        # Set initial water content
        initial_water_content = InitialWaterContent(value=['FC'])
        print("   ✅ Initial water content set to Field Capacity (FC)")
        
        # Step 4: Create and configure model
        print("\nStep 4: Creating AquaCrop model")
        model = AquaCropModel(
            sim_start_time=sim_start_time,
            sim_end_time=sim_end_time,
            weather_df=weather_df,
            soil=soil,
            crop=crop,
            initial_water_content=initial_water_content,
        )
        print("   ✅ Model created successfully")
        
        # Step 5: Run simulation
        print("\nStep 5: Running crop simulation...")
        print("   This may take a moment...")
        model.run_model(till_termination=True)
        print("   ✅ Simulation completed successfully")
        
        # Step 6: Extract results
        print("\nStep 6: Extracting simulation results")
        results = model.get_simulation_results()
        
        # Debug: Print information about the results
        print(f"   Results shape: {results.shape}")
        print(f"   Results columns: {list(results.columns)}")
        if not results.empty:
            print(f"   First few rows:")
            print(results.head())
        else:
            print("   Results DataFrame is empty!")
        
        # Calculate yield metrics from the actual results
        yield_metrics = {}
        
        # Check for different possible yield column names
        yield_column = None
        possible_yield_columns = ['Dry yield (tonne/ha)', 'Yield (tonne/ha)', 'Yield', 'yield', 'Biomass (tonne/ha)', 'Biomass']
        
        for col in possible_yield_columns:
            if col in results.columns:
                yield_column = col
                print(f"   Found yield column: {yield_column}")
                break
        
        if not results.empty and yield_column:
            # Calculate basic yield statistics
            total_yield = results[yield_column].sum()
            avg_yield = results[yield_column].mean()
            max_yield = results[yield_column].max()
            min_yield = results[yield_column].min()
            final_yield = results[yield_column].iloc[-1] if not results.empty else 0
            
            # Calculate seasonal yields (harvest periods)
            seasonal_yields = []
            if 'Season' in results.columns and 'Harvest Date (YYYY/MM/DD)' in results.columns:
                # Get unique seasons and their yields
                for season in results['Season'].unique():
                    if pd.notna(season):
                        season_data = results[results['Season'] == season]
                        if not season_data.empty and yield_column in season_data.columns:
                            season_yield = season_data[yield_column].iloc[-1]  # Last value in season
                            harvest_date = season_data['Harvest Date (YYYY/MM/DD)'].iloc[-1] if 'Harvest Date (YYYY/MM/DD)' in season_data.columns else "Unknown"
                            seasonal_yields.append({
                                'season': int(season),
                                'harvest_date': str(harvest_date),
                                'yield_tonne_per_ha': round(season_yield, 2)
                            })
            
            yield_metrics = {
                "total_yield_tonne_per_ha": round(total_yield, 2),
                "average_yield_tonne_per_ha": round(avg_yield, 2),
                "maximum_yield_tonne_per_ha": round(max_yield, 2),
                "minimum_yield_tonne_per_ha": round(min_yield, 2),
                "final_yield_tonne_per_ha": round(final_yield, 2),
                "seasonal_yields": seasonal_yields
            }
            
            print(f"\n🎯 YIELD PREDICTION RESULTS:")
            print(f"   Final Yield: {final_yield:.2f} tonne/ha")
            print(f"   Average Yield: {avg_yield:.2f} tonne/ha")
            print(f"   Maximum Yield: {max_yield:.2f} tonne/ha")
            print(f"   Minimum Yield: {min_yield:.2f} tonne/ha")
            print(f"   Total Yield: {total_yield:.2f} tonne/ha")
            
            if seasonal_yields:
                print(f"\n📅 SEASONAL YIELD BREAKDOWN:")
                for season_data in seasonal_yields:
                    print(f"   Season {season_data['season']}: {season_data['yield_tonne_per_ha']} tonne/ha (Harvest: {season_data['harvest_date']})")
            
        else:
            error_msg = "No yield data found in simulation results"
            if results.empty:
                error_msg = "Simulation results are empty"
            elif not yield_column:
                error_msg = f"No yield column found. Available columns: {list(results.columns)}"
            
            yield_metrics = {
                "error": error_msg,
                "total_yield_tonne_per_ha": 0,
                "average_yield_tonne_per_ha": 0,
                "maximum_yield_tonne_per_ha": 0,
                "minimum_yield_tonne_per_ha": 0,
                "final_yield_tonne_per_ha": 0,
                "seasonal_yields": []
            }
            print(f"❌ {error_msg}")
        
        # Prepare comprehensive results
        simulation_results = {
            "status": "success",
            "simulation_parameters": {
                "crop_type": crop_type,
                "planting_date": planting_date,
                "soil_type": soil_type,
                "simulation_years": sim_years,
                "simulation_period": f"{sim_start_time} to {sim_end_time}",
                "weather_data_source": "Tunis climate data",
                "implementation_type": "mock" if use_mock else "real_aquacrop"
            },
            "yield_predictions": yield_metrics,
            "simulation_steps": [
                "1. Loaded weather data from Tunis climate file",
                "2. Configured soil parameters",
                f"3. Set up {crop_type} crop with planting date {planting_date}",
                "4. Initialized water content to field capacity",
                f"5. Ran {sim_years}-year simulation from {sim_start_time} to {sim_end_time}",
                "6. Extracted yield predictions from simulation results"
            ],
            "model_info": {
                "model_name": "AquaCrop",
                "description": "FAO crop water productivity model for simulating crop growth and water management",
                "transparency": "Full simulation process is logged and visible to user",
                "implementation": "Real AquaCrop" if not use_mock else "Mock implementation for demonstration"
            },
            "raw_results_summary": {
                "total_records": len(results) if not results.empty else 0,
                "columns": list(results.columns) if not results.empty else [],
                "date_range": {
                    "start": str(results['Date'].min()) if not results.empty and 'Date' in results.columns else None,
                    "end": str(results['Date'].max()) if not results.empty and 'Date' in results.columns else None
                }
            }
        }
        
        return simulation_results
        
    except ImportError as e:
        error_msg = f"AquaCrop library not installed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "suggestion": "Install aquacrop with: pip install aquacrop"
        }
    
    except Exception as e:
        error_msg = f"Yield prediction failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg
        }


def main():
    """Main function for command-line usage."""
    # Parse command line arguments
    crop_type = sys.argv[1] if len(sys.argv) > 1 else "Wheat"
    planting_date = sys.argv[2] if len(sys.argv) > 2 else "10/01"
    soil_type = sys.argv[3] if len(sys.argv) > 3 else "SandyLoam"
    sim_years = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    
    print("=" * 60)
    print("🌾 AQUACROP WHEAT YIELD PREDICTION TOOL - ENHANCED")
    print("=" * 60)
    
    # Run prediction
    results = predict_yield(crop_type, planting_date, soil_type, sim_years)
    
    # Print JSON output for programmatic use
    print("\n" + "=" * 60)
    print("📊 DETAILED RESULTS (JSON):")
    print("=" * 60)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    return results


if __name__ == "__main__":
    main()
