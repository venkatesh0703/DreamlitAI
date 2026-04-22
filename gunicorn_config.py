import os
import sys

# Add src directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

bind = "0.0.0.0:" + os.getenv("PORT", "5000")
workers = 2
worker_class = "sync"
timeout = 180
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
