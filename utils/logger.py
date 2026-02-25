"""
Logging utilities for Zybooks Solver
"""
from datetime import datetime


class Logger:
    """Simple logger that can output to console and/or GUI"""
    
    def __init__(self, gui_callback=None):
        """
        Args:
            gui_callback: Optional function to call with log messages for GUI display
        """
        self.gui_callback = gui_callback
    
    def log(self, message):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        formatted_msg = f"[{timestamp}] {message}"
        
        # Print to console
        print(formatted_msg)
        
        # Send to GUI if callback provided
        if self.gui_callback:
            self.gui_callback(formatted_msg)
    
    def success(self, message):
        """Log a success message"""
        self.log(f"✓ {message}")
    
    def error(self, message):
        """Log an error message"""
        self.log(f"✗ {message}")
    
    def info(self, message):
        """Log an info message"""
        self.log(f"ℹ {message}")
