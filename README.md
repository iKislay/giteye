# 🔍 GitEye - GitHub Leaked API Key Scanner

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/iKislay/giteye?style=social)](https://github.com/iKislay/giteye)

> **GitEye** is a powerful and comprehensive GitHub API key scanner that helps security researchers, developers, and organizations discover leaked API keys across multiple AI services on GitHub.

## 🌟 Features

- **Multi-Service Support**: Scan for leaked API keys from:
  - 🤖 **Anthropic** (Claude API)
  - 🧠 **OpenAI** (GPT API)
  - 🚀 **XAI** (Grok API)
- **Smart Detection**: Advanced regex patterns to identify various API key formats
- **Real-time Validation**: Verify discovered keys using actual API endpoints
- **Parallel Processing**: Run multiple scanners simultaneously for efficiency
- **User-Friendly Interface**: Beautiful CLI with progress tracking
- **CSV Export**: Export results to a comprehensive CSV file with status codes
- **Headless Mode**: Optional headless Chrome for server environments
- **Resume Capability**: Continue scanning from where you left off

## 📋 Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- GitHub account (for authentication)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/iKislay/giteye.git
   cd giteye
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

### Quick Start

Run the main application:
```bash
python main.py
```

You'll see the GitEye logo and a menu to select which API keys to scan for:

```
1. Anthropic
2. OpenAI  
3. XAI API
4. All
```

### Command Line Options

Each scanner supports various options:

```bash
# Run in headless mode
python -m anthropic_api_scanner_main.src.main --headless

# Start from a specific iteration
python -m anthropic_api_scanner_main.src.main --from-iter 10

# Only check existing keys
python -m anthropic_api_scanner_main.src.main --check-existed-keys-only

# Check insufficient quota keys
python -m anthropic_api_scanner_main.src.main --check-insuffcient-quota

# Custom keywords and languages
python -m anthropic_api_scanner_main.src.main -k "api key" "secret" -l "python" "javascript"
```

## 🛡️ Security & Ethics

### Responsible Disclosure
- **For Educational Purposes**: This tool is designed for security research and educational purposes
- **Respect Rate Limits**: The tool includes built-in rate limiting to respect GitHub's API
- **No Malicious Use**: Do not use this tool for unauthorized access or malicious purposes
- **Report Responsibly**: If you find valid API keys, report them to the respective service providers

### Legal Compliance
- Ensure you comply with GitHub's Terms of Service
- Respect rate limits and usage policies
- Use only for authorized security research

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Reporting Bugs
1. Check existing issues first
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information

### 💡 Suggesting Features
1. Open an issue with the "enhancement" label
2. Describe the feature and its benefits
3. Provide use cases if possible

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests if applicable
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to your branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### 📝 Code Style
- Follow PEP 8 guidelines
- Add type hints where appropriate
- Include docstrings for functions and classes
- Use meaningful variable and function names

## ⭐ Star This Project

If GitEye has been helpful in your security research or development work, please consider giving it a star! ⭐

**Why star this project?**
- 🌟 **Support Development**: Stars help motivate continued development
- 🔍 **Discoverability**: More stars = more visibility = more contributors
- 🛡️ **Security Community**: Help build a stronger security research community
- 📈 **Feature Requests**: Higher visibility helps prioritize new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Kislay**
- GitHub: [@iKislay](https://github.com/iKislay)
- LinkedIn: [Kislay](https://www.linkedin.com/in/kislayy/)

## 🙏 Acknowledgments

- Thanks to the open-source community for various libraries and tools
- GitHub for providing the platform for security research
- All contributors and users who help improve this tool

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/iKislay/giteye/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iKislay/giteye/discussions)
- **Email**: Feel free to reach out for collaboration opportunities

---

<div align="center">
  <p>Made with ❤️ for the security community</p>
  <p>If this tool helped you, please give it a ⭐</p>
</div> 