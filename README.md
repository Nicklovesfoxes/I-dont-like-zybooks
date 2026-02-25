# Zybooks Solver

Automated solver for Zybooks educational platform questions using Selenium WebDriver.

## Project Structure

```
zybooks_solver/
├── main.py                    # Entry point - launches GUI and browser
├── config.py                  # Constants, selectors, delays
├── requirements.txt           # Python dependencies
├── gui/
│   ├── __init__.py
│   └── control_panel.py      # tkinter GUI control panel
├── solvers/
│   ├── __init__.py
│   ├── base_solver.py        # Base class with common methods
│   ├── radio_solver.py       # ✓ FULLY IMPLEMENTED
│   ├── animation_solver.py   # ✗ Stub (not implemented)
│   ├── clickable_solver.py   # ✗ Stub (not implemented)
│   ├── short_answer_solver.py # ✗ Stub (not implemented)
│   └── drag_drop_solver.py   # ✗ Stub (not implemented)
└── utils/
    ├── __init__.py
    ├── browser.py            # Browser setup/control
    └── logger.py             # Logging utilities
```

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. A Chrome browser window will open and navigate to Zybooks
3. A control panel GUI will appear
4. Manually log in to Zybooks in the browser window
5. Navigate to the chapter/section you want to solve
6. Select an action from the dropdown in the control panel
7. Optionally enable "Force Mode" to re-solve completed questions
8. Click "Run" to start the solver
9. Click "Stop" to halt execution at any time
10. Click "Show Output" to see detailed logs

## Implemented Features

### ✓ Radio Question Solver
- Fully functional solver for multiple choice and True/False questions
- Automatically detects and skips completed questions (unless Force Mode enabled)
- Tries each option until correct answer is found
- Proper feedback detection at document level
- Random delays between questions to appear more human-like

### ✗ Other Solvers (Not Yet Implemented)
- Animation Solver
- Clickable Question Solver
- Short Answer Solver
- Drag & Drop Solver

These solvers currently just print a "not implemented" message.

## Features

- **GUI Control Panel**: Easy-to-use interface with tkinter
- **Force Mode**: Re-solve already completed questions
- **Stop/Start Control**: Pause execution at any time
- **Detailed Logging**: Timestamped logs with success/error indicators
- **Threading**: Non-blocking execution prevents GUI freezing
- **Modular Design**: Easy to extend with new solver types

## Development Notes

- Only Radio Question Solver is currently implemented
- Other solvers are stubbed out and ready for implementation
- Follows the specification from `zybooks-solver-python-spec.txt`
- Uses thread-safe logging with GUI callbacks
