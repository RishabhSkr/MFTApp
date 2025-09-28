
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import smtplib
import shutil
import os
import time
import threading
from datetime import datetime, timedelta
import argparse
import subprocess
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
class FileSchedulerApp:
    def __init__(self, root=None, config_file=None):
        # Set script_dir at the very top so it's always available
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        # Support for command-line execution
        self.gui_mode = root is not None
        self.config_file = config_file or 'file_scheduler_config.json'
        if self.gui_mode:
            self.root = root
            self.root.title("File Scheduler Application - Windows Task Scheduler Integration")
            self.root.geometry("900x700")

        # Initialize database
        self.init_database()

        # Configuration variables
        if self.gui_mode:
            self.source_path = tk.StringVar()
            self.destination_path = tk.StringVar()
            self.operation_type = tk.StringVar(value="copy")
            self.schedule_time = tk.StringVar(value="00:00")
            self.schedule_frequency = tk.StringVar(value="daily")

            # Date folder configuration
            self.use_date_folders = tk.BooleanVar(value=True)
            self.date_format = tk.StringVar(value="YYYY-MM-DD")
            self.date_folder_type = tk.StringVar(value="current")
            self.custom_date = tk.StringVar()

            # Email configuration
            self.smtp_server = tk.StringVar(value="smtp.gmail.com")
            self.smtp_port = tk.StringVar(value="587")
            self.sender_email = tk.StringVar()
            self.sender_password = tk.StringVar()
            self.recipient_email = tk.StringVar()
            self.use_tls = tk.BooleanVar(value=True)

            # Task name for Windows Task Scheduler
            self.task_name = tk.StringVar(value="FileScheduler_Task")
        else:
            # For command-line mode, load from config
            self.load_config_dict()

        if self.gui_mode:
            self.create_widgets()
            self.load_config()

    def init_database(self):
        """Initialize SQLite database for logging"""
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_scheduler_log.db')
        self.conn = sqlite3.connect(db_path, timeout=30.0)
        self.conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source_path TEXT NOT NULL,
                destination_path TEXT NOT NULL,
                final_destination TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                status TEXT NOT NULL,
                files_processed INTEGER,
                error_message TEXT,
                schedule_time TEXT,
                date_folder TEXT,
                execution_mode TEXT DEFAULT 'GUI'
            )
        """)
        self.conn.commit()
        print(f"Database initialized at: {db_path}")

    def create_widgets(self):
        """Create the GUI widgets"""
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # File Operations Tab
        self.create_file_ops_tab(notebook)

        # Windows Scheduler Tab
        self.create_scheduler_tab(notebook)

        # Email Settings Tab
        self.create_email_tab(notebook)

        # Logs Tab
        self.create_logs_tab(notebook)

        # Control buttons at bottom
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(control_frame, text="Create Windows Task", command=self.create_windows_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Delete Windows Task", command=self.delete_windows_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Run Once Now", command=self.run_once).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Preview Destination", command=self.preview_destination).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Save Config", command=self.save_config).pack(side=tk.RIGHT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def create_file_ops_tab(self, notebook):
        """Create file operations configuration tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="File Operations")

        # Source selection
        ttk.Label(frame, text="Source Path:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.source_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)

        # Destination selection
        ttk.Label(frame, text="Base Destination Path:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.destination_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_destination).grid(row=1, column=2, padx=5, pady=5)

        # Date folder configuration frame
        date_frame = ttk.LabelFrame(frame, text="Date-based Folder Organization")
        date_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=10)

        # Enable date folders checkbox
        ttk.Checkbutton(date_frame, text="Create date-based folders in destination", 
                       variable=self.use_date_folders, command=self.update_date_widgets).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        # Date format selection
        ttk.Label(date_frame, text="Date Format:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.date_format_combo = ttk.Combobox(date_frame, textvariable=self.date_format, width=15,
                                            values=["YYYY-MM-DD", "YYYY/MM/DD", "DD-MM-YYYY", "DD/MM/YYYY", "YYYYMMDD", "MM-DD-YYYY"])
        self.date_format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # Date type selection
        ttk.Label(date_frame, text="Date Source:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        date_type_frame = ttk.Frame(date_frame)
        date_type_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=2)

        ttk.Radiobutton(date_type_frame, text="Current Date", variable=self.date_folder_type, 
                       value="current", command=self.update_date_widgets).pack(side=tk.LEFT)
        ttk.Radiobutton(date_type_frame, text="Schedule Date", variable=self.date_folder_type, 
                       value="schedule", command=self.update_date_widgets).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(date_type_frame, text="Custom Date", variable=self.date_folder_type, 
                       value="custom", command=self.update_date_widgets).pack(side=tk.LEFT, padx=10)

        # Custom date entry
        ttk.Label(date_frame, text="Custom Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.custom_date_entry = ttk.Entry(date_frame, textvariable=self.custom_date, width=15)
        self.custom_date_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        # Preview label
        self.preview_label = ttk.Label(date_frame, text="Preview: ", foreground="blue")
        self.preview_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        # Operation type
        ttk.Label(frame, text="Operation:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        op_frame = ttk.Frame(frame)
        op_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(op_frame, text="Copy", variable=self.operation_type, value="copy").pack(side=tk.LEFT)
        ttk.Radiobutton(op_frame, text="Move", variable=self.operation_type, value="move").pack(side=tk.LEFT, padx=10)

        # Initialize date widgets
        self.update_date_widgets()

    def create_scheduler_tab(self, notebook):
        """Create Windows Task Scheduler configuration tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Windows Scheduler")

        # Task configuration
        task_frame = ttk.LabelFrame(frame, text="Windows Task Scheduler Configuration")
        task_frame.pack(fill=tk.X, padx=5, pady=5)

        # Task name
        ttk.Label(task_frame, text="Task Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(task_frame, textvariable=self.task_name, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Schedule configuration
        ttk.Label(task_frame, text="Schedule Time (HH:MM):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(task_frame, textvariable=self.schedule_time, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(task_frame, text="Frequency:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        freq_combo = ttk.Combobox(task_frame, textvariable=self.schedule_frequency, 
                                values=["daily", "weekly", "monthly", "once"], width=15)
        freq_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Task status frame
        status_frame = ttk.LabelFrame(frame, text="Task Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        # Status display
        self.task_status_var = tk.StringVar(value="No active Windows task")
        ttk.Label(status_frame, textvariable=self.task_status_var).pack(padx=5, pady=5)

        # Buttons for task management
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Check Task Status", command=self.check_task_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Windows Tasks", command=self.view_windows_tasks).pack(side=tk.LEFT, padx=5)

        # Information text
        info_text = tk.Text(frame, height=8, width=80, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        info_text.insert(tk.END, """Windows Task Scheduler Integration:

✅ PERSISTENT SCHEDULING: Tasks continue running even after closing this application
✅ SYSTEM INTEGRATION: Uses Windows native Task Scheduler service
✅ AUTOMATIC STARTUP: Tasks can run at system boot or user login
✅ RELIABILITY: Windows manages task execution and recovery

How it works:
1. Configure your file operation settings
2. Set schedule time and frequency
3. Click "Create Windows Task" to register with Windows Task Scheduler
4. Close this application - your scheduled task will continue running
5. Check Windows Task Scheduler (taskschd.msc) to view/manage tasks
6. Use "Delete Windows Task" to remove scheduled tasks

Task Execution:
- Tasks run in background using this same application in command-line mode
- All logging continues to work normally
- Email notifications are sent as configured
- Date-based folders are created as configured

Requirements:
- Administrator privileges may be required for some operations
- Python must be accessible from system PATH or full path will be used""")
        info_text.config(state=tk.DISABLED)

        # Update task status on tab creation
        self.root.after(1000, self.check_task_status)

    def create_email_tab(self, notebook):
        """Create email configuration tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Email Settings")

        # SMTP Configuration
        ttk.Label(frame, text="SMTP Server:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.smtp_server, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.smtp_port, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Checkbutton(frame, text="Use TLS", variable=self.use_tls).grid(row=1, column=2, padx=5, pady=5)

        # Email credentials
        ttk.Label(frame, text="Sender Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.sender_email, width=30).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Password:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.sender_password, width=30, show="*").grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Recipient Email:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.recipient_email, width=30).grid(row=4, column=1, padx=5, pady=5)

        # Test email button
        ttk.Button(frame, text="Test Email", command=self.test_email).grid(row=5, column=1, pady=10)

        # Email templates info
        help_frame = ttk.LabelFrame(frame, text="Email Templates")
        help_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=10, sticky=tk.W+tk.E)

        ttk.Label(help_frame, text="Success: File operation completed with date folder information").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(help_frame, text="Failure: File operation failed with error details and attempted path").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(help_frame, text="Windows Task: Automated execution via Windows Task Scheduler").pack(anchor=tk.W, padx=5, pady=2)

    def create_logs_tab(self, notebook):
        """Create logs viewing tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Logs")

        # Logs tree view
        columns = ('Timestamp', 'Operation', 'Status', 'Files', 'Date Folder', 'Mode', 'Source', 'Final Destination')
        self.logs_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)

        # Configure columns
        column_widths = {'Timestamp': 130, 'Operation': 70, 'Status': 70, 'Files': 50, 
                        'Date Folder': 90, 'Mode': 60, 'Source': 120, 'Final Destination': 120}

        for col in columns:
            self.logs_tree.heading(col, text=col)
            self.logs_tree.column(col, width=column_widths.get(col, 100))

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.logs_tree.xview)
        self.logs_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack logs components
        self.logs_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Log management buttons
        log_button_frame = ttk.Frame(frame)
        log_button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(log_button_frame, text="Refresh Logs", command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_button_frame, text="Clear Old Logs (>30 days)", command=self.clear_old_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_button_frame, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)

        # Load initial logs
        self.refresh_logs()

    def update_date_widgets(self):
        """Update date-related widgets based on current settings"""
        if not self.gui_mode:
            return

        enabled = self.use_date_folders.get()

        # Enable/disable date format combo
        self.date_format_combo.configure(state="normal" if enabled else "disabled")

        # Enable/disable custom date entry
        self.custom_date_entry.configure(state="normal" if enabled and self.date_folder_type.get() == "custom" else "disabled")

        # Update preview
        self.update_preview()

    def update_preview(self):
        """Update the destination preview"""
        if not self.gui_mode:
            return

        if not self.use_date_folders.get():
            preview_text = f"Preview: {self.destination_path.get() or '[Base Destination]'}"
        else:
            base_dest = self.destination_path.get() or "[Base Destination]"
            date_folder = self.get_date_folder_name()
            preview_text = f"Preview: {base_dest}/{date_folder}"

        self.preview_label.configure(text=preview_text)

    def get_date_folder_name(self, operation_date=None):
        """Generate date folder name based on current settings"""
        use_date_folders = self.use_date_folders.get() if self.gui_mode else self.config.get('use_date_folders', True)
        if not use_date_folders:
            return ""

        date_folder_type = self.date_folder_type.get() if self.gui_mode else self.config.get('date_folder_type', 'current')

        # Determine which date to use
        if date_folder_type == "current":
            date_obj = datetime.now()
        elif date_folder_type == "schedule":
            date_obj = operation_date or datetime.now()
        else:  # custom
            custom_date = self.custom_date.get() if self.gui_mode else self.config.get('custom_date', '')
            try:
                date_obj = datetime.strptime(custom_date, "%Y-%m-%d")
            except ValueError:
                date_obj = datetime.now()

        # Format according to selected format
        format_map = {
            "YYYY-MM-DD": "%Y-%m-%d",
            "YYYY/MM/DD": "%Y/%m/%d",
            "DD-MM-YYYY": "%d-%m-%Y",
            "DD/MM/YYYY": "%d/%m/%Y",
            "YYYYMMDD": "%Y%m%d",
            "MM-DD-YYYY": "%m-%d-%Y"
        }

        date_format = self.date_format.get() if self.gui_mode else self.config.get('date_format', 'YYYY-MM-DD')
        format_str = format_map.get(date_format, "%Y-%m-%d")
        return date_obj.strftime(format_str)

    def browse_source(self):
        """Browse for source directory"""
        path = filedialog.askdirectory(title="Select Source Directory")
        if path:
            self.source_path.set(path)
            self.update_preview()

    def browse_destination(self):
        """Browse for destination directory"""
        path = filedialog.askdirectory(title="Select Base Destination Directory")
        if path:
            self.destination_path.set(path)
            self.update_preview()

    def preview_destination(self):
        """Show a preview of the final destination path"""
        destination_path = self.destination_path.get() if self.gui_mode else self.config.get('destination_path', '')
        if not destination_path:
            messagebox.showwarning("Warning", "Please select a base destination path first.")
            return

        date_folder = self.get_date_folder_name()
        use_date_folders = self.use_date_folders.get() if self.gui_mode else self.config.get('use_date_folders', True)

        if use_date_folders:
            final_dest = os.path.join(destination_path, date_folder)
            message = f"Files will be copied/moved to:\n\n{final_dest}\n\nDate folder: {date_folder}"
        else:
            final_dest = destination_path
            message = f"Files will be copied/moved to:\n\n{final_dest}\n\nNo date folder will be created."

        messagebox.showinfo("Destination Preview", message)

    def create_windows_task(self):
        """Create a Windows Task Scheduler task"""
        try:
            # Validate configuration
            if not all([self.source_path.get(), self.destination_path.get(), self.task_name.get()]):
                messagebox.showerror("Error", "Please configure source path, destination path, and task name.")
                return

            # Save current configuration
            self.save_config()

            # Get Python executable path
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)
            config_path = os.path.join(self.script_dir, self.config_file)

            # Build command arguments
            task_command = f'"{python_exe}" "{script_path}" --batch --config "{config_path}"'

            # Build schtasks command
            task_name = self.task_name.get()
            schedule_time = self.schedule_time.get()
            frequency = self.schedule_frequency.get().upper()

            # Delete existing task if it exists
            try:
                subprocess.run(f'schtasks /delete /tn "{task_name}" /f', 
                             shell=True, capture_output=True, check=False)
            except:
                pass

            # Create schtasks command based on frequency
            if frequency == "DAILY":
                schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{task_command}" /sc daily /st {schedule_time} /f'
            elif frequency == "WEEKLY":
                schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{task_command}" /sc weekly /st {schedule_time} /f'
            elif frequency == "MONTHLY":
                schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{task_command}" /sc monthly /st {schedule_time} /f'
            elif frequency == "ONCE":
                # For once, we'll schedule it for tomorrow at the specified time
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%m/%d/%Y')
                schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{task_command}" /sc once /sd {tomorrow} /st {schedule_time} /f'
            else:
                messagebox.showerror("Error", f"Unsupported frequency: {frequency}")
                return

            print(f"Creating task with command: {schtasks_cmd}")

            # Execute schtasks command
            result = subprocess.run(schtasks_cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.status_var.set("Windows task created successfully")
                messagebox.showinfo("Success", 
                    f"Windows Task Scheduler task '{task_name}' created successfully!\n\n"
                    f"Schedule: {frequency} at {schedule_time}\n"
                    f"The task will continue running even after closing this application.\n\n"
                    f"View in Task Scheduler: taskschd.msc")
                self.check_task_status()
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                print(f"Error creating task: {error_msg}")
                messagebox.showerror("Error", f"Failed to create Windows task:\n{error_msg}")

        except Exception as e:
            print(f"Exception creating task: {str(e)}")
            messagebox.showerror("Error", f"Failed to create Windows task:\n{str(e)}")

    def delete_windows_task(self):
        """Delete the Windows Task Scheduler task"""
        try:
            task_name = self.task_name.get()
            if not task_name:
                messagebox.showerror("Error", "Please specify a task name.")
                return

            # Confirm deletion
            if not messagebox.askyesno("Confirm Deletion", 
                f"Are you sure you want to delete the Windows task '{task_name}'?"):
                return

            # Delete the task
            result = subprocess.run(f'schtasks /delete /tn "{task_name}" /f', 
                                  shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.status_var.set("Windows task deleted successfully")
                messagebox.showinfo("Success", f"Windows task '{task_name}' deleted successfully!")
                self.check_task_status()
            else:
                error_msg = result.stderr or result.stdout or "Task not found"
                messagebox.showinfo("Info", f"Task deletion result:\n{error_msg}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete Windows task:\n{str(e)}")

    def check_task_status(self):
        """Check if Windows task exists and is scheduled"""
        if not self.gui_mode:
            return

        try:
            task_name = self.task_name.get()
            if not task_name:
                self.task_status_var.set("No task name specified")
                return

            # Query the specific task
            result = subprocess.run(f'schtasks /query /tn "{task_name}" /fo list', 
                                  shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                # Parse the output to get task info
                lines = result.stdout.split('\n')
                status = "Unknown"
                next_run = "Unknown"

                for line in lines:
                    if "Status:" in line:
                        status = line.split("Status:")[1].strip()
                    elif "Next Run Time:" in line:
                        next_run = line.split("Next Run Time:")[1].strip()

                self.task_status_var.set(f"Task '{task_name}' exists - Status: {status}\nNext Run: {next_run}")
            else:
                self.task_status_var.set(f"Task '{task_name}' not found in Windows Task Scheduler")

        except Exception as e:
            self.task_status_var.set(f"Error checking task status: {str(e)}")

    def view_windows_tasks(self):
        """Open Windows Task Scheduler"""
        try:
            subprocess.run("taskschd.msc", shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Task Scheduler:\n{str(e)}")

    def perform_file_operation(self):
        """Perform the actual file copy/move operation"""
        execution_mode = "GUI" if self.gui_mode else "BATCH"

        # Get configuration values
        if self.gui_mode:
            source = self.source_path.get()
            base_destination = self.destination_path.get()
            operation = self.operation_type.get()
        else:
            source = self.config.get('source_path', '')
            base_destination = self.config.get('destination_path', '')
            operation = self.config.get('operation_type', 'copy')

        print(f"[{execution_mode}] Starting file operation: {operation}")
        print(f"[{execution_mode}] Source: {source}")
        print(f"[{execution_mode}] Base destination: {base_destination}")

        if not source or not base_destination:
            error_msg = "Source or destination path not specified"
            print(f"[{execution_mode}] Error: {error_msg}")
            self.log_operation("ERROR", error_msg, 0, "Missing paths", "", execution_mode)
            return False

        try:
            # Determine final destination with date folder
            operation_date = datetime.now()
            date_folder = self.get_date_folder_name(operation_date)

            if date_folder:
                final_destination = os.path.join(base_destination, date_folder)
                print(f"[{execution_mode}] Date folder: {date_folder}")
            else:
                final_destination = base_destination
                print(f"[{execution_mode}] No date folder")

            print(f"[{execution_mode}] Final destination: {final_destination}")

            # Ensure destination directory exists
            os.makedirs(final_destination, exist_ok=True)
            print(f"[{execution_mode}] Created destination directory")

            files_processed = 0
            start_time = datetime.now()

            # Get list of files to process
            if os.path.isfile(source):
                files_to_process = [source]
                print(f"[{execution_mode}] Processing single file")
            else:
                files_to_process = []
                for root, dirs, files in os.walk(source):
                    for file in files:
                        files_to_process.append(os.path.join(root, file))
                print(f"[{execution_mode}] Found {len(files_to_process)} files to process")

            for file_path in files_to_process:
                try:
                    if os.path.isfile(source):
                        # Single file operation
                        dest_file = os.path.join(final_destination, os.path.basename(file_path))
                    else:
                        # Directory operation - maintain structure
                        rel_path = os.path.relpath(file_path, source)
                        dest_file = os.path.join(final_destination, rel_path)
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                    if operation == "copy":
                        shutil.copy2(file_path, dest_file)
                    else:  # move
                        shutil.move(file_path, dest_file)

                    files_processed += 1

                    if files_processed % 10 == 0:  # Progress update every 10 files
                        print(f"[{execution_mode}] Processed {files_processed} files...")

                except Exception as e:
                    error_msg = f"Failed to {operation} {file_path}: {str(e)}"
                    print(f"[{execution_mode}] File error: {error_msg}")
                    self.log_operation("ERROR", error_msg, files_processed, str(e), date_folder, execution_mode)
                    return False

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Log success
            success_msg = f"{operation.title()} operation completed"
            if date_folder:
                success_msg += f" to date folder '{date_folder}'"

            details = f"Processed {files_processed} files in {duration:.2f} seconds"
            print(f"[{execution_mode}] Success: {success_msg}")
            print(f"[{execution_mode}] {details}")

            self.log_operation("SUCCESS", success_msg, files_processed, details, date_folder, execution_mode)

            # Send success email
            self.send_notification_email("SUCCESS", files_processed, duration, final_destination, date_folder, execution_mode)

            if self.gui_mode:
                self.status_var.set(f"Operation completed: {files_processed} files processed")

            return True

        except Exception as e:
            error_msg = f"Operation failed: {str(e)}"
            print(f"[{execution_mode}] Exception: {error_msg}")
            self.log_operation("ERROR", error_msg, 0, str(e), date_folder if 'date_folder' in locals() else "", execution_mode)
            self.send_notification_email("ERROR", 0, 0, "", "", execution_mode, str(e))
            return False

    def log_operation(self, status, message, files_processed, details, date_folder, execution_mode="GUI"):
        """Log operation to database with improved error handling"""
        try:
            # Ensure database connection is valid
            if not self.conn:
                self.init_database()

            cursor = self.conn.cursor()

            # Get configuration values safely
            if self.gui_mode:
                source_path = self.source_path.get()
                destination_path = self.destination_path.get()
                operation_type = self.operation_type.get()
                schedule_time = self.schedule_time.get()
                final_dest = os.path.join(destination_path, date_folder) if date_folder else destination_path
            else:
                source_path = self.config.get('source_path', 'Unknown')
                destination_path = self.config.get('destination_path', 'Unknown')
                operation_type = self.config.get('operation_type', 'Unknown')
                schedule_time = self.config.get('schedule_time', 'Unknown')
                final_dest = os.path.join(destination_path, date_folder) if date_folder else destination_path

            # Insert log record
            cursor.execute("""
                INSERT INTO file_operations 
                (timestamp, source_path, destination_path, final_destination, operation_type, status, 
                 files_processed, error_message, schedule_time, date_folder, execution_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                source_path,
                destination_path,
                final_dest,
                operation_type,
                status,
                files_processed,
                details,
                schedule_time,
                date_folder,
                execution_mode
            ))
            self.conn.commit()

            print(f"[{execution_mode}] Log entry created: {status} - {message}")

            # Update status bar if in GUI mode
            if self.gui_mode:
                self.status_var.set(f"{status}: {message}")

            # Refresh logs if visible
            if self.gui_mode:
                try:
                    self.refresh_logs()
                except:
                    pass

        except Exception as e:
            print(f"[{execution_mode}] Failed to log operation: {str(e)}")
            # Don't raise the exception to avoid breaking the main operation

    def send_notification_email(self, status, files_processed, duration, final_destination="", 
                              date_folder="", execution_mode="GUI", error_msg=None):
        """Send email notification"""
        try:
            # Get email configuration
            if self.gui_mode:
                smtp_server = self.smtp_server.get()
                smtp_port = self.smtp_port.get()
                sender_email = self.sender_email.get()
                sender_password = self.sender_password.get()
                recipient_email = self.recipient_email.get()
                use_tls = self.use_tls.get()
                operation_type = self.operation_type.get()
                source_path = self.source_path.get()
                destination_path = self.destination_path.get()
            else:
                smtp_server = self.config.get('smtp_server', '')
                smtp_port = self.config.get('smtp_port', '587')
                sender_email = self.config.get('sender_email', '')
                sender_password = self.config.get('sender_password', '')
                recipient_email = self.config.get('recipient_email', '')
                use_tls = self.config.get('use_tls', True)
                operation_type = self.config.get('operation_type', 'unknown')
                source_path = self.config.get('source_path', 'unknown')
                destination_path = self.config.get('destination_path', 'unknown')

            if not all([sender_email, sender_password, recipient_email]):
                print(f"[{execution_mode}] Email not configured, skipping notification")
                return  # Email not configured

            print(f"[{execution_mode}] Sending email notification...")

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email

            if status == "SUCCESS":
                msg['Subject'] = f"File Scheduler - {operation_type.title()} Operation Successful ({execution_mode})"
                body = f"""
File {operation_type} operation completed successfully!

Execution Mode: {execution_mode}
Details:
- Source: {source_path}
- Base Destination: {destination_path}
- Final Destination: {final_destination}
- Operation: {operation_type.title()}
- Files processed: {files_processed}
- Duration: {duration:.2f} seconds
- Date Folder: {date_folder if date_folder else 'None (disabled)'}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated message from File Scheduler Application.
                """
            else:
                msg['Subject'] = f"File Scheduler - {operation_type.title()} Operation Failed ({execution_mode})"
                body = f"""
File {operation_type} operation failed!

Execution Mode: {execution_mode}
Details:
- Source: {source_path}
- Base Destination: {destination_path}
- Operation: {operation_type.title()}
- Date Folder Setting: {date_folder if date_folder else 'None (disabled)'}
- Error: {error_msg}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the application logs for more details.

This is an automated message from File Scheduler Application.
                """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            if use_tls:
                server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()

            print(f"[{execution_mode}] Email notification sent successfully")

        except Exception as e:
            print(f"[{execution_mode}] Failed to send email notification: {str(e)}")

    def test_email(self):
        """Test email configuration"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email.get()
            msg['To'] = self.recipient_email.get()
            msg['Subject'] = "File Scheduler - Test Email (Windows Task Scheduler Integration)"

            preview_dest = "Not configured"
            if self.destination_path.get():
                date_folder = self.get_date_folder_name()
                if self.use_date_folders.get() and date_folder:
                    preview_dest = f"{self.destination_path.get()}/{date_folder}"
                else:
                    preview_dest = self.destination_path.get()

            body = f"""This is a test email from File Scheduler Application with Windows Task Scheduler Integration.

Current Configuration:
- Email configuration is working correctly!
- Date folders: {'Enabled' if self.use_date_folders.get() else 'Disabled'}
- Preview destination: {preview_dest}
- Current date folder would be: {self.get_date_folder_name() if self.use_date_folders.get() else 'N/A'}
- Task Name: {self.task_name.get()}
- Schedule: {self.schedule_frequency.get()} at {self.schedule_time.get()}

Windows Task Scheduler Integration:
- Tasks will persist after application closes
- Background execution with full logging
- Email notifications continue to work
- All date folder functionality preserved

Test completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!"""

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server.get(), int(self.smtp_port.get()))
            if self.use_tls.get():
                server.starttls()
            server.login(self.sender_email.get(), self.sender_password.get())
            server.sendmail(self.sender_email.get(), self.recipient_email.get(), msg.as_string())
            server.quit()

            messagebox.showinfo("Success", "Test email sent successfully!\nCheck your email for configuration details.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test email:\n{str(e)}")

    def refresh_logs(self):
        """Refresh the logs tree view"""
        if not self.gui_mode:
            return

        # Clear existing items
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)

        try:
            # Load from database
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT timestamp, operation_type, status, files_processed, date_folder, 
                       execution_mode, source_path, final_destination
                FROM file_operations
                ORDER BY timestamp DESC
                LIMIT 200
            """)

            for row in cursor.fetchall():
                # Format timestamp
                try:
                    timestamp = datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp = row[0]

                # Handle date folder display
                date_folder = row[4] if row[4] else "None"

                # Handle execution mode
                execution_mode = row[5] if row[5] else "GUI"

                # Truncate long paths
                source = row[6][:20] + "..." if len(row[6]) > 20 else row[6]
                final_dest = row[7][:20] + "..." if len(row[7]) > 20 else row[7]

                self.logs_tree.insert('', 'end', values=(
                    timestamp, row[1].title() if row[1] else "Unknown", row[2], 
                    row[3], date_folder, execution_mode, source, final_dest
                ))

        except Exception as e:
            print(f"Error refreshing logs: {str(e)}")

    def clear_old_logs(self):
        """Clear logs older than 30 days"""
        try:
            if messagebox.askyesno("Confirm", "Clear all logs older than 30 days?"):
                cursor = self.conn.cursor()
                cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
                cursor.execute("DELETE FROM file_operations WHERE timestamp < ?", (cutoff_date,))
                deleted_count = cursor.rowcount
                self.conn.commit()

                messagebox.showinfo("Success", f"Deleted {deleted_count} old log entries.")
                self.refresh_logs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear old logs:\n{str(e)}")

    def export_logs(self):
        """Export logs to CSV file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT timestamp, source_path, destination_path, final_destination,
                           operation_type, status, files_processed, error_message,
                           schedule_time, date_folder, execution_mode
                    FROM file_operations
                    ORDER BY timestamp DESC
                """)

                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    import csv
                    writer = csv.writer(csvfile)
                    writer.writerow(['Timestamp', 'Source Path', 'Destination Path', 'Final Destination',
                                   'Operation Type', 'Status', 'Files Processed', 'Error Message',
                                   'Schedule Time', 'Date Folder', 'Execution Mode'])
                    writer.writerows(cursor.fetchall())

                messagebox.showinfo("Success", f"Logs exported to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs:\n{str(e)}")

    def run_once(self):
        """Run the file operation once immediately"""
        if self.gui_mode:
            self.status_var.set("Running operation...")
            threading.Thread(target=self.perform_file_operation, daemon=True).start()
        else:
            self.perform_file_operation()

    def save_config(self):
        """Save configuration to file"""
        config = {
            'source_path': self.source_path.get() if self.gui_mode else self.config.get('source_path', ''),
            'destination_path': self.destination_path.get() if self.gui_mode else self.config.get('destination_path', ''),
            'operation_type': self.operation_type.get() if self.gui_mode else self.config.get('operation_type', 'copy'),
            'schedule_time': self.schedule_time.get() if self.gui_mode else self.config.get('schedule_time', '00:00'),
            'schedule_frequency': self.schedule_frequency.get() if self.gui_mode else self.config.get('schedule_frequency', 'daily'),
            'use_date_folders': self.use_date_folders.get() if self.gui_mode else self.config.get('use_date_folders', True),
            'date_format': self.date_format.get() if self.gui_mode else self.config.get('date_format', 'YYYY-MM-DD'),
            'date_folder_type': self.date_folder_type.get() if self.gui_mode else self.config.get('date_folder_type', 'current'),
            'custom_date': self.custom_date.get() if self.gui_mode else self.config.get('custom_date', ''),
            'smtp_server': self.smtp_server.get() if self.gui_mode else self.config.get('smtp_server', 'smtp.gmail.com'),
            'smtp_port': self.smtp_port.get() if self.gui_mode else self.config.get('smtp_port', '587'),
            'sender_email': self.sender_email.get() if self.gui_mode else self.config.get('sender_email', ''),
            'sender_password': self.sender_password.get() if self.gui_mode else self.config.get('sender_password', ''),
            'recipient_email': self.recipient_email.get() if self.gui_mode else self.config.get('recipient_email', ''),
            'use_tls': self.use_tls.get() if self.gui_mode else self.config.get('use_tls', True),
            'task_name': self.task_name.get() if self.gui_mode else self.config.get('task_name', 'FileScheduler_Task')
        }

        try:
            config_path = os.path.join(self.script_dir, self.config_file)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            if self.gui_mode:
                messagebox.showinfo("Success", f"Configuration saved to:\n{config_path}")
            else:
                print(f"Configuration saved to: {config_path}")

        except Exception as e:
            error_msg = f"Failed to save configuration: {str(e)}"
            if self.gui_mode:
                messagebox.showerror("Error", error_msg)
            else:
                print(error_msg)

    def load_config(self):
        """Load configuration from file"""
        try:
            config_path = os.path.join(self.script_dir, self.config_file)
            with open(config_path, 'r') as f:
                config = json.load(f)

            if self.gui_mode:
                self.source_path.set(config.get('source_path', ''))
                self.destination_path.set(config.get('destination_path', ''))
                self.operation_type.set(config.get('operation_type', 'copy'))
                self.schedule_time.set(config.get('schedule_time', '00:00'))
                self.schedule_frequency.set(config.get('schedule_frequency', 'daily'))
                self.use_date_folders.set(config.get('use_date_folders', True))
                self.date_format.set(config.get('date_format', 'YYYY-MM-DD'))
                self.date_folder_type.set(config.get('date_folder_type', 'current'))
                self.custom_date.set(config.get('custom_date', ''))
                self.smtp_server.set(config.get('smtp_server', 'smtp.gmail.com'))
                self.smtp_port.set(config.get('smtp_port', '587'))
                self.sender_email.set(config.get('sender_email', ''))
                self.sender_password.set(config.get('sender_password', ''))
                self.recipient_email.set(config.get('recipient_email', ''))
                self.use_tls.set(config.get('use_tls', True))
                self.task_name.set(config.get('task_name', 'FileScheduler_Task'))

                # Update widgets after loading
                self.update_date_widgets()

        except FileNotFoundError:
            # Set default custom date to today
            if self.gui_mode:
                self.custom_date.set(datetime.now().strftime('%Y-%m-%d'))
                self.update_date_widgets()
        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            if self.gui_mode:
                messagebox.showerror("Error", error_msg)
                self.custom_date.set(datetime.now().strftime('%Y-%m-%d'))
                self.update_date_widgets()
            else:
                print(error_msg)

    def load_config_dict(self):
        """Load configuration as dictionary for batch mode"""
        try:
            config_path = os.path.join(self.script_dir, self.config_file)
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            print(f"Configuration loaded from: {config_path}")
        except Exception as e:
            print(f"Failed to load configuration: {str(e)}")
            self.config = {}

    def on_closing(self):
        """Handle application closing"""
        if self.conn:
            self.conn.close()

        if self.gui_mode:
            self.root.destroy()

def main():
    """Main function to handle both GUI and command-line execution"""
    parser = argparse.ArgumentParser(description='File Scheduler Application')
    parser.add_argument('--batch', action='store_true', help='Run in batch mode (no GUI)')
    parser.add_argument('--config', help='Configuration file path')

    args = parser.parse_args()

    if args.batch:
        # Command-line/batch execution
        print("Starting File Scheduler in batch mode...")
        app = FileSchedulerApp(root=None, config_file=args.config)
        success = app.perform_file_operation()
        app.on_closing()

        if success:
            print("Batch operation completed successfully")
            sys.exit(0)
        else:
            print("Batch operation failed")
            sys.exit(1)
    else:
        # GUI execution
        print("Starting File Scheduler in GUI mode...")
        root = tk.Tk()
        app = FileSchedulerApp(root, config_file=args.config)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()

if __name__ == "__main__":
    main()
