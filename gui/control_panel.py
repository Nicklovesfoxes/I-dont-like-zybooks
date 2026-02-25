"""
GUI Control Panel for Zybooks Solver
"""
import tkinter as tk
from tkinter import scrolledtext
import threading


class ControlPanel:
    """Main GUI control panel for the Zybooks Solver"""
    
    def __init__(self, solver_manager):
        """
        Args:
            solver_manager: SolverManager instance to control solvers
        """
        self.solver_manager = solver_manager
        
        # Setup main window
        self.root = tk.Tk()
        self.root.title("Zybooks Solver")
        self.root.geometry("400x600")
        
        # Action selection dropdown
        self.action_var = tk.StringVar(value="Select Action...")
        self.dropdown = tk.OptionMenu(
            self.root,
            self.action_var,
            "Select Action...",
            "Scan Only",
            "Solve All On Page",
            "Solve All (Continuous)",
            "Solve Radio Questions",
            "Solve Animations",
            "Solve Short Answer",
        )
        self.dropdown.pack(pady=10, fill=tk.X, padx=10)
        
        # Force mode checkbox
        self.force_mode = tk.BooleanVar()
        self.force_check = tk.Checkbutton(
            self.root,
            text="Force Mode (re-solve completed questions)",
            variable=self.force_mode
        )
        self.force_check.pack(pady=5)
        
        # Run/Stop buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10, fill=tk.X, padx=10)
        
        self.run_btn = tk.Button(
            btn_frame,
            text="Run",
            command=self.on_run,
            bg="#28a745",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.run_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="Stop",
            command=self.on_stop,
            bg="#dc3545",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        
        # Toggle output button
        self.output_visible = False
        self.toggle_btn = tk.Button(
            self.root,
            text="Show Output",
            command=self.toggle_output
        )
        self.toggle_btn.pack(pady=5, fill=tk.X, padx=10)
        
        # Output text area (initially hidden)
        self.output = scrolledtext.ScrolledText(
            self.root,
            height=20,
            state='disabled',
            wrap=tk.WORD
        )
        
        self.is_running = False
    
    def toggle_output(self):
        """Toggle visibility of output panel"""
        self.output_visible = not self.output_visible
        if self.output_visible:
            self.output.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)
            self.toggle_btn.config(text="Hide Output")
        else:
            self.output.pack_forget()
            self.toggle_btn.config(text="Show Output")
    
    def log(self, message):
        """
        Add a log message to the output panel
        
        Args:
            message: Message to log (should already include timestamp)
        """
        self.output.config(state='normal')
        self.output.insert(tk.END, message + '\n')
        self.output.see(tk.END)
        self.output.config(state='disabled')
    
    def on_run(self):
        """Handle Run button click"""
        action = self.action_var.get()
        
        if action == "Select Action...":
            self.log("Please select an action from the dropdown")
            return
        
        self.is_running = True
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        force = self.force_mode.get()
        
        # Start solver in separate thread to prevent GUI freezing
        thread = threading.Thread(
            target=self.run_solver,
            args=(action, force),
            daemon=True
        )
        thread.start()
    
    def on_stop(self):
        """Handle Stop button click"""
        self.solver_manager.stop()
        self.log("Stop requested...")
        self.stop_btn.config(state=tk.DISABLED)
    
    def run_solver(self, action, force):
        """
        Run the selected solver in a background thread
        
        Args:
            action: Selected action from dropdown
            force: Force mode enabled
        """
        try:
            self.solver_manager.run(action, force)
        except Exception as e:
            self.log(f"ERROR: {e}")
        finally:
            # Re-enable run button
            self.root.after(0, self.reset_buttons)
    
    def reset_buttons(self):
        """Reset button states after solver completes"""
        self.is_running = False
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def start(self):
        """Start the GUI main loop"""
        self.root.mainloop()
