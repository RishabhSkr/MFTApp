import tkinter as tk
from tkinter import ttk
from config.config import save_config
from scheduler.task_scheduler import create_windows_task, delete_windows_task, check_task_status
from fileOperation.fileOperations import run_once
from utils.utils import preview_destination,view_windows_tasks
from emailer.email import test_email
from database.db import refresh_logs,clear_old_logs,export_logs
def create_file_ops_tab(self,notebook):

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

    # Network share fields
    ttk.Label(frame, text="Network Share Path:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    self.network_path = tk.StringVar()
    ttk.Entry(frame, textvariable=self.network_path, width=40).grid(row=2, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(frame, text="Network Username:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    self.network_user = tk.StringVar()
    ttk.Entry(frame, textvariable=self.network_user, width=40).grid(row=3, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(frame, text="Network Password:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    self.network_pass = tk.StringVar()
    ttk.Entry(frame, textvariable=self.network_pass, width=40, show="*").grid(row=4, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(frame, text="Drive Letter:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    self.network_drive = tk.StringVar(value="Z")
    ttk.Entry(frame, textvariable=self.network_drive, width=5).grid(row=5, column=1, sticky="w", padx=5, pady=5)

    # Date folder configuration frame
    date_frame = ttk.LabelFrame(frame, text="Date-based Folder Organization")
    date_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=10)

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
    ttk.Label(frame, text="Operation:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
    op_frame = ttk.Frame(frame)
    op_frame.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
    ttk.Radiobutton(op_frame, text="Copy", variable=self.operation_type, value="copy").pack(side=tk.LEFT)
    ttk.Radiobutton(op_frame, text="Move", variable=self.operation_type, value="move").pack(side=tk.LEFT, padx=10)

    # Initialize date widgets
    self.update_date_widgets()

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
    
    ttk.Button(control_frame, text="Create Windows Task", command=lambda:create_windows_task(self)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Delete Windows Task", command=lambda:delete_windows_task(self)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Run Once Now", command=lambda:run_once(self)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Preview Destination", command=lambda:preview_destination(self)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Save Config", command=lambda:save_config(self)).pack(side=tk.RIGHT, padx=5)
    
    # Status bar
    status_frame = ttk.Frame(self.root)
    status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

    self.status_var = tk.StringVar(value="Ready")
    status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
    status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

    self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", length=200, mode="determinate")
    self.progress_bar.pack(side=tk.RIGHT)
    
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
    
    ttk.Button(button_frame, text="Check Task Status", command=lambda:check_task_status(self)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Windows Tasks", command=lambda:view_windows_tasks(self)).pack(side=tk.LEFT, padx=5)
    
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
    ttk.Button(frame, text="Test Email", command=lambda:test_email(self)).grid(row=5, column=1, pady=10)
    
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
    
    ttk.Button(log_button_frame, text="Refresh Logs", command=lambda:refresh_logs(self)).pack(side=tk.LEFT, padx=5)
    ttk.Button(log_button_frame, text="Clear Old Logs (>30 days)", command=lambda:clear_old_logs(self)).pack(side=tk.LEFT, padx=5)
    ttk.Button(log_button_frame, text="Export Logs", command=lambda:export_logs(self)).pack(side=tk.LEFT, padx=5)
    
    # Load initial logs
    refresh_logs(self)