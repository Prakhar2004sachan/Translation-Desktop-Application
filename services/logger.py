import logging
from collections import deque
from datetime import datetime

class GUILogger(logging.Handler):
    def __init__(self, capacity: int = 1000):
        super().__init__()
        self.logs = deque(maxlen=capacity)
        
    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append({
            "timestamp": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage()
        })

def setup_logger() -> GUILogger:
    logger = logging.getLogger("AppLogger")
    logger.setLevel(logging.DEBUG)
    
    gui_handler = GUILogger()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    gui_handler.setFormatter(formatter)
    
    logger.addHandler(gui_handler)
    return gui_handler
