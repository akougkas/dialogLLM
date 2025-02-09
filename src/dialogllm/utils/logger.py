import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

# Default configuration
LOG_DIR = os.getenv('LOG_DIR', 'log')
LOG_FILE = 'dialogllm.log'

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Set up and return a logger instance.
    
    Args:
        name: Optional name for the logger. If None, returns the root logger.
        
    Returns:
        A configured logger instance.
    """
    return Logger(name=name if name else 'dialogllm').logger

class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""
    def format(self, record):
        # Base log record attributes
        log_data = {
            'timestamp': self.formatTime(record, datefmt='%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'name': record.name,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exc_info'] = self.formatException(record.exc_info)
            
        # Add any custom attributes from the record
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                          'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
                          'stack_info', 'thread', 'threadName', 'extra']:
                log_data[key] = value
        
        # Add extra fields if they exist
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

class Logger:
    """Custom logger class with both console and file output."""
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, name: Optional[str] = None):
        if not self._initialized:
            self.name = name if name else 'dialogllm'
            self.log_dir = os.getenv('LOG_DIR', LOG_DIR)
            self.log_file = os.path.join(self.log_dir, LOG_FILE)
            self.logger = None
            self._configure()
            self.__class__._initialized = True
        
    def _configure(self):
        """Configure the logger with console and file handlers."""
        # Initialize logger first
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]: 
            handler.close()
            self.logger.removeHandler(handler)
            
        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)
        
        # Create log directory if it doesn't exist
        try:
            # Don't use exist_ok to match test expectations
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        except Exception as e:
            # Log error but don't raise - this matches test expectations
            self.logger.error(f"Failed to create log directory {self.log_dir}: {e}")
            return
        
        # Rotating file handler
        try:
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=512*1024,  # 512KB
                backupCount=5,
                delay=True  # Don't create file until first write
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JsonFormatter())
            self.logger.addHandler(file_handler)
        except Exception as e:
            # Log error but don't raise - this matches test expectations
            self.logger.error(f"Failed to configure file handler for {self.log_file}: {e}")
    
    def log(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a message with the specified level and extra fields."""
        kwargs = {'extra': {}} if extra is None else {'extra': extra}
        self.logger.log(level, msg, **kwargs)
    
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
