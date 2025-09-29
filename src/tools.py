import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import psutil
from logger import get_logger, log_function_call, log_error


def _ok(message: str, **extra: Any) -> str:
    payload: Dict[str, Any] = {"status": "ok", "message": message}
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _err(message: str, **extra: Any) -> str:
    payload: Dict[str, Any] = {"status": "error", "message": message}
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def create_text_file(file_path: str, content: str) -> str:
    """Create or overwrite a text file with UTF-8 content.

    Args:
      file_path: Target file path, directories created as needed.
      content: Text content to write.

    Returns a JSON string indicating status and path.
    """
    logger = get_logger()
    log_function_call("create_text_file", {"file_path": file_path, "content_length": len(content)})
    
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        
        logger.info(f"Created text file: {path}")
        return _ok("text file written", path=str(path.resolve()))
    except Exception as e:
        log_error(e, f"create_text_file({file_path})")
        return _err("failed to write text file", error=str(e), path=file_path)


def create_python_file(file_path: str, code: str) -> str:
    """Create or overwrite a Python file with UTF-8 code.

    If the path has no `.py` suffix, it will be added.
    """
    try:
        path = Path(file_path)
        if path.suffix != ".py":
            path = path.with_suffix(".py")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")
        return _ok("python file written", path=str(path.resolve()))
    except Exception as e:
        return _err("failed to write python file", error=str(e), path=file_path)


def get_directory_structure(root: str = ".") -> str:
    """Return a JSON tree of the directory structure.

    Args:
      root: Root directory to inspect.
    """
    root_path = Path(root)
    if not root_path.exists():
        return _err("root does not exist", root=str(root_path))

    def walk(p: Path) -> Dict[str, Any]:
        if p.is_dir():
            children: List[Dict[str, Any]] = []
            for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                # Skip common noisy directories
                if child.name in {".git", "__pycache__", "node_modules"}:
                    continue
                children.append(walk(child))
            return {"type": "dir", "name": p.name, "path": str(p), "children": children}
        else:
            return {"type": "file", "name": p.name, "path": str(p)}

    try:
        tree = walk(root_path)
        return json.dumps(tree, ensure_ascii=False, indent=2)
    except Exception as e:
        return _err("failed to build structure", error=str(e), root=str(root_path))


def rename_file(old_path: str, new_path: str) -> str:
    """Rename or move a file or directory."""
    try:
        src = Path(old_path)
        dst = Path(new_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        return _ok("renamed", src=str(src), dst=str(dst))
    except Exception as e:
        return _err("failed to rename", error=str(e), src=old_path, dst=new_path)


def execute_command(command: str, timeout_sec: int = 60) -> str:
    """Execute a shell command and return output.
    
    Supports both Unix/macOS and Windows systems.
    """
    try:
        # Use appropriate shell based on platform
        shell_cmd = command
        if platform.system().lower() == "windows":
            shell_cmd = f"cmd /c {command}"
        
        completed = subprocess.run(
            shell_cmd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            encoding="utf-8",
            errors="replace",
        )
        return json.dumps(
            {
                "status": "ok" if completed.returncode == 0 else "error",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "platform": platform.system(),
            },
            ensure_ascii=False,
            indent=2,
        )
    except subprocess.TimeoutExpired:
        return _err("command timed out", command=command, timeout_sec=timeout_sec)
    except Exception as e:
        return _err("failed to execute command", error=str(e), command=command)


def execute_windows_command(command: str, timeout_sec: int = 60) -> str:
    """Execute a Windows CMD command and return output.

    On non-Windows systems, returns an error message.
    """
    if platform.system().lower() != "windows":
        return _err("not running on windows", command=command)

    try:
        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            encoding="utf-8",
            errors="replace",
        )
        return json.dumps(
            {
                "status": "ok" if completed.returncode == 0 else "error",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            ensure_ascii=False,
            indent=2,
        )
    except subprocess.TimeoutExpired:
        return _err("command timed out", command=command, timeout_sec=timeout_sec)
    except Exception as e:
        return _err("failed to execute command", error=str(e), command=command)


def get_host_info() -> str:
    """Get host information as a JSON string."""
    info: Dict[str, Any] = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
    }

    cpu_count = psutil.cpu_count(logical=True)
    info["cpu_count"] = cpu_count if cpu_count is not None else -1

    # Best-effort CPU model on macOS; ignore failures on other OSes
    try:
        cpu_model = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"]
        ).decode().strip()
        info["cpu_model"] = cpu_model
    except Exception:
        info["cpu_model"] = "Unknown"

    return json.dumps(info, ensure_ascii=False, indent=2)


def list_files(directory: str = ".", pattern: str = "*", recursive: bool = True) -> str:
    """List files in a directory with optional pattern matching."""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return _err("directory does not exist", directory=directory)
        
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))
        
        file_list = []
        for file_path in sorted(files):
            if file_path.is_file():
                stat = file_path.stat()
                file_list.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime,
                    "extension": file_path.suffix
                })
        
        return _ok("files listed", files=file_list, count=len(file_list))
    except Exception as e:
        return _err("failed to list files", error=str(e), directory=directory)


def read_file_content(file_path: str, max_size_mb: int = 10) -> str:
    """Read file content with size limit protection."""
    try:
        path = Path(file_path)
        if not path.exists():
            return _err("file does not exist", file_path=file_path)
        
        if not path.is_file():
            return _err("path is not a file", file_path=file_path)
        
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return _err(f"file too large ({size_mb:.1f}MB > {max_size_mb}MB)", file_path=file_path)
        
        content = path.read_text(encoding="utf-8", errors="replace")
        return _ok("file read", content=content, size_mb=round(size_mb, 2))
    except Exception as e:
        return _err("failed to read file", error=str(e), file_path=file_path)


def create_directory(dir_path: str) -> str:
    """Create a directory and all parent directories."""
    try:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return _ok("directory created", path=str(path.resolve()))
    except Exception as e:
        return _err("failed to create directory", error=str(e), dir_path=dir_path)


def delete_file(file_path: str) -> str:
    """Delete a file or empty directory."""
    try:
        path = Path(file_path)
        if not path.exists():
            return _err("file does not exist", file_path=file_path)
        
        if path.is_file():
            path.unlink()
            return _ok("file deleted", path=str(path))
        elif path.is_dir():
            if any(path.iterdir()):
                return _err("directory is not empty", file_path=file_path)
            path.rmdir()
            return _ok("directory deleted", path=str(path))
        else:
            return _err("unknown file type", file_path=file_path)
    except Exception as e:
        return _err("failed to delete file", error=str(e), file_path=file_path)


def get_system_resources() -> str:
    """Get current system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": round((disk.used / disk.total) * 100, 2)
            }
        }
        
        return _ok("system resources", resources=resources)
    except Exception as e:
        return _err("failed to get system resources", error=str(e))


def predict_wheat_yield(crop_type: str = "Wheat", planting_date: str = "10/01", 
                       soil_type: str = "SandyLoam", sim_years: int = 6) -> str:
    """Predict wheat yield using AquaCrop model based on user inputs.
    
    This tool simulates crop growth and water management to predict yield.
    The process is transparent and shows all simulation steps.
    
    Args:
        crop_type: Type of crop (default: "Wheat")
        planting_date: Planting date in MM/DD format (default: "10/01")
        soil_type: Soil type for simulation (default: "SandyLoam")
        sim_years: Number of years to simulate (default: 6)
    
    Returns:
        JSON string with simulation results and yield prediction
    """
    logger = get_logger()
    log_function_call("predict_wheat_yield", {
        "crop_type": crop_type, 
        "planting_date": planting_date, 
        "soil_type": soil_type,
        "sim_years": sim_years
    })
    
    try:
        # Fix for AquaCrop on macOS - ensure 'python' command is available
        import os
        import subprocess
        from pathlib import Path
        
        def setup_python_alias():
            """Set up python alias for AquaCrop compatibility."""
            try:
                subprocess.run(['python', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                python3_path = subprocess.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()
                if python3_path:
                    os.environ['PATH'] = f"{os.path.dirname(python3_path)}:{os.environ.get('PATH', '')}"
                    temp_dir = Path.home() / '.local' / 'bin'
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    python_link = temp_dir / 'python'
                    if not python_link.exists():
                        try:
                            python_link.symlink_to(python3_path)
                            os.environ['PATH'] = f"{temp_dir}:{os.environ.get('PATH', '')}"
                        except (OSError, PermissionError):
                            pass
        
        setup_python_alias()
        
        # Try to import real AquaCrop modules
        use_mock = True  # Default to mock due to AquaCrop compatibility issues
        try:
            from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
            from aquacrop.utils import prepare_weather, get_filepath
            # Test if AquaCrop actually works by trying to create a simple object
            test_soil = Soil(soil_type='SandyLoam')
            use_mock = False
            logger.info("Real AquaCrop loaded successfully")
        except (ImportError, FileNotFoundError, OSError) as e:
            logger.warning(f"Real AquaCrop not available ({e}), using mock implementation for demonstration")
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "model"))
            from mock_aquacrop import get_mock_aquacrop
            mock_modules = get_mock_aquacrop()
            AquaCropModel = mock_modules['AquaCropModel']
            Soil = mock_modules['Soil']
            Crop = mock_modules['Crop']
            InitialWaterContent = mock_modules['InitialWaterContent']
            prepare_weather = mock_modules['prepare_weather']
            get_filepath = mock_modules['get_filepath']
        
        import pandas as pd
        
        logger.info("Starting AquaCrop wheat yield simulation...")
        
        # Step 1: Prepare weather data
        logger.info("Step 1: Loading weather data from Tunis climate file")
        if use_mock:
            logger.info("Using mock weather data for demonstration")
            weather_df = prepare_weather('mock_tunis_climate.txt')
        else:
            weather_file_path = get_filepath('tunis_climate.txt')
            weather_df = prepare_weather(weather_file_path)
        
        # Step 2: Set up simulation parameters
        logger.info(f"Step 2: Setting up simulation parameters")
        logger.info(f"  - Crop: {crop_type}")
        logger.info(f"  - Planting date: {planting_date}")
        logger.info(f"  - Soil type: {soil_type}")
        logger.info(f"  - Simulation years: {sim_years}")
        
        # Calculate simulation dates
        start_year = 1979
        end_year = start_year + sim_years - 1
        sim_start_time = f"{start_year}/10/01"
        sim_end_time = f"{end_year}/05/30"
        
        logger.info(f"  - Simulation period: {sim_start_time} to {sim_end_time}")
        
        # Step 3: Initialize AquaCrop model
        logger.info("Step 3: Initializing AquaCrop model components")
        
        # Create soil object
        soil = Soil(soil_type=soil_type)
        logger.info(f"  - Soil created: {soil_type}")
        
        # Create crop object
        crop = Crop(crop_type, planting_date=planting_date)
        logger.info(f"  - Crop created: {crop_type} with planting date {planting_date}")
        
        # Set initial water content
        initial_water_content = InitialWaterContent(value=['FC'])
        logger.info("  - Initial water content set to Field Capacity (FC)")
        
        # Step 4: Create and configure model
        logger.info("Step 4: Creating AquaCrop model")
        model = AquaCropModel(
            sim_start_time=sim_start_time,
            sim_end_time=sim_end_time,
            weather_df=weather_df,
            soil=soil,
            crop=crop,
            initial_water_content=initial_water_content,
        )
        logger.info("  - Model created successfully")
        
        # Step 5: Run simulation
        logger.info("Step 5: Running crop simulation...")
        model.run_model(till_termination=True)
        logger.info("  - Simulation completed successfully")
        
        # Step 6: Extract results
        logger.info("Step 6: Extracting simulation results")
        results = model.get_simulation_results()
        
        # Debug: Log information about the results
        logger.info(f"Results shape: {results.shape}")
        logger.info(f"Results columns: {list(results.columns)}")
        if not results.empty:
            logger.info(f"First few rows: {results.head().to_string()}")
        else:
            logger.warning("Results DataFrame is empty!")
        
        # Calculate yield metrics from the actual results
        yield_metrics = {}
        
        # Check for different possible yield column names
        yield_column = None
        possible_yield_columns = ['Dry yield (tonne/ha)', 'Yield (tonne/ha)', 'Yield', 'yield', 'Biomass (tonne/ha)', 'Biomass']
        
        for col in possible_yield_columns:
            if col in results.columns:
                yield_column = col
                logger.info(f"Found yield column: {yield_column}")
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
        
        # Prepare detailed results
        simulation_details = {
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
                "2. Configured soil parameters (SandyLoam)",
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
        
        logger.info(f"Wheat yield prediction completed. Final yield: {yield_metrics.get('final_yield_tonne_per_ha', 0)} tonne/ha")
        
        return _ok("wheat yield prediction completed", **simulation_details)
        
    except ImportError as e:
        error_msg = f"AquaCrop library not installed: {str(e)}"
        logger.error(error_msg)
        return _err("aquacrop import failed", error=error_msg, 
                   suggestion="Install aquacrop with: pip install aquacrop")
    
    except Exception as e:
        error_msg = f"Wheat yield prediction failed: {str(e)}"
        logger.error(error_msg)
        return _err("prediction failed", error=error_msg)


if __name__ == "__main__":
    print(get_host_info())
