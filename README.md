# Agent Demo - AI-Powered Mac Assistant

A Python-based AI agent that uses DeepSeek API to perform various file operations and system tasks on Mac platforms.

## 🎯 Features

- **File Management**: Create, rename, and manage text/Python files
- **System Information**: Get directory structure and host information
- **Command Execution**: Execute system commands (with safety checks)
- **Interactive Mode**: Both CLI and REPL interfaces
- **Multi-language Support**: Works with Python, Go, C, and other languages

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- DeepSeek API key

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
# Edit .env with your DeepSeek API key
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

## 🛠️ Available Tools

- `create_text_file`: Create or overwrite text files
- `create_python_file`: Create Python files with proper extensions
- `get_directory_structure`: Get JSON tree of directory structure
- `rename_file`: Rename or move files/directories
- `execute_windows_command`: Execute system commands (Mac-optimized)
- `get_host_info`: Get detailed system information

## 📁 Project Structure

```
agent_demo/
├── src/
│   ├── main.py          # Main agent application
│   ├── tools.py         # Tool functions
│   └── test/            # Example files
├── data/                # Data directory
├── model/               # Model directory
├── fig/                 # Figures directory
├── .env                 # Environment configuration
└── README.md           # This file
```

## 🔧 Configuration

The agent can be configured through environment variables:

- `DEEPSEEK_API_KEY`: Your DeepSeek API key (required)
- `DEEPSEEK_BASE_URL`: API base URL (default: https://api.deepseek.com)

## 🧪 Testing

Run the test examples:
```bash
python src/test/hello_world.py
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

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the tool documentation in `src/tools.py`