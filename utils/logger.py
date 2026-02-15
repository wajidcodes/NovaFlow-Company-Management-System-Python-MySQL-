"""
Logging Configuration

Provides a centralized logging setup for the application.
Logs are written to both file and console for easy debugging.
"""
import logging
import os
from datetime import datetime


def setup_logger(name, log_level=logging.INFO):
    """
    Setup and return a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (default: INFO)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if not exists
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file with date
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers on repeated calls
    if not logger.handlers:
        # File handler - logs everything
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # Console handler - only warnings and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Format: timestamp | level | module | message
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


# Convenience function for quick logging
def get_logger(name=None):
    """Get a logger with default configuration."""
    return setup_logger(name or 'app')


if __name__ == "__main__":
    # Test logging when run directly
    logger = setup_logger("test")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    print("Check logs/ directory for log file")
