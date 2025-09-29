#!/usr/bin/env python3
"""
Wheat Yield Prediction Example

This example demonstrates how to use the AquaCrop wheat yield prediction tool
both as a standalone module and through the LLM agent.

Usage:
    python wheat_yield_example.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import create_agent


def example_standalone_usage():
    """Example of using the standalone AquaCrop model."""
    print("=" * 60)
    print("🌾 STANDALONE AQUACROP USAGE EXAMPLE")
    print("=" * 60)
    
    # Import the standalone module
    sys.path.insert(0, str(Path(__file__).parent.parent / "model"))
    from aquacrop_model import predict_yield
    
    # Example 1: Default parameters
    print("\n📊 Example 1: Default wheat yield prediction")
    print("-" * 40)
    results1 = predict_yield()
    print(f"Status: {results1['status']}")
    if results1['status'] == 'success':
        yield_data = results1['yield_predictions']
        print(f"Final Yield: {yield_data['final_yield_tonne_per_ha']} tonne/ha")
        print(f"Average Yield: {yield_data['average_yield_tonne_per_ha']} tonne/ha")
    
    # Example 2: Custom parameters
    print("\n📊 Example 2: Custom parameters")
    print("-" * 40)
    results2 = predict_yield(
        crop_type="Wheat",
        planting_date="11/15",
        soil_type="ClayLoam",
        sim_years=4
    )
    print(f"Status: {results2['status']}")
    if results2['status'] == 'success':
        yield_data = results2['yield_predictions']
        print(f"Final Yield: {yield_data['final_yield_tonne_per_ha']} tonne/ha")
        print(f"Average Yield: {yield_data['average_yield_tonne_per_ha']} tonne/ha")


def example_agent_usage():
    """Example of using the LLM agent for wheat yield prediction."""
    print("\n" + "=" * 60)
    print("🤖 LLM AGENT WHEAT YIELD PREDICTION EXAMPLE")
    print("=" * 60)
    
    agent = create_agent()
    
    # Example 1: Simple yield prediction request
    print("\n📊 Example 1: Simple yield prediction")
    print("-" * 40)
    result1 = agent.run_sync("Predict wheat yield for planting date 10/01")
    print("Agent Response:")
    print(result1.output)
    
    # Example 2: Detailed yield prediction with custom parameters
    print("\n📊 Example 2: Detailed yield prediction with custom parameters")
    print("-" * 40)
    result2 = agent.run_sync(
        "Predict wheat yield with planting date 11/15, soil type ClayLoam, and 4 years simulation. "
        "Show me the step-by-step process and explain what AquaCrop does."
    )
    print("Agent Response:")
    print(result2.output)
    
    # Example 3: Compare different scenarios
    print("\n📊 Example 3: Compare different scenarios")
    print("-" * 40)
    result3 = agent.run_sync(
        "Compare wheat yield predictions for different planting dates: 10/01, 11/01, and 12/01. "
        "Use the same soil type and explain the differences."
    )
    print("Agent Response:")
    print(result3.output)


def example_transparency_demo():
    """Demonstrate the transparency of the wheat yield prediction process."""
    print("\n" + "=" * 60)
    print("🔍 TRANSPARENCY DEMONSTRATION")
    print("=" * 60)
    
    agent = create_agent()
    
    print("\nThis example shows how the LLM agent makes the wheat yield prediction process transparent:")
    print("1. The agent explains what AquaCrop is and how it works")
    print("2. The agent shows all simulation steps")
    print("3. The agent provides detailed results and explanations")
    print("4. Users can see exactly how the yield prediction is calculated")
    
    result = agent.run_sync(
        "Explain how you predict wheat yield. What is AquaCrop and how does it work? "
        "Show me a complete example with all the steps visible."
    )
    print("\nAgent Response:")
    print(result.output)


def example_error_handling():
    """Demonstrate error handling in wheat yield prediction."""
    print("\n" + "=" * 60)
    print("⚠️  ERROR HANDLING DEMONSTRATION")
    print("=" * 60)
    
    agent = create_agent()
    
    print("\nThis example shows how the system handles errors gracefully:")
    
    # Test with invalid parameters
    result = agent.run_sync(
        "Predict wheat yield with invalid planting date '13/45' and explain what happens"
    )
    print("\nAgent Response:")
    print(result.output)


def main():
    """Main function to run all examples."""
    print("🌾 WHEAT YIELD PREDICTION EXAMPLES")
    print("=" * 60)
    print("This demo shows how to use the AquaCrop wheat yield prediction tool")
    print("both as a standalone module and through the LLM agent.")
    print("The process is fully transparent - users can see every step!")
    
    try:
        # Run standalone examples
        example_standalone_usage()
        
        # Run agent examples
        example_agent_usage()
        
        # Demonstrate transparency
        example_transparency_demo()
        
        # Demonstrate error handling
        example_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey Features Demonstrated:")
        print("• Standalone AquaCrop module usage")
        print("• LLM agent integration")
        print("• Transparent simulation process")
        print("• Detailed yield predictions")
        print("• Error handling")
        print("• Multiple parameter scenarios")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install aquacrop")
        sys.exit(1)


if __name__ == "__main__":
    main()
