#!/usr/bin/env python3
"""Basic usage examples for the agent demo."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import create_agent


def example_file_operations():
    """Example of file operations."""
    print("=== File Operations Example ===")
    
    agent = create_agent()
    
    # Create a Python file
    result = agent.run_sync("Create a Python script called 'hello.py' that prints 'Hello, World!'")
    print("Create Python file:", result.output)
    
    # List files
    result = agent.run_sync("List all Python files in the current directory")
    print("List Python files:", result.output)


def example_system_info():
    """Example of system information gathering."""
    print("\n=== System Information Example ===")
    
    agent = create_agent()
    
    # Get system info
    result = agent.run_sync("Get detailed system information")
    print("System info:", result.output)
    
    # Get Mac-specific info
    result = agent.run_sync("Get Mac system information including macOS version")
    print("Mac info:", result.output)


def example_command_execution():
    """Example of command execution."""
    print("\n=== Command Execution Example ===")
    
    agent = create_agent()
    
    # Execute a simple command
    result = agent.run_sync("Execute the command 'ls -la' to list files")
    print("Command execution:", result.output)


def example_interactive_session():
    """Example of interactive session."""
    print("\n=== Interactive Session Example ===")
    print("Starting interactive session. Type 'quit' to exit.")
    
    agent = create_agent()
    
    while True:
        try:
            user_input = input("\n>>> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
                
            result = agent.run_sync(user_input)
            print(result.output)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Agent Demo - Basic Usage Examples")
    print("=" * 50)
    
    try:
        example_file_operations()
        example_system_info()
        example_command_execution()
        
        # Uncomment to run interactive session
        # example_interactive_session()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        sys.exit(1)