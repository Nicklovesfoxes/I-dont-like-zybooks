# I Don't Like Zybooks

An automated Zybooks solver built with Python and Selenium WebDriver to help students complete interactive exercises more efficiently.

## ✨ Features

- **🎯 Multiple Question Types**: Supports radio/multiple choice questions with additional solver types in development
- **🖥️ User-Friendly GUI**: Clean tkinter interface with real-time logging
- **⚡ Force Mode**: Re-solve already completed questions
- **🛑 Stop/Start Control**: Pause and resume execution anytime
- **🔄 Automated Browser**: Handles Zybooks navigation with Selenium
- **📝 Detailed Logging**: Timestamped logs with success/error tracking
- **🧵 Threaded Execution**: Non-blocking design keeps GUI responsive
- **🎲 Randomized Delays**: Human-like timing to avoid detection

## 📂 Project Structure

```
I-dont-like-zybooks/
├── main.py                    # Application entry point
├── config.py                  # Configuration & selectors
├── requirements.txt           # Python dependencies
├── gui/
│   ├── __init__.py
│   └── control_panel.py      # GUI control panel
├── solvers/
│   ├── __init__.py
│   ├── base_solver.py        # Base solver class
│   ├── radio_solver.py       # ✓ Multiple choice/True-False
│   ├── animation_solver.py   # 🚧 In progress
│   ├── question_scanner.py   # Question detection utilities
│   └── short_answer_solver.py # 🚧 In progress
└── utils/
    ├── __init__.py
    ├── browser.py            # Chrome WebDriver setup
    ├── logger.py             # Logging system
    └── timing.py             # Delay utilities
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- Git (for cloning)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nicklovesfoxes/I-dont-like-zybooks.git
   cd I-dont-like-zybooks
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📖 Usage

1. **Launch the application**
   ```bash
   python main.py
   ```

2. **Sign in to Zybooks**
   - Chrome will open automatically
   - Log in to your Zybooks account manually
   - Navigate to your desired chapter/section

3. **Use the control panel**
   - Select a solver from the dropdown menu
   - Enable "Force Mode" if you want to re-solve completed questions
   - Click "Run" to start solving
   - Click "Stop" to pause execution
   - Click "Show Output" for detailed logs

## ✅ Solver Status

| Solver Type | Status | Description |
|------------|--------|-------------|
| Radio Questions | ✅ Complete | Multiple choice & True/False questions |
| Animation | 🚧 In Progress | Interactive animation exercises |
| Short Answer | 🚧 In Progress | Text-based answer fields |
| Clickable | ⏳ Planned | Click-based interactions |
| Drag & Drop | ⏳ Planned | Drag-and-drop exercises |

## 🛠️ Technical Details

### Technologies Used
- **Python 3.8+**: Core programming language
- **Selenium WebDriver**: Browser automation
- **tkinter**: GUI framework
- **Threading**: Asynchronous execution
- **Chrome Driver**: Browser control

### Architecture
- **Modular Design**: Each solver type is independent
- **Base Solver Class**: Shared functionality across all solvers
- **Thread-Safe Logging**: Real-time GUI updates without blocking
- **Configuration Management**: Centralized settings in `config.py`

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is for educational purposes. Use responsibly.

## 👤 Author

**Nicklovesfoxes**
- GitHub: [@Nicklovesfoxes](https://github.com/Nicklovesfoxes)
- Repository: [I-dont-like-zybooks](https://github.com/Nicklovesfoxes/I-dont-like-zybooks)