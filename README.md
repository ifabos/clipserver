# Clipserver

A simple web-based clipboard sharing server that allows you to access your clipboard content through a web interface.

## Features

- Web interface for viewing and modifying clipboard content
- Secure authentication with randomly generated token
- Easy to use API for clipboard operations
- Cross-platform compatibility

## Installation

```bash
pip install wclip
```

## Usage

### Command Line

Simply run the clipserver command:

```bash
clipserver
```

Or run as a module:

```bash
python -m clipserver
```

### Options

```
clipserver [--port PORT] [--no-browser]
  --port PORT      Specify the port to run the server on (default: 8080)
  --no-browser     Don't automatically open the browser
  --help           Show this help message
```

### As a Library

```python
from clipserver import start_server

# Start with default settings
start_server()

# Or with custom settings
start_server(port=9090, open_browser=False)
```

## Security

- The server generates a random 8-character password on startup
- Authentication uses username "clipboard" and the generated password
- Only authenticated users can access clipboard data
- Sessions are maintained using secure cookies

## Requirements

- Python 3.6+
- pyperclip

## License

MIT License - see the [LICENSE](LICENSE) file for details.
