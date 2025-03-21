"""
Webclipboard - A web-based clipboard sharing server

This module provides a simple web server that allows you to access
your clipboard content through a web interface.
"""

__version__ = '0.1.0'

from .server import start_server

__all__ = ['start_server']
