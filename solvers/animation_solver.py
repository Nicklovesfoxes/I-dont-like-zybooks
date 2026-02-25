"""
Animation Solver - Plays through animation activities
"""
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .base_solver import BaseSolver
from config import SELECTORS, MAX_RETRIES
from utils.timing import bell_curve_delay


class AnimationSolver(BaseSolver):
    """Solver for animation questions"""
    
    def solve_questions(self, questions):
        """
        Solve pre-scanned animation questions
        
        Args:
            questions: List of question dictionaries (already filtered by scanner)
        """
        self.logger.info(f"Starting Animation Solver")
        self.logger.info(f"Processing {len(questions)} animation questions")
        
        if not questions:
            self.logger.info("No animation questions to solve")
            return
        
        # Solve each animation
        solved_count = 0
        for idx, question_data in enumerate(questions, 1):
            if self.should_stop():
                return
            
            self.logger.info(f"Animation {idx}/{len(questions)}")
            
            if self.solve_animation(question_data['element']):
                solved_count += 1
            
            # Random delay between animations
            if idx < len(questions):  # Don't delay after last animation
                self.random_delay()
        
        self.logger.success(f"Completed! Solved {solved_count}/{len(questions)} animations")
    
    def solve_animation(self, animation):
        """
        Solve a single animation by playing it through
        
        Strategy:
        1. Click Start button
        2. Enable 2x speed checkbox
        3. Click Play button repeatedly until completed
        4. Check chevron for completion after each play
        
        Args:
            animation: WebElement of the animation container
            
        Returns:
            bool: True if animation was completed successfully
        """
        try:
            # Step 1: Find and click Start button
            if not self.click_start_button(animation):
                return False
            
            # Step 2: Enable 2x speed if available
            self.enable_2x_speed(animation)
            
            # Step 3: Play animation until completion
            if not self.play_until_complete(animation):
                return False
            
            self.logger.success("Animation completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error solving animation: {e}")
            return False
    
    def click_start_button(self, animation):
        """
        Find and click the Start button
        
        Args:
            animation: WebElement of the animation container
            
        Returns:
            bool: True if successful
        """
        try:
            start_btn = animation.find_element(
                By.CSS_SELECTOR,
                SELECTORS['ANIMATIONS']['start_button']
            )
            
            self.logger.info("Clicking Start button...")
            self.safe_click(start_btn, "Start button")
            
            # Wait for animation to initialize (bell curve: avg 400ms, range 250-650ms)
            bell_curve_delay(mean_ms=400, std_dev_ms=100, min_ms=250, max_ms=650)
            
            return True
            
        except NoSuchElementException:
            # Maybe start button doesn't exist or was already clicked
            self.logger.info("Start button not found (may already be started)")
            return True
        except Exception as e:
            self.logger.error(f"Error clicking start button: {e}")
            return False
    
    def enable_2x_speed(self, animation):
        """
        Enable 2x speed checkbox if available
        
        Args:
            animation: WebElement of the animation container
        """
        try:
            speed_checkbox = animation.find_element(
                By.CSS_SELECTOR,
                SELECTORS['ANIMATIONS']['speed_checkbox']
            )
            
            # Check if already checked
            if not speed_checkbox.is_selected():
                self.logger.info("Enabling 2x speed...")
                self.safe_click(speed_checkbox, "2x speed checkbox")
                
                # Small delay after enabling speed (bell curve: avg 150ms, range 80-250ms)
                bell_curve_delay(mean_ms=150, std_dev_ms=40, min_ms=80, max_ms=250)
            else:
                self.logger.info("2x speed already enabled")
                
        except NoSuchElementException:
            self.logger.info("2x speed checkbox not found (may not be available)")
        except Exception as e:
            self.logger.error(f"Error enabling 2x speed: {e}")
    
    def play_until_complete(self, animation):
        """
        Repeatedly wait then click Play button until completion
        
        Cycle: Wait 2 seconds → Click Play (if possible) → Check completion → Repeat
        
        Args:
            animation: WebElement of the animation container
            
        Returns:
            bool: True if animation completed within max attempts
        """
        max_attempts = MAX_RETRIES  # From config.py (20 attempts)
        attempt = 0
        
        while attempt < max_attempts:
            if self.should_stop():
                return False
            
            attempt += 1
            self.logger.info(f"Play cycle {attempt}/{max_attempts}...")
            
            # Wait 2 seconds before clicking play (bell curve: avg 2000ms, range 1800-2200ms)
            self.logger.info("Waiting 2 seconds...")
            bell_curve_delay(mean_ms=2000, std_dev_ms=100, min_ms=1800, max_ms=2200)
            
            # Try to click the Play button (no retries - just try once)
            # If it fails, we'll try again in the next cycle
            self.click_play_button(animation)
            
            # Small delay after clicking to let animation process
            bell_curve_delay(mean_ms=200, std_dev_ms=50, min_ms=100, max_ms=300)
            
            # Check if completed (strict check)
            if self.is_complete(animation):
                self.logger.success(f"Animation completed after {attempt} play cycles")
                return True
        
        self.logger.error(f"Animation did not complete after {max_attempts} attempts")
        return False
    
    def click_play_button(self, animation):
        """
        Try to find and click the Play button once
        
        No retries - if it fails, the main loop will try again in 2 seconds
        
        Args:
            animation: WebElement of the animation container
            
        Returns:
            bool: True if successfully clicked, False if failed
        """
        try:
            play_btn = animation.find_element(
                By.CSS_SELECTOR,
                SELECTORS['ANIMATIONS']['play_button']
            )
            
            # Found the button, try to click it
            self.safe_click(play_btn, "Play button")
            return True
            
        except NoSuchElementException:
            self.logger.info("Play button not found, will retry in next cycle")
            return False
                    
        except Exception as e:
            self.logger.info(f"Could not click play button: {e}, will retry in next cycle")
            return False
    
    def is_complete(self, animation):
        """
        Check if animation is completed by examining chevron
        
        STRICT completion check - must have BOTH:
        - chevron has "filled" class AND
        - aria-label is "Activity completed"
        
        The chevron is in a parent container, not inside the animation element,
        so we need to search upward in the DOM tree.
        
        Args:
            animation: WebElement of the animation container
            
        Returns:
            bool: True if completed (strict check)
        """
        try:
            # Try to find chevron in parent elements (up to 5 levels up)
            current = animation
            for _ in range(5):
                try:
                    # Try to find chevron at this level
                    chevron = current.find_element(
                        By.CSS_SELECTOR,
                        SELECTORS['ANIMATIONS']['chevron']
                    )
                    
                    # Get both classes and aria-label
                    classes = chevron.get_attribute('class') or ''
                    aria_label = chevron.get_attribute('aria-label') or ''
                    
                    # STRICT check: Must have "filled" class AND correct aria-label
                    has_filled = 'filled' in classes
                    is_completed = 'Activity completed' in aria_label
                    
                    if has_filled and is_completed:
                        return True
                    
                except NoSuchElementException:
                    pass
                
                # Move up to parent
                try:
                    current = current.find_element(By.XPATH, '..')
                except:
                    break
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking completion: {e}")
            return False
    
    def safe_click(self, element, element_name="element"):
        """
        Click element with scroll and JavaScript fallback
        (same pattern as radio and short answer solvers)
        
        Args:
            element: WebElement to click
            element_name: Name for logging
        """
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            # Small delay after scroll
            bell_curve_delay(mean_ms=150, std_dev_ms=40, min_ms=80, max_ms=250)
            element.click()
        except Exception as click_error:
            # Fallback: Use JavaScript click if normal click is intercepted
            self.logger.info(f"Using JavaScript click for {element_name}")
            self.driver.execute_script("arguments[0].click();", element)
