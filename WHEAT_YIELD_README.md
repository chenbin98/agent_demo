# Wheat Yield Prediction Tool

This tool provides transparent wheat yield prediction using the AquaCrop model, designed for integration with LLM agents. Users can input crop parameters and receive detailed yield predictions with full visibility into the simulation process.

## Features

- 🌾 **Transparent Process**: Every step of the simulation is logged and visible to users
- 🤖 **LLM Integration**: Seamlessly integrated with the agent system
- 📊 **Detailed Results**: Comprehensive yield metrics and simulation data
- 🔧 **Flexible Parameters**: Customizable crop type, planting date, soil type, and simulation duration
- 📈 **Standalone Usage**: Can be used independently or through the LLM agent

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have your API keys configured in a `.env` file:
```
DEEPSEEK_API_KEY=your_api_key_here
# or
OPENAI_API_KEY=your_api_key_here
```

## Usage

### 1. Standalone Usage

Run the AquaCrop model directly:

```bash
# Default parameters
python model/aquacrop_model.py

# Custom parameters
python model/aquacrop_model.py Wheat 11/15 ClayLoam 4
```

### 2. LLM Agent Usage

Use the agent to predict wheat yield:

```python
from src.main import create_agent

agent = create_agent()

# Simple prediction
result = agent.run_sync("Predict wheat yield for planting date 10/01")

# Detailed prediction with explanation
result = agent.run_sync(
    "Predict wheat yield with planting date 11/15, soil type ClayLoam, "
    "and 4 years simulation. Show me the step-by-step process."
)
```

### 3. Programmatic Usage

Use the tool function directly:

```python
from src.tools import predict_wheat_yield
import json

# Predict yield with custom parameters
result = predict_wheat_yield(
    crop_type="Wheat",
    planting_date="10/01",
    soil_type="SandyLoam",
    sim_years=6
)

# Parse the JSON result
data = json.loads(result)
print(f"Final yield: {data['yield_predictions']['final_yield_tonne_per_ha']} tonne/ha")
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `crop_type` | str | "Wheat" | Type of crop to simulate |
| `planting_date` | str | "10/01" | Planting date in MM/DD format |
| `soil_type` | str | "SandyLoam" | Soil type for simulation |
| `sim_years` | int | 6 | Number of years to simulate |

## Output

The tool returns a comprehensive JSON response containing:

### Simulation Parameters
- Crop type and planting date
- Soil type and simulation duration
- Weather data source information

### Yield Predictions
- Final yield (tonne/ha)
- Average yield (tonne/ha)
- Maximum yield (tonne/ha)
- Minimum yield (tonne/ha)
- Total yield (tonne/ha)

### Simulation Steps
- Detailed list of all simulation steps
- Transparency information about the process

### Model Information
- AquaCrop model details
- Description of the simulation process

## Example Output

```json
{
  "status": "ok",
  "message": "wheat yield prediction completed",
  "simulation_parameters": {
    "crop_type": "Wheat",
    "planting_date": "10/01",
    "soil_type": "SandyLoam",
    "simulation_years": 6,
    "simulation_period": "1979/10/01 to 1984/05/30",
    "weather_data_source": "Tunis climate data"
  },
  "yield_predictions": {
    "final_yield_tonne_per_ha": 3.45,
    "average_yield_tonne_per_ha": 3.12,
    "maximum_yield_tonne_per_ha": 4.20,
    "minimum_yield_tonne_per_ha": 2.10,
    "total_yield_tonne_per_ha": 18.72
  },
  "simulation_steps": [
    "1. Loaded weather data from Tunis climate file",
    "2. Configured soil parameters (SandyLoam)",
    "3. Set up Wheat crop with planting date 10/01",
    "4. Initialized water content to field capacity",
    "5. Ran 6-year simulation from 1979/10/01 to 1984/05/30",
    "6. Extracted yield predictions from simulation results"
  ],
  "model_info": {
    "model_name": "AquaCrop",
    "description": "FAO crop water productivity model for simulating crop growth and water management",
    "transparency": "Full simulation process is logged and visible to user"
  }
}
```

## Transparency Features

The tool is designed to be completely transparent to users:

1. **Step-by-Step Logging**: Every simulation step is logged and visible
2. **Parameter Visibility**: All input parameters are clearly displayed
3. **Process Explanation**: The agent explains what AquaCrop is and how it works
4. **Error Handling**: Clear error messages with suggestions for resolution
5. **Detailed Results**: Comprehensive output with all relevant metrics

## Testing

Run the test suite to verify everything is working:

```bash
python test_wheat_yield.py
```

Run the comprehensive examples:

```bash
python examples/wheat_yield_example.py
```

## Files Structure

```
model/
├── aquacrop_model.py          # Standalone AquaCrop tool
src/
├── tools.py                   # Contains predict_wheat_yield function
├── main.py                    # Agent with wheat yield tool integrated
examples/
├── wheat_yield_example.py     # Comprehensive usage examples
test_wheat_yield.py            # Test suite
WHEAT_YIELD_README.md          # This documentation
```

## Error Handling

The tool handles various error conditions gracefully:

- **Missing Dependencies**: Clear message if AquaCrop is not installed
- **Invalid Parameters**: Validation and helpful error messages
- **Simulation Failures**: Detailed error reporting with context
- **API Issues**: Proper error handling for agent integration

## Contributing

When extending this tool:

1. Maintain transparency - log all important steps
2. Provide clear error messages
3. Include comprehensive documentation
4. Add tests for new features
5. Follow the existing JSON response format

## License

This tool is part of the agent_demo project and follows the same licensing terms.
