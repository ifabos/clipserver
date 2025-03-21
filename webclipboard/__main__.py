"""
Command-line interface for the webclipboard module.
"""

import argparse
import sys
from .server import start_server

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Web Clipboard Server')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port to run the server on (default: 8080)')
    parser.add_argument('--no-browser', action='store_true',
                        help="Don't automatically open the browser")
    
    return parser.parse_args()

def main():
    """Main entry point for the command-line interface."""
    try:
        args = parse_args()
        start_server(port=args.port, open_browser=not args.no_browser)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
