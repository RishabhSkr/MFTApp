from tkinter import filedialog, messagebox
from datetime import datetime
import os
import subprocess

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

def view_windows_tasks(self):
    """Open Windows Task Scheduler"""
    try:
        subprocess.run("taskschd.msc", shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Task Scheduler:\n{str(e)}")