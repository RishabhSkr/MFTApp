import tkinter as tk 
import os
import argparse
import sys
from config.config import load_config_dict,on_closing,map_network_drive, unmap_network_drive,load_config
from database.db import init_database
from gui.mainWindow import create_widgets, create_file_ops_tab, create_scheduler_tab, create_email_tab, create_logs_tab
from utils.utils import update_date_widgets, update_preview,get_date_folder_name,browse_source, browse_destination, view_windows_tasks
from scheduler.task_scheduler import create_windows_task, delete_windows_task, check_task_status
import types
from fileOperation.fileOperations import run_once, perform_file_operation

class FileSchedulerApp:
    def __init__(self, root=None, config_file=None):
        self.db_path = r"C:\\Users\\Rishabh.Sonkar\\Desktop\\FileCopier\\database\\file_scheduler_log.db"  # Use absolute path for reliability
        # define wrapper
        self.on_closing = lambda: on_closing(self)
         # Set script_dir at the very top
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        # Support for command-line execution
        self.gui_mode = root is not None
        self.config_file = config_file or 'file_scheduler_config.json'
        self.perform_file_operation = types.MethodType(perform_file_operation, self)        
        
        # Bind perform_file_operation and run_once in all modes
        self.perform_file_operation = types.MethodType(perform_file_operation, self)
        self.get_date_folder_name = types.MethodType(get_date_folder_name, self)
        self.run_once = types.MethodType(run_once, self)
        
        # Initialize databaseload_config
        init_database(self)
        
        # Configuration variables
        if self.gui_mode:
            self.root = root
            self.root.title("File Scheduler Application - Windows Task Scheduler Integration")
            self.root.geometry("900x700")

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
            
             # Status and progress
            self.status_var = tk.StringVar(value="Ready")
            self.progress_bar = None # Will be created in create_widgets
            # Task name for Windows Task Scheduler
            self.task_name = tk.StringVar(value="FileScheduler_Task")
            # Bind methods from other modules to the instance
            self.create_file_ops_tab = types.MethodType(create_file_ops_tab, self)
            self.create_scheduler_tab = types.MethodType(create_scheduler_tab, self)
            self.create_email_tab = types.MethodType(create_email_tab, self)
            self.create_logs_tab = types.MethodType(create_logs_tab, self)
            self.update_date_widgets = types.MethodType(update_date_widgets, self)
            self.update_preview = types.MethodType(update_preview, self)
            self.browse_source = types.MethodType(browse_source, self)
            self.browse_destination = types.MethodType(browse_destination, self)
            self.view_windows_tasks = types.MethodType(view_windows_tasks, self)
            self.check_task_status = types.MethodType(check_task_status, self)
            self.create_windows_task = types.MethodType(create_windows_task, self)
            self.delete_windows_task = types.MethodType(delete_windows_task, self)
            self.map_network_drive = map_network_drive
            self.unmap_network_drive = unmap_network_drive
            self.run_once = types.MethodType(run_once, self)
            # Create widgets and load config
            create_widgets(self)
            load_config(self)
        else:
            # Batch mode: Initialize attributes as normal strings/bools, not StringVar
            self.source_path = ""
            self.destination_path = ""
            self.operation_type = "copy"
            self.schedule_time = "00:00"
            self.schedule_frequency = "daily"
            self.use_date_folders = True
            self.date_format = "YYYY-MM-DD"
            self.date_folder_type = "current"
            self.custom_date = ""
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = "587"
            self.sender_email = ""
            self.sender_password = ""
            self.recipient_email = ""
            self.use_tls = True
            self.status_var = ""
            self.progress_bar = None
            self.task_name = "FileScheduler_Task"

            # For command-line mode, load from config
            load_config_dict(self)
        
        # Get script directory for absolute paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    
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
        drive_letter = 'Z' # drive letter
        network_path = app.config.get('network_path', '') # network share path
        username = app.config.get('network_user', '') 
        password = app.config.get('network_pass', '') 
        # print(f"Mapping network drive {drive_letter}: to {network_path} with {username}  {password}")
          # Mount the network drive
        if not map_network_drive(drive_letter, network_path, username, password):
            print("ERROR: Failed to map network drive Z:")
            sys.exit(1)

        try:
            success = app.perform_file_operation()
            app.on_closing()
        finally:
            # Always unmount the drive
            unmap_network_drive(drive_letter)

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
