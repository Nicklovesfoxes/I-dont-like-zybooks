"""
Radio Question Solver - Solves multiple choice and True/False questions
"""
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .base_solver import BaseSolver
from config import SELECTORS
from utils.timing import bell_curve_delay


class RadioQuestionSolver(BaseSolver):
    """Solver for radio button questions (multiple choice, True/False)"""
    
    def solve_questions(self, questions):
        """
        Solve pre-scanned radio questions
        
        Args:
            questions: List of question dictionaries (already filtered by scanner)
        """
        self.logger.info(f"Starting Radio Question Solver")
        self.logger.info(f"Processing {len(questions)} radio questions")
        
        if not questions:
            self.logger.info("No radio questions to solve")
            return
        
        # Solve each question
        solved_count = 0
        for idx, question_data in enumerate(questions, 1):
            if self.should_stop():
                return
            
            self.logger.info(f"Question {idx}/{len(questions)}")
            
            if self.solve_question(question_data['element']):
                solved_count += 1
            
            # Random delay between questions
            if idx < len(questions):  # Don't delay after last question
                self.random_delay()
        
        self.logger.success(f"Completed! Solved {solved_count}/{len(questions)} questions")
    
    def solve_question(self, question):
        """
        Solve a single radio question by trying each option
        
        Args:
            question: WebElement of the question
            
        Returns:
            bool: True if question was solved successfully
        """
        try:
            radios = question.find_elements(
                By.CSS_SELECTOR,
                SELECTORS['RADIO']['radio_input']
            )
        except NoSuchElementException:
            self.logger.error("No radio buttons found in question")
            return False
        
        self.logger.info(f"Found {len(radios)} radio buttons")
        
        # Try each radio button until correct answer found
        for radio_idx, radio in enumerate(radios, 1):
            if self.should_stop():
                return False
            
            try:
                # Get button text for logging
                parent = radio.find_element(By.XPATH, '..')
                text = parent.text.strip()
                if not text:
                    text = f"Option {radio_idx}"
                
                self.logger.info(f"Trying: {text}")
                
                # Capture existing feedback messages BEFORE clicking
                old_feedback_messages = self.get_current_feedback_messages()
                
                # Click the radio button (with scroll and fallback)
                try:
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
                    # Small delay after scroll (bell curve: avg 200ms, range 100-400ms)
                    bell_curve_delay(mean_ms=200, std_dev_ms=50, min_ms=100, max_ms=400)
                    radio.click()
                except Exception as click_error:
                    # Fallback: Use JavaScript click if normal click is intercepted
                    self.logger.info("Using JavaScript click as fallback")
                    self.driver.execute_script("arguments[0].click();", radio)
                
                # Wait for feedback to appear (bell curve: avg 500ms, range 300-800ms)
                bell_curve_delay(mean_ms=500, std_dev_ms=100, min_ms=300, max_ms=800)
                
                # Check for NEW feedback (not the old ones)
                if self.check_feedback(old_feedback_messages):
                    return True
                
            except Exception as e:
                self.logger.error(f"Error clicking radio button: {e}")
                continue
        
        self.logger.error("No correct answer found for question")
        return False
    
    def get_current_feedback_messages(self):
        """
        Get all current feedback messages on the page
        Returns set of message texts to compare against later
        """
        messages = set()
        try:
            # Get all feedback elements
            all_feedback = self.driver.find_elements(By.CSS_SELECTOR, 'div.zb-explanation')
            for feedback in all_feedback:
                try:
                    # Get the message text (the explanation div, not the "Correct" h3)
                    msg_div = feedback.find_element(By.CSS_SELECTOR, 'div')
                    text = msg_div.text.strip()
                    if text:
                        messages.add(text)
                except:
                    pass
        except:
            pass
        return messages
    
    def check_feedback(self, old_messages):
        """
        Check for NEW feedback after clicking a radio button
        Only looks for feedback with message text different from old_messages
        
        Args:
            old_messages: Set of feedback message texts that existed before clicking
            
        Returns:
            bool: True if new correct feedback found, False if new incorrect or no new feedback
        """
        wait_time = 0
        max_wait = 2.0  # 2 seconds max
        check_interval = 0.1  # Check every 100ms
        
        while wait_time < max_wait:
            if self.should_stop():
                return False
            
            # Check for correct feedback with NEW message
            try:
                correct_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    SELECTORS['RADIO']['feedback_correct']
                )
                for elem in correct_elements:
                    try:
                        msg_div = elem.find_element(By.CSS_SELECTOR, 'div')
                        text = msg_div.text.strip()
                        # Only consider it if it's a NEW message
                        if text and text not in old_messages:
                            self.logger.success("Correct answer found!")
                            return True
                    except:
                        pass
            except:
                pass
            
            # Check for incorrect feedback with NEW message
            try:
                incorrect_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    SELECTORS['RADIO']['feedback_incorrect']
                )
                for elem in incorrect_elements:
                    try:
                        msg_div = elem.find_element(By.CSS_SELECTOR, 'div')
                        text = msg_div.text.strip()
                        # Only consider it if it's a NEW message
                        if text and text not in old_messages:
                            self.logger.info("✗ Incorrect, trying next option")
                            return False
                    except:
                        pass
            except:
                pass
            
            # Using bell curve delay
            bell_curve_delay(mean_ms=100, std_dev_ms=25, min_ms=50, max_ms=150)
            wait_time += 0.1
            wait_time += check_interval
        
        # No NEW feedback after 2 seconds
        self.logger.info("No feedback received, trying next option")
        return False
