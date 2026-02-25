"""
Zybooks Solver - Main Entry Point
Automated solver for Zybooks educational platform questions
"""
import threading
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from utils.browser import setup_browser, navigate_to_zybooks
from utils.logger import Logger
from utils.timing import bell_curve_delay
from gui.control_panel import ControlPanel
from solvers.question_scanner import QuestionScanner
from solvers.radio_solver import RadioQuestionSolver
from solvers.animation_solver import AnimationSolver
from solvers.short_answer_solver import ShortAnswerSolver


class SolverManager:
    """Manages question scanning and solver execution with 3-phase workflow"""
    
    def __init__(self, driver, logger):
        """
        Args:
            driver: Selenium WebDriver instance
            logger: Logger instance
        """
        self.driver = driver
        self.logger = logger
        self.stop_event = threading.Event()
        
        # Initialize scanner
        self.scanner = QuestionScanner(driver, logger)
        
        # Initialize all solvers
        self.solvers = {
            'radio': RadioQuestionSolver(driver, logger, self.stop_event),
            'animation': AnimationSolver(driver, logger, self.stop_event),
            'short_answer': ShortAnswerSolver(driver, logger, self.stop_event),
        }
    
    def run(self, action, force_mode):
        """
        Run selected solver with unified 3-phase workflow
        
        Args:
            action: Action to perform (from dropdown)
            force_mode: Whether to re-solve completed questions
        """
        # Clear stop event
        self.stop_event.clear()
        
        # Handle continuous mode differently
        if action == "Solve All (Continuous)":
            self.run_continuous(force_mode)
            return
        
        self.logger.info(f"Starting: {action} (Force Mode: {force_mode})")
        self.logger.info("")
        
        # PHASE 1: SCAN - Detect all questions
        self.logger.info("=" * 50)
        self.logger.info("PHASE 1: SCANNING PAGE")
        self.logger.info("=" * 50)
        
        all_questions = self.scanner.scan_all_questions()
        
        if not all_questions:
            self.logger.error("No questions found on page!")
            return
        
        # If Scan Only, stop here
        if action == "Scan Only":
            self.logger.info("="*50)
            self.logger.info("Scan complete! (Scan Only mode - no solving)")
            self.logger.info("="*50)
            return
        
        if self.stop_event.is_set():
            return
        
        # PHASE 2: FILTER - Filter by type and completion
        self.logger.info("=" * 50)
        self.logger.info("PHASE 2: FILTERING QUESTIONS")
        self.logger.info("=" * 50)
        
        filtered = self.filter_questions(all_questions, action, force_mode)
        
        if not filtered:
            self.logger.info("No questions to process after filtering")
            self.logger.info("=" * 50)
            return
        
        self.logger.info(f"Filtered to {len(filtered)} questions for processing")
        self.logger.info("=" * 50)
        self.logger.info("")
        
        if self.stop_event.is_set():
            return
        
        # PHASE 3: SOLVE - Execute appropriate solver(s)
        self.logger.info("=" * 50)
        self.logger.info("PHASE 3: SOLVING QUESTIONS")
        self.logger.info("=" * 50)
        
        self.solve_filtered_questions(filtered, action)
        
        self.logger.info("")
        self.logger.info("=" * 50)
        self.logger.info("Solver execution completed!")
        self.logger.info("=" * 50)
    
    def run_continuous(self, force_mode):
        """
        Continuously solve all questions on each page, then navigate to next section
        
        Args:
            force_mode: Whether to re-solve completed questions
        """
        self.logger.info(f"Starting: Solve All (Continuous) (Force Mode: {force_mode})")
        self.logger.info("This will solve all questions on each page, then move to the next section")
        self.logger.info("")
        
        page_count = 0
        
        while not self.stop_event.is_set():
            page_count += 1
            
            self.logger.info("=" * 60)
            self.logger.info(f"PAGE {page_count}")
            self.logger.info("=" * 60)
            self.logger.info("")
            
            # PHASE 1: SCAN
            self.logger.info("=" * 50)
            self.logger.info("PHASE 1: SCANNING PAGE")
            self.logger.info("=" * 50)
            
            all_questions = self.scanner.scan_all_questions()
            
            if not all_questions:
                self.logger.info("No questions found on this page")
            else:
                if self.stop_event.is_set():
                    break
                
                # PHASE 2: FILTER
                self.logger.info("=" * 50)
                self.logger.info("PHASE 2: FILTERING QUESTIONS")
                self.logger.info("=" * 50)
                
                filtered = self.filter_questions(all_questions, "Solve All (Continuous)", force_mode)
                
                if filtered:
                    self.logger.info(f"Filtered to {len(filtered)} questions for processing")
                    self.logger.info("=" * 50)
                    self.logger.info("")
                    
                    if self.stop_event.is_set():
                        break
                    
                    # PHASE 3: SOLVE
                    self.logger.info("=" * 50)
                    self.logger.info("PHASE 3: SOLVING QUESTIONS")
                    self.logger.info("=" * 50)
                    
                    self.solve_filtered_questions(filtered, "Solve All (Continuous)")
                else:
                    self.logger.info("No questions to process after filtering")
                    self.logger.info("=" * 50)
            
            if self.stop_event.is_set():
                break
            
            # Try to navigate to next section
            self.logger.info("")
            self.logger.info("=" * 50)
            self.logger.info("NAVIGATING TO NEXT SECTION")
            self.logger.info("=" * 50)
            
            if not self.click_next_section():
                self.logger.info("No more sections found - continuous solving complete!")
                break
            
            # Wait 4 seconds for page to load
            self.logger.info("Waiting 4 seconds for page to load...")
            bell_curve_delay(mean_ms=4000, std_dev_ms=200, min_ms=3800, max_ms=4200)
            self.logger.info("")
        
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("CONTINUOUS SOLVING COMPLETED!")
        self.logger.info(f"Processed {page_count} pages")
        self.logger.info("=" * 60)
    
    def click_next_section(self):
        """
        Click the next section navigation link at the bottom of the page
        
        Returns:
            bool: True if next link was found and clicked, False otherwise
        """
        try:
            # Look for the next section link with arrow_downward icon
            icon = self.driver.find_element(
                By.CSS_SELECTOR,
                'a.nav-link i[aria-label="arrow_downward"]'
            )
            
            # Get the parent anchor element (icon is direct child of anchor)
            link_element = icon.find_element(By.XPATH, '..')
            
            # Get the section name for logging
            section_text = link_element.text.strip()
            self.logger.info(f"Found next section link: '{section_text}'")
            
            # Get the href for additional logging
            href = link_element.get_attribute('href')
            self.logger.info(f"Target URL: {href}")
            
            # Scroll into view and click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_element)
            bell_curve_delay(mean_ms=300, std_dev_ms=50, min_ms=200, max_ms=400)
            
            self.logger.info("Clicking next section link...")
            try:
                link_element.click()
                self.logger.success(f"Clicked! Navigating to: {section_text}")
            except Exception as click_error:
                # JavaScript click fallback
                self.logger.info(f"Normal click failed ({click_error}), using JavaScript click")
                self.driver.execute_script("arguments[0].click();", link_element)
                self.logger.success(f"JavaScript click successful! Navigating to: {section_text}")
            
            return True
            
        except NoSuchElementException:
            self.logger.info("No next section link found (might be last section)")
            return False
        except Exception as e:
            self.logger.error(f"Error clicking next section: {e}")
            return False
    
    def filter_questions(self, questions, action, force_mode):
        """
        Filter questions based on action and force mode
        
        Args:
            questions: List of all scanned questions
            action: Selected action from dropdown
            force_mode: Whether to include completed questions
            
        Returns:
            list: Filtered questions ready for solving
        """
        # Map actions to question types
        type_map = {
            "Solve Radio Questions": "radio",
            "Solve Animations": "animation",
            "Solve Short Answer": "short_answer",
        }
        
        filtered = []
        
        for q in questions:
            # Filter by type (unless "Solve All On Page")
            if action not in ["Solve All On Page", "Solve All (Continuous)"]:
                target_type = type_map.get(action)
                if q['type'] != target_type:
                    continue
            
            # Filter by completion status (unless force mode)
            if not force_mode and q['completed']:
                continue
            
            filtered.append(q)
        
        return filtered
    
    def solve_filtered_questions(self, questions, action):
        """
        Route filtered questions to appropriate solver(s)
        
        Args:
            questions: Filtered list of questions to solve
            action: Selected action (determines routing)
        """
        if action in ["Solve All On Page", "Solve All (Continuous)"]:
            # Group by type and solve each group
            grouped = {}
            for q in questions:
                qtype = q['type']
                if qtype not in grouped:
                    grouped[qtype] = []
                grouped[qtype].append(q)
            
            # Solve each type
            type_solver_map = {
                'radio': ('Radio Questions', self.solvers['radio']),
                'animation': ('Animations', self.solvers['animation']),
                'short_answer': ('Short Answer', self.solvers['short_answer']),
            }
            
            for qtype, type_questions in grouped.items():
                if self.stop_event.is_set():
                    break
                
                name, solver = type_solver_map.get(qtype, (qtype, None))
                if solver:
                    self.logger.info(f"\n--- {name} ---")
                    solver.solve_questions(type_questions)
        else:
            # Single type - route to appropriate solver
            type_map = {
                "Solve Radio Questions": self.solvers['radio'],
                "Solve Animations": self.solvers['animation'],
                "Solve Short Answer": self.solvers['short_answer'],
            }
            
            solver = type_map.get(action)
            if solver:
                solver.solve_questions(questions)
            else:
                self.logger.error(f"Unknown action: {action}")
    
    def stop(self):
        """Signal all solvers to stop"""
        self.stop_event.set()
        self.logger.info("Stop signal sent to solvers")


def main():
    """Main entry point"""
    print("="*60)
    print("ZYBOOKS SOLVER")
    print("="*60)
    print("\nStarting browser...")
    
    # Setup browser
    driver = setup_browser()
    
    print("Browser launched successfully!")
    print("\nNavigating to Zybooks...")
    
    # Navigate to Zybooks
    navigate_to_zybooks(driver)
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("1. Manually log in to Zybooks in the browser window")
    print("2. Navigate to the chapter/section you want to solve")
    print("3. Use the control panel to start solving questions")
    print("="*60)
    
    # Setup logger and GUI
    gui = None
    
    def gui_log_callback(message):
        """Callback to send logs to GUI"""
        if gui:
            gui.root.after(0, lambda: gui.log(message))
    
    logger = Logger(gui_callback=gui_log_callback)
    
    # Setup solver manager
    solver_manager = SolverManager(driver, logger)
    
    # Create and start GUI
    gui = ControlPanel(solver_manager)
    
    print("\nControl panel opened!")
    print("Close the control panel window to exit.\n")
    
    try:
        gui.start()
    finally:
        print("\nCleaning up...")
        driver.quit()
        print("Browser closed. Goodbye!")


if __name__ == "__main__":
    main()
