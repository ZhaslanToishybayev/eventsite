"""
🚀 Production WSGI для UnitySphere AI
Gunicorn + Nginx конфигурация
"""

import os
import multiprocessing

# 🔧 Gunicorn Config
bind = "127.0.0.1:8001"  # Internal port
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# 📁 Paths
chdir = "/var/www/myapp/eventsite"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
capture_output = True

# 🔒 Security
preload_app = True
daemon = False
pidfile = "/var/run/gunicorn.pid"

# 🚀 Performance
worker_tmp_dir = "/dev/shm"
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 📊 Monitoring
statsd_host = "localhost:8125"
statsd_prefix = "unitysphere.ai"

# 🌐 Environment
raw_env = [
    "DJANGO_SETTINGS_MODULE=core.settings",
    "DEBUG=False",
]

# 🔄 Graceful shutdown
graceful_timeout = 30
keepalive = 2