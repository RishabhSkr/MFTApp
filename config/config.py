
import os
import json
from datetime import datetime

try:
    from tkinter import messagebox
except ImportError:
    messagebox = None  # In batch mode, tkinter may not be available
    
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
