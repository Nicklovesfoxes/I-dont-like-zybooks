"""
Base solver class with common functionality
"""
import random
import time
from config import MIN_BETWEEN_QUESTIONS, MAX_BETWEEN_QUESTIONS
from utils.timing import bell_curve_delay


class BaseSolver:
    """Base class for all question solvers"""
    
    def __init__(self, driver, logger, stop_event=None):
        """
        Args:
            driver: Selenium WebDriver instance
            logger: Logger instance for output
            stop_event: Optional threading.Event to check for stop requests
        """
        self.driver = driver
        self.logger = logger
        self.stop_event = stop_event
    
    def should_stop(self):
        """Check if solver should stop execution"""
        if self.stop_event and self.stop_event.is_set():
            self.logger.info("Stop requested by user")
            return True
        return False
    
    def random_delay(self, min_ms=None, max_ms=None, use_bell_curve=True):
        """
        Wait for a random amount of time
        
        Args:
            min_ms: Minimum delay in milliseconds (default: MIN_BETWEEN_QUESTIONS)
            max_ms: Maximum delay in milliseconds (default: MAX_BETWEEN_QUESTIONS)
            use_bell_curve: If True, uses bell curve distribution (more human-like)
                          If False, uses uniform distribution (flat probability)
        """
        if min_ms is None:
            min_ms = MIN_BETWEEN_QUESTIONS
        if max_ms is None:
            max_ms = MAX_BETWEEN_QUESTIONS
        
        if use_bell_curve:
            # Bell curve: most delays near center, few at extremes
            mean_ms = (min_ms + max_ms) / 2
            std_dev_ms = (max_ms - min_ms) / 6  # ~95% within min-max range
            bell_curve_delay(mean_ms, std_dev_ms, min_ms, max_ms)
        else:
            # Uniform: equal probability across range
            delay_seconds = random.uniform(min_ms / 1000, max_ms / 1000)
            time.sleep(delay_seconds)
    
    def solve_all(self, force_mode=False):
        """
        Main entry point for solving questions
        Should be implemented by child classes
        
        Args:
            force_mode: If True, re-solve already completed questions
        """
        raise NotImplementedError("Subclasses must implement solve_all()")
