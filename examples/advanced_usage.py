#!/usr/bin/env python3
"""Advanced usage examples for the agent demo."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import create_agent


def example_project_setup():
    """Example of setting up a new project."""
    print("=== Project Setup Example ===")
    
    agent = create_agent()
    
    # Create a new project structure
    commands = [
        "Create a new directory called 'my_project'",
        "Create a Python file 'my_project/main.py' with a simple hello world function",
        "Create a requirements.txt file in 'my_project' with common dependencies",
        "Create a README.md file in 'my_project' with project description",
        "List the contents of 'my_project' directory"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        result = agent.run_sync(cmd)
        print(f"Result: {result.output}")


def example_mac_specific_operations():
    """Example of Mac-specific operations."""
    print("\n=== Mac-Specific Operations Example ===")
    
    agent = create_agent()
    
    # Get Mac-specific information
    commands = [
        "Get detailed Mac system information",
        "List installed applications",
        "Check if Homebrew is installed and list packages",
        "Get Mac permission status",
        "Create a desktop shortcut for a script"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        result = agent.run_sync(cmd)
        print(f"Result: {result.output}")


def example_automation_script():
    """Example of creating an automation script."""
    print("\n=== Automation Script Example ===")
    
    agent = create_agent()
    
    # Create an automation script
    script_content = '''
import os
import subprocess
from pathlib import Path

def cleanup_temp_files():
    """Clean up temporary files."""
    temp_dir = Path("/tmp")
    count = 0
    
    for file in temp_dir.glob("*.tmp"):
        try:
            file.unlink()
            count += 1
        except Exception as e:
            print(f"Error deleting {file}: {e}")
    
    print(f"Cleaned up {count} temporary files")

if __name__ == "__main__":
    cleanup_temp_files()
'''
    
    result = agent.run_sync(f"Create a Python file 'cleanup.py' with this content: {script_content}")
    print("Automation script creation:", result.output)


def example_data_processing():
    """Example of data processing tasks."""
    print("\n=== Data Processing Example ===")
    
    agent = create_agent()
    
    # Create a data processing script
    commands = [
        "Create a Python script that reads a CSV file and calculates basic statistics",
        "Create a sample CSV file with some data",
        "Create a script that processes JSON data and extracts specific fields"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        result = agent.run_sync(cmd)
        print(f"Result: {result.output}")


def example_web_scraping():
    """Example of web scraping setup."""
    print("\n=== Web Scraping Example ===")
    
    agent = create_agent()
    
    # Create a web scraping script
    commands = [
        "Create a Python script that uses requests and BeautifulSoup to scrape a website",
        "Create a requirements.txt file with web scraping dependencies",
        "Create a configuration file for web scraping settings"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        result = agent.run_sync(cmd)
        print(f"Result: {result.output}")


if __name__ == "__main__":
    print("Agent Demo - Advanced Usage Examples")
    print("=" * 50)
    
    try:
        example_project_setup()
        example_mac_specific_operations()
        example_automation_script()
        example_data_processing()
        example_web_scraping()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        sys.exit(1)