# Agent Demo - AI-Powered Mac Assistant

A Python-based AI agent that uses the DeepSeek/OpenAI API to perform file/system tasks on macOS and provide transparent agricultural modeling (wheat yield prediction via AquaCrop).

## 🎯 Features

- **File Management**: Create, rename, and manage text/Python files
- **System Information**: Get directory structure and host information
- **Command Execution**: Execute system commands (with safety checks)
- **Interactive Mode**: Both CLI and REPL interfaces
- **Multi-language Support**: Works with Python, Go, C, and other languages
- **Agricultural Modeling**: Wheat yield prediction via AquaCrop with step-by-step transparency (mock fallback included)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- DeepSeek or OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agent_demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API key(s)
# e.g.
# DEEPSEEK_API_KEY=sk-...
# or OPENAI_API_KEY=sk-...
```

### Usage

#### Command Line Mode
```bash
python src/main.py "Create a Python script that prints hello world"
```

#### Interactive REPL Mode
```bash
python src/main.py --repl
```

#### Wheat Yield Prediction (AquaCrop)
- Run the comprehensive example:
```bash
python examples/wheat_yield_example.py
```
- Or ask directly via the agent:
```bash
python src/main.py "Find the best wheat planting date between 09/25 and 10/03"
```

#### Conversation History Utilities
- Clear history:
```bash
python src/main.py --clear-history
```
- Show history summary:
```bash
python src/main.py --history-summary
```

## 🛠️ Available Tools

- `create_text_file`: Create or overwrite text files
- `create_python_file`: Create Python files with proper extensions
- `get_directory_structure`: Get JSON tree of directory structure
- `rename_file`: Rename or move files/directories
- `execute_windows_command`: Execute system commands (Mac-optimized)
- `get_host_info`: Get detailed system information
- `predict_wheat_yield`: Predict wheat yield using the AquaCrop model (transparent steps)

## 📁 Project Structure

```
agent_demo/
├── src/
│   ├── main.py          # Main agent application
│   ├── tools.py         # Tool functions
│   └── test/            # Example files (misc)
├── examples/            # Usage examples incl. wheat yield demo
├── data/                # Data directory
├── model/               # Model directory
├── fig/                 # Figures directory
├── WHEAT_YIELD_README.md# Wheat yield tool documentation
├── .env                 # Environment configuration
└── README.md           # This file
```

## 🔧 Configuration

The agent can be configured through environment variables:

- `DEEPSEEK_API_KEY`: Your DeepSeek API key (required)
- `OPENAI_API_KEY`: Alternative provider API key (optional)
- `DEEPSEEK_BASE_URL`: API base URL (default: https://api.deepseek.com)

## 🧪 Testing

Run unit tests:
```bash
python -m pytest tests/ -v
```

Run examples:
```bash
python examples/basic_usage.py
python examples/wheat_yield_example.py
```

Use Makefile shortcuts:
```bash
make install
make test
make run PROMPT="Find the best wheat planting date between 09/25 and 10/03"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your DeepSeek API key is correctly set in `.env`
2. **Permission Errors**: Make sure the agent has write permissions in target directories
3. **Command Execution**: Some commands may require additional permissions
4. **AquaCrop Import**: If AquaCrop is not installed or fails to load, a mock implementation is used. To try the real model:
   - Install: `pip install aquacrop`
   - Note: Platform-specific constraints may still apply

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the tool documentation in `src/tools.py`

## 🌾 Recent Analysis Snapshot

Based on the latest conversation history in `conversation_history.json`, recent wheat planting date analyses showed:

- Best planting window: early October.
- For 09/25–10/03: recommended dates are October 1 or October 3.
- For 09/25–10/05: recommended dates are October 1 or October 5.
- Average yield advantage: early October dates ≈ 8.78 t/ha vs late September ≈ 8.73 t/ha (example simulations).
- Note on Shandong in December: December planting is outside the typical winter wheat window (optimal is mid‑September to late October) and is not recommended; consider late‑October/November what‑if analyses instead.

For full transparency and detailed step logs, see `examples/wheat_yield_example.py` and `WHEAT_YIELD_README.md`.
