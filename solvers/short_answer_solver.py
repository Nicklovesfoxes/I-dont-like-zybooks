"""
Short Answer Solver - Reveals answers and submits them
"""
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .base_solver import BaseSolver
from config import SELECTORS
from utils.timing import bell_curve_delay


class ShortAnswerSolver(BaseSolver):
    """Solver for short answer questions"""
    
    def solve_questions(self, questions):
        """
        Solve pre-scanned short answer questions
        
        Args:
            questions: List of question dictionaries (already filtered by scanner)
        """
        self.logger.info(f"Starting Short Answer Solver")
        self.logger.info(f"Processing {len(questions)} short answer questions")
        
        if not questions:
            self.logger.info("No short answer questions to solve")
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
        Solve a single short answer question
        
        Strategy:
        1. Find show answer button, input field, check button
        2. Click "Show answer" button TWICE (Zybooks requires this)
        3. Extract answer from span.forfeit-answer
        4. Type answer into input field
        5. Click check button
        6. Verify completion
        
        Args:
            question: WebElement of the question
            
        Returns:
            bool: True if question was solved successfully
        """
        try:
            # Find the required elements
            show_answer_btn = self.find_show_answer_button(question)
            input_field = self.find_input_field(question)
            check_btn = self.find_check_button(question)
            
            if not all([show_answer_btn, input_field, check_btn]):
                self.logger.error("Missing required elements (show answer/input/check button)")
                return False
            
            # Step 1: Click "Show Answer" button TWICE (required by Zybooks)
            self.logger.info("Revealing answer...")
            if not self.reveal_answer(show_answer_btn):
                return False
            
            # Step 2: Extract the answer
            answer = self.extract_answer(question)
            if not answer:
                self.logger.error("Could not find answer after revealing")
                return False
            
            self.logger.info(f"Answer found: '{answer}'")
            
            # Step 3: Type answer into input field
            if not self.type_answer(input_field, answer):
                return False
            
            # Step 4: Click check button to submit
            if not self.submit_answer(check_btn):
                return False
            
            # Step 5: Verify completion
            if self.verify_completion(question):
                self.logger.success("Question completed successfully!")
                return True
            else:
                self.logger.error("Answer submitted but question not marked as complete")
                return False
            
        except Exception as e:
            self.logger.error(f"Error solving question: {e}")
            return False
    
    def find_show_answer_button(self, question):
        """Find the 'Show answer' button within question"""
        try:
            btn = question.find_element(
                By.CSS_SELECTOR,
                SELECTORS['SHORT_ANSWER']['show_answer']
            )
            return btn
        except NoSuchElementException:
            self.logger.error("Show answer button not found")
            return None
    
    def find_input_field(self, question):
        """Find the input/textarea field for answer entry"""
        # Try textarea first (preferred according to spec)
        try:
            field = question.find_element(
                By.CSS_SELECTOR,
                SELECTORS['SHORT_ANSWER']['textarea']
            )
            return field
        except NoSuchElementException:
            pass
        
        # Fallback to generic textarea
        try:
            field = question.find_element(By.CSS_SELECTOR, 'textarea')
            return field
        except NoSuchElementException:
            pass
        
        # Fallback to text input (based on user's HTML example)
        try:
            field = question.find_element(By.CSS_SELECTOR, 'input.zb-input')
            return field
        except NoSuchElementException:
            pass
        
        # Final fallback to any text input
        try:
            field = question.find_element(By.CSS_SELECTOR, 'input[type="text"]')
            return field
        except NoSuchElementException:
            self.logger.error("Input field not found")
            return None
    
    def find_check_button(self, question):
        """Find the 'Check' button within question"""
        try:
            btn = question.find_element(
                By.CSS_SELECTOR,
                SELECTORS['SHORT_ANSWER']['check']
            )
            return btn
        except NoSuchElementException:
            self.logger.error("Check button not found")
            return None
    
    def reveal_answer(self, show_answer_btn):
        """
        Click show answer button TWICE as required by Zybooks
        
        Args:
            show_answer_btn: WebElement of show answer button
            
        Returns:
            bool: True if clicks were successful
        """
        try:
            # First click - primes the button
            self.logger.info("First click on 'Show answer'...")
            self.safe_click(show_answer_btn, "Show answer button (1st click)")
            
            # Wait between clicks (bell curve: avg 150ms, range 100-250ms)
            bell_curve_delay(mean_ms=150, std_dev_ms=30, min_ms=100, max_ms=250)
            
            # Second click - reveals the answer
            self.logger.info("Second click on 'Show answer'...")
            self.safe_click(show_answer_btn, "Show answer button (2nd click)")
            
            # Wait for answer to appear (bell curve: avg 300ms, range 200-500ms)
            bell_curve_delay(mean_ms=300, std_dev_ms=75, min_ms=200, max_ms=500)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking show answer button: {e}")
            return False
    
    def extract_answer(self, question):
        """
        Extract the answer from span.forfeit-answer after revealing
        
        Args:
            question: WebElement of the question
            
        Returns:
            str: The answer text, or None if not found
        """
        try:
            # Look for answer in forfeit-answer span
            answer_elem = question.find_element(
                By.CSS_SELECTOR,
                SELECTORS['SHORT_ANSWER']['answers']
            )
            answer = answer_elem.text.strip()
            
            if answer:
                return answer
            
            # If text is empty, try getting innerHTML
            answer = answer_elem.get_attribute('innerHTML').strip()
            return answer if answer else None
            
        except NoSuchElementException:
            # Try alternative selectors
            try:
                # Sometimes the answer is in the explanation div
                answer_elem = question.find_element(By.CSS_SELECTOR, 'span.forfeit-answer')
                answer = answer_elem.text.strip()
                if answer:
                    return answer
            except:
                pass
            
            self.logger.error("Answer element not found")
            return None
    
    def type_answer(self, input_field, answer):
        """
        Type the answer into the input field
        
        Args:
            input_field: WebElement of input/textarea
            answer: String to type
            
        Returns:
            bool: True if successful
        """
        try:
            # Scroll field into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_field)
            bell_curve_delay(mean_ms=200, std_dev_ms=50, min_ms=100, max_ms=350)
            
            # Clear any existing value
            input_field.clear()
            
            # Small delay after clearing (bell curve: avg 100ms, range 50-200ms)
            bell_curve_delay(mean_ms=100, std_dev_ms=30, min_ms=50, max_ms=200)
            
            # Type the answer
            self.logger.info(f"Typing answer into field...")
            input_field.send_keys(answer)
            
            # Trigger input event to ensure Zybooks detects the change
            self.driver.execute_script("""
                var event = new Event('input', { bubbles: true });
                arguments[0].dispatchEvent(event);
            """, input_field)
            
            # Wait after typing (bell curve: avg 200ms, range 100-350ms)
            bell_curve_delay(mean_ms=200, std_dev_ms=60, min_ms=100, max_ms=350)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error typing answer: {e}")
            return False
    
    def submit_answer(self, check_btn):
        """
        Click the check button to submit answer
        
        Args:
            check_btn: WebElement of check button
            
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Submitting answer...")
            self.safe_click(check_btn, "Check button")
            
            # Wait for submission to process (bell curve: avg 600ms, range 400-1000ms)
            bell_curve_delay(mean_ms=600, std_dev_ms=150, min_ms=400, max_ms=1000)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking check button: {e}")
            return False
    
    def safe_click(self, element, element_name="element"):
        """
        Click element with scroll and JavaScript fallback
        (same pattern as radio solver)
        
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
    
    def verify_completion(self, question):
        """
        Verify the question was completed by checking for filled chevron
        (same pattern as radio solver)
        
        Args:
            question: WebElement of the question
            
        Returns:
            bool: True if question is marked as complete
        """
        max_wait = 2.0  # 2 seconds max
        wait_time = 0
        check_interval = 0.1
        
        while wait_time < max_wait:
            if self.should_stop():
                return False
            
            try:
                # Check if chevron is filled (completion indicator)
                # Try to find chevron in parent elements
                parent = question
                for _ in range(3):  # Check up to 3 levels up
                    try:
                        chevron = parent.find_element(By.CSS_SELECTOR, 'div.zb-chevron')
                        classes = chevron.get_attribute('class') or ''
                        if 'filled' in classes:
                            return True
                    except:
                        pass
                    
                    try:
                        parent = parent.find_element(By.XPATH, '..')
                    except:
                        break
                
            except:
                pass
            
            bell_curve_delay(mean_ms=100, std_dev_ms=25, min_ms=50, max_ms=150)
            wait_time += check_interval
        
        return False
