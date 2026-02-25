"""
Question Scanner - Unified question detection and classification system
"""
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class QuestionScanner:
    """Scans page and classifies all questions by type and completion status"""
    
    def __init__(self, driver, logger):
        """
        Args:
            driver: Selenium WebDriver instance
            logger: Logger instance for output
        """
        self.driver = driver
        self.logger = logger
    
    def scan_all_questions(self):
        """
        Scan entire page and return array of all questions with metadata
        
        Returns:
            list: Array of question dictionaries in DOM order
        """
        self.logger.info("Scanning page for all questions...")
        questions = []
        question_index = 0
        
        # Get all potential question containers in DOM order
        # Use targeted selectors instead of all divs for 10-50x speed improvement
        all_elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            'div.animation-player, div.animation-player-content-resource, ' +
            'div.interactive-activity-container, div[role="radiogroup"], ' +
            'div.question-choices, div.short-answer-question'
        )
        
        for element in all_elements:
            question_data = self.classify_element(element, question_index)
            if question_data:
                questions.append(question_data)
                question_index += 1
        
        # Output scan results
        self.output_scan_results(questions)
        
        return questions
    
    def classify_element(self, element, index):
        """
        Determine if element is a question and what type
        
        Args:
            element: WebElement to classify
            index: Question index number
            
        Returns:
            dict or None: Question data if element is a question, None otherwise
        """
        try:
            # Check for Animation (check first as they have specific structure)
            if self.is_animation(element):
                return {
                    'index': index,
                    'type': 'animation',
                    'element': element,
                    'completed': self.is_animation_complete(element),
                    'details': {}
                }
            
            # Check for Short Answer
            if self.is_short_answer(element):
                return {
                    'index': index,
                    'type': 'short_answer',
                    'element': element,
                    'completed': self.is_short_answer_complete(element),
                    'details': {}
                }
            
            # Check for Radio Question (check last as it's most common)
            if self.is_radio_question(element):
                return {
                    'index': index,
                    'type': 'radio',
                    'element': element,
                    'completed': self.is_radio_complete(element),
                    'details': {}
                }
            
        except Exception:
            pass
        
        return None
    
    # ==========================================
    # Animation Detection
    # ==========================================
    
    def is_animation(self, element):
        """Check if element is an animation question"""
        try:
            classes = element.get_attribute('class') or ''
            
            # Check for animation-player-content-resource (container wrapper)
            if 'animation-player-content-resource' in classes:
                return True
            
            # Check for animation-player class (the actual player element)
            # Verify it's a real animation by checking for start button or animation-controls
            if 'animation-player' in classes:
                # Verify it has animation controls (start button)
                try:
                    element.find_element(By.CSS_SELECTOR, 'button[class*="start-button"]')
                    return True
                except:
                    # Maybe no start button, check for animation-controls
                    try:
                        element.find_element(By.CSS_SELECTOR, 'div.animation-controls')
                        return True
                    except:
                        pass
            
            return False
        except:
            return False
    
    def is_animation_complete(self, element):
        """Check if animation is completed"""
        try:
            chevron = element.find_element(By.CSS_SELECTOR, 'div[class*="zb-chevron"]')
            classes = chevron.get_attribute('class') or ''
            return 'filled' in classes or 'orange' in classes
        except:
            return False
    
    # ==========================================
    # Radio Question Detection
    # ==========================================
    
    def is_radio_question(self, element):
        """Check if element is a radio question"""
        try:
            classes = element.get_attribute('class') or ''
            
            # MUST NOT be a radio button wrapper (individual button)
            if 'zb-radio-button' in classes or 'radio-button' in classes:
                return False
            
            # MUST be the radiogroup container or question-choices container
            # Check for role="radiogroup"
            role = element.get_attribute('role')
            if role == 'radiogroup':
                # Verify it has radio inputs
                radios = element.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                return len(radios) > 0
            
            # Check for question-choices class
            if 'question-choices' in classes:
                # Verify it has radio inputs
                radios = element.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                return len(radios) > 0
            
            return False
        except:
            return False
    
    def is_radio_complete(self, element):
        """Check if radio question is completed"""
        try:
            # The element we detect is the radiogroup, but chevron is in parent container
            # Try to find chevron in parent first
            parent = element.find_element(By.XPATH, '..')
            if parent:
                try:
                    chevron = parent.find_element(By.CSS_SELECTOR, 'div.zb-chevron.question-chevron')
                    classes = chevron.get_attribute('class') or ''
                    if 'filled' in classes:
                        return True
                except:
                    pass
                
                # Try going up another level (sometimes it's in grandparent)
                try:
                    grandparent = parent.find_element(By.XPATH, '..')
                    chevron = grandparent.find_element(By.CSS_SELECTOR, 'div.zb-chevron.question-chevron')
                    classes = chevron.get_attribute('class') or ''
                    if 'filled' in classes:
                        return True
                except:
                    pass
        except:
            pass
        
        # Fallback: check if any radio is selected
        try:
            radios = element.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            return any(r.is_selected() for r in radios)
        except:
            return False
    
    # ==========================================
    # Short Answer Detection
    # ==========================================
    
    def is_short_answer(self, element):
        """Check if element is a short answer question"""
        try:
            classes = element.get_attribute('class') or ''
            return 'short-answer-question' in classes
        except:
            return False
    
    def is_short_answer_complete(self, element):
        """Check if short answer is completed"""
        try:
            chevron = element.find_element(By.CSS_SELECTOR, 'div.zb-chevron')
            classes = chevron.get_attribute('class') or ''
            return 'filled' in classes
        except:
            return False
    
    # ==========================================
    # Output Formatting
    # ==========================================
    
    def output_scan_results(self, questions):
        """Output formatted scan results to log"""
        self.logger.info("\n" + "="*50)
        self.logger.info("[SCAN RESULTS]")
        self.logger.info("="*50)
        self.logger.info(f"Found {len(questions)} questions on page:\n")
        
        if not questions:
            self.logger.info("No questions found!")
            self.logger.info("="*50 + "\n")
            return
        
        # Count by type
        counts = {}
        for q in questions:
            qtype = q['type']
            if qtype not in counts:
                counts[qtype] = {'total': 0, 'completed': 0, 'incomplete': 0}
            counts[qtype]['total'] += 1
            if q['completed']:
                counts[qtype]['completed'] += 1
            else:
                counts[qtype]['incomplete'] += 1
        
        # Type labels for display
        type_labels = {
            'animation': 'Animation',
            'radio': 'Radio',
            'short_answer': 'Short Answer',
        }
        
        # List all questions
        for idx, q in enumerate(questions, 1):
            label = type_labels.get(q['type'], q['type'])
            status = "✓ Completed" if q['completed'] else "✗ Incomplete"
            self.logger.info(f"{idx:2d}. [{label:13s}] {status}")
        
        # Summary
        self.logger.info("\nSummary:")
        for qtype, stats in sorted(counts.items()):
            label = type_labels.get(qtype, qtype)
            self.logger.info(
                f"- {label}: {stats['total']} total "
                f"({stats['completed']} completed, {stats['incomplete']} incomplete)"
            )
        self.logger.info("="*50 + "\n")
