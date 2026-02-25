"""
Browser setup and management utilities
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


def setup_browser():
    """
    Initialize and return a Chrome WebDriver instance
    
    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    options = Options()
    # Don't run headless - user needs to see what's happening
    # options.add_argument('--headless')
    
    # Optional: Start maximized
    options.add_argument('--start-maximized')
    
    # Disable automation flags
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Disable some security features that might interfere
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Setup driver - try multiple approaches
    driver = None
    errors = []
    
    # Approach 1: Try webdriver-manager
    if WEBDRIVER_MANAGER_AVAILABLE:
        try:
            print("Attempting to setup Chrome with webdriver-manager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("Success with webdriver-manager!")
            return driver
        except Exception as e:
            errors.append(f"webdriver-manager failed: {e}")
            print(f"webdriver-manager failed, trying alternative...")
    
    # Approach 2: Try default Chrome (Selenium 4.6+ has built-in manager)
    if driver is None:
        try:
            print("Attempting to setup Chrome with Selenium's built-in manager...")
            driver = webdriver.Chrome(options=options)
            print("Success with built-in manager!")
            return driver
        except Exception as e:
            errors.append(f"Built-in manager failed: {e}")
    
    # If both failed, raise detailed error
    error_msg = "\n".join([
        "Failed to initialize Chrome WebDriver.",
        "Errors encountered:",
        *[f"  - {err}" for err in errors],
        "",
        "Please ensure:",
        "  1. Chrome browser is installed",
        "  2. ChromeDriver matches your Chrome version",
        "  3. Try: pip install --upgrade selenium webdriver-manager"
    ])
    raise RuntimeError(error_msg)


def navigate_to_zybooks(driver):
    """
    Navigate to Zybooks website
    
    Args:
        driver: WebDriver instance
    """
    driver.get('https://learn.zybooks.com')
