
import subprocess
import sys
import os
from datetime import datetime, timedelta
from tkinter import messagebox
from config.config import save_config
def create_windows_task(app):
    """Create a Windows Task Scheduler task"""
    try:
        # Validate configuration
        if not all([app.source_path.get(), app.destination_path.get(), app.task_name.get()]):
            messagebox.showerror("Error", "Please configure source path, destination path, and task name.")
            return
        
        # Save current configuration
        save_config(app)
        
        # Get Python executable path
        python_exe = sys.executable
        script_path = os.path.abspath(sys.argv[0]) # Use sys.argv[0] for the entry script
        config_path = os.path.join(app.script_dir, app.config_file)
        # log_file_path = os.path.join(app.script_dir, "task_run.log")
        
        # The long command to execute WITHOUT output redirection
        long_task_command = f'"{python_exe}" "{script_path}" --batch --config "{config_path}"'
        
        # Create a helper batch file to overcome the /tr length limit
        batch_file_path = os.path.join(app.script_dir, "run_task.bat")
        with open(batch_file_path, "w") as f:
            f.write("@echo off\n")
            # Change to the script's directory to ensure all paths are resolved correctly
            f.write(f'cd /d "{app.script_dir}"\n')
            f.write(long_task_command + "\n")

        # The command for schtasks is now just the path to the batch file
        task_command = f'"{batch_file_path}"'
       
        # Build schtasks command
        task_name = app.task_name.get()
        schedule_time = app.schedule_time.get()
        frequency = app.schedule_frequency.get().upper()
        
        # Delete existing task if it exists
        try:
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', 
                         shell=True, capture_output=True, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
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
        result = subprocess.run(schtasks_cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            app.status_var.set("Windows task created successfully")
            messagebox.showinfo("Success", 
                f"Windows Task Scheduler task '{task_name}' created successfully!\n\n"
                f"Schedule: {frequency} at {schedule_time}\n"
                f"The task will continue running even after closing this application.\n\n"
                f"View in Task Scheduler: taskschd.msc")
            app.check_task_status()
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            print(f"Error creating task: {error_msg}")
            messagebox.showerror("Error", f"Failed to create Windows task:\n{error_msg}")
            
    except Exception as e:
        print(f"Exception creating task: {str(e)}")
        messagebox.showerror("Error", f"Failed to create Windows task:\n{str(e)}")

def delete_windows_task(app):
    """Delete the Windows Task Scheduler task"""
    try:
        task_name = app.task_name.get()
        if not task_name:
            messagebox.showerror("Error", "Please specify a task name.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
            f"Are you sure you want to delete the Windows task '{task_name}'?"):
            return
        
        # Delete the task
        result = subprocess.run(f'schtasks /delete /tn "{task_name}" /f', 
                              shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            app.status_var.set("Windows task deleted successfully")
            messagebox.showinfo("Success", f"Windows task '{task_name}' deleted successfully!")
            app.check_task_status()
        else:
            error_msg = result.stderr or result.stdout or "Task not found"
            messagebox.showinfo("Info", f"Task deletion result:\n{error_msg}")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete Windows task:\n{str(e)}")

def check_task_status(app):
    """Check if Windows task exists and is scheduled"""
    if not app.gui_mode:
        return
        
    try:
        task_name = app.task_name.get()
        if not task_name:
            app.task_status_var.set("No task name specified")
            return
        
        # Query the specific task
        result = subprocess.run(f'schtasks /query /tn "{task_name}" /fo list', 
                              shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            # Parse the output to get task info
            lines = result.stdout.split('\n')
            status = "Unknown"
            next_run = "Unknown"
            
            for line in lines:
                if "Status:" in line:
                    status = line.split(':')[1].strip()
                elif "Next Run Time:" in line:
                    next_run = line.split(':')[1].strip()
            
            app.task_status_var.set(f"Status: {status}, Next Run: {next_run}")
        else:
            app.task_status_var.set("Task not found or not scheduled")
            
    except Exception as e:
        app.task_status_var.set(f"Error checking status: {str(e)}")
        

