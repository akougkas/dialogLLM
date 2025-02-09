import logging
import json
import sys
from logging.handlers import RotatingFileHandler
import os
from typing import Optional, Dict, Any

LOG_DIR = os.getenv('LOG_DIR', 'log')
LOG_FILE = os.path.join(LOG_DIR, "dialogllm.log")

class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.default_time_format),
            "thread": record.threadName,
            "process": record.process,
        }
        
        # Add extra fields directly from record.__dict__
        for key, value in record.__dict__.items():
            if key not in {
                'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                'funcName', 'levelname', 'levelno', 'lineno', 'module',
                'msecs', 'msg', 'name', 'pathname', 'process',
                'processName', 'relativeCreated', 'stack_info', 'thread',
                'threadName', 'message'
            }:
                log_record[key] = value
            
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)
            
        return json.dumps(log_record)

class Logger:
    """Singleton logger class for DialogLLM."""
    _instance: Optional['Logger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            instance = super().__new__(cls)
            # Initialize instance attributes
            instance.log_dir = os.getenv('LOG_DIR', LOG_DIR)
            instance.log_file = os.path.join(instance.log_dir, "dialogllm.log")
            # Create log directory immediately
            if not os.path.exists(instance.log_dir):
                os.makedirs(instance.log_dir)
            cls._instance = instance
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._configure()
            self._initialized = True
            
    def _configure(self):
        """Configure logging with console and file handlers."""
        # Create log directory if it doesn't exist
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create log directory {self.log_dir}: {e}")

        # Configure logger
        self.logger = logging.getLogger('dialogllm')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers if any
        for handler in self.logger.handlers[:]: 
            handler.close()  # Ensure files are closed
            self.logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)

        # File handler with rotation
        try:
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=512*1024,  # 512KB
                backupCount=5,
                delay=True  # Don't open file until first log
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(JsonFormatter())
            self.logger.addHandler(file_handler)
        except Exception as e:
            raise RuntimeError(f"Failed to configure file handler for {self.log_file}: {e}")
    
    def log(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a message with the specified level and extra fields."""
        if extra:
            self.logger.log(level, msg, extra=extra)
        else:
            self.logger.log(level, msg)
    
    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.DEBUG, msg, extra)
    
    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.INFO, msg, extra)
    
    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.WARNING, msg, extra)
    
    def error(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.ERROR, msg, extra)
    
    def exception(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.logger.exception(msg, extra=extra or {})

# Global logger instance
logger = Logger()
