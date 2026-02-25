"""
Timing utilities for human-like delays using bell curve distributions
"""
import random
import time


def bell_curve_delay(mean_ms, std_dev_ms=None, min_ms=None, max_ms=None):
    """
    Wait for a random amount of time using a bell curve (Gaussian distribution)
    This creates more human-like timing - most delays near the mean, few outliers
    
    Args:
        mean_ms: Average delay in milliseconds (center of bell curve)
        std_dev_ms: Standard deviation in milliseconds (spread of curve)
                   If None, defaults to mean_ms / 4
        min_ms: Minimum delay in milliseconds (clips low outliers)
               If None, defaults to mean_ms / 2
        max_ms: Maximum delay in milliseconds (clips high outliers)
               If None, defaults to mean_ms * 2
    
    Example:
        bell_curve_delay(1000)  # Average 1s, most between 0.5-2s
        bell_curve_delay(500, 100)  # Average 0.5s, tighter spread
    """
    # Set defaults
    if std_dev_ms is None:
        std_dev_ms = mean_ms / 4  # 25% of mean as standard deviation
    
    if min_ms is None:
        min_ms = mean_ms / 2  # Half the mean as minimum
    
    if max_ms is None:
        max_ms = mean_ms * 2  # Double the mean as maximum
    
    # Generate delay from bell curve (normal distribution)
    delay_ms = random.gauss(mean_ms, std_dev_ms)
    
    # Clip to min/max bounds
    delay_ms = max(min_ms, min(max_ms, delay_ms))
    
    # Convert to seconds and sleep
    delay_seconds = delay_ms / 1000.0
    time.sleep(delay_seconds)
    
    return delay_ms  # Return actual delay used (for logging if needed)


def uniform_delay(min_ms, max_ms):
    """
    Wait for a random amount of time using uniform distribution (flat distribution)
    Each value between min and max has equal probability
    
    Args:
        min_ms: Minimum delay in milliseconds
        max_ms: Maximum delay in milliseconds
    """
    delay_seconds = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
    time.sleep(delay_seconds)
    return delay_seconds * 1000


# Preset delay configurations for common use cases
class DelayPresets:
    """Preset delay configurations for different timing needs"""
    
    @staticmethod
    def quick_click():
        """Very short delay between clicks within same question"""
        bell_curve_delay(mean_ms=200, std_dev_ms=50, min_ms=100, max_ms=400)
    
    @staticmethod
    def between_questions():
        """Normal delay between questions"""
        bell_curve_delay(mean_ms=1250, std_dev_ms=300, min_ms=500, max_ms=2000)
    
    @staticmethod
    def page_load():
        """Longer delay for page loads or animations"""
        bell_curve_delay(mean_ms=2000, std_dev_ms=500, min_ms=1000, max_ms=4000)
    
    @staticmethod
    def feedback_check():
        """Short delay when checking for feedback"""
        bell_curve_delay(mean_ms=100, std_dev_ms=25, min_ms=50, max_ms=200)
