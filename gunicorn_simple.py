"""
Simple Gunicorn configuration for testing
"""

import multiprocessing

# Simple config
bind = "127.0.0.1:8001"
workers = 1
worker_class = "sync"
timeout = 30
keepalive = 2

# Basic logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Environment
raw_env = [
    "DJANGO_SETTINGS_MODULE=core.settings",
    "DEBUG=False",
]

preload_app = True
daemon = False