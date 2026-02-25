"""
Configuration constants and CSS selectors for Zybooks Solver
"""

# Delays (in milliseconds)
MIN_BETWEEN_QUESTIONS = 500
MAX_BETWEEN_QUESTIONS = 1700
CHECK_INTERVAL = 100
ANIMATION_STEP_TIMEOUT = 30000
ANSWER_WAIT = 1000

# Max retries
MAX_RETRIES = 60

# CSS Selectors
SELECTORS = {
    'ANIMATIONS': {
        'container': 'div[class*="interactive-activity-container"][class*="animation-player"]',
        'chevron': 'div[class*="zb-chevron"][class*="title-bar-chevron"]',
        'speed_checkbox': 'div[class*="speed-control"] input[type="checkbox"]',
        'start_button': 'button[class*="start-button"]',
        'play_button': 'button[aria-label="Play"]',
    },
    
    'RADIO': {
        'content_resource': 'div[class*="content-resource"]',
        'question': 'div[class*="question"]',
        'radio_input': 'input[type="radio"]',
        'radio_button': 'div.zb-radio-button > input',
        'feedback_correct': 'div.zb-explanation.correct',
        'feedback_incorrect': 'div.zb-explanation.incorrect',
    },
    
    'SHORT_ANSWER': {
        'container': 'div.short-answer-content-resource',
        'question': 'div.question-set-question.short-answer-question',
        'textarea': 'textarea.zb-text-area',
        'show_answer': 'button.show-answer-button',
        'check': 'button.check-button',
        'answers': 'div.answers span.forfeit-answer',
    }
}
