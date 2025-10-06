import sqlite3
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox

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
    
    
def log_operation(self, status, message, files_processed, details, date_folder,execution_mode="GUI", conn=None):
    try:
        connection = conn if conn is not None else self.conn
        if not connection:
            self.init_database()
            connection = self.conn

        cursor = connection.cursor()

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
        connection.commit()

        print(f"[{execution_mode}] Log entry created: {status} - {message}")

        # Update status bar if in GUI mode
        if self.gui_mode:
            self.status_var.set(f"{status}: {message}")

        # Refresh logs if visible
        if self.gui_mode:
            try:
                from .db import refresh_logs
                self.root.after(0, lambda: refresh_logs(self))
            except:
                pass

    except Exception as e:
        print(f"[{execution_mode}] Failed to log operation: {str(e)}")
        # Don't raise the exception to avoid breaking the main operation




def refresh_logs(self):
    """Refresh the logs tree view"""
    if not self.gui_mode:
        return

    # Clear existing items
    for item in self.logs_tree.get_children():
        self.logs_tree.delete(item)

    try:
        # Open a new local DB connection (in the main thread)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, operation_type, status, files_processed, date_folder, 
                       execution_mode, source_path, final_destination
                FROM file_operations
                ORDER BY timestamp DESC
                LIMIT 200
            """)

            for row in cursor.fetchall():
                try:
                    timestamp = datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp = row[0]

                date_folder = row[4] if row[4] else "None"
                execution_mode = row[5] if row[5] else "GUI"
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
            refresh_logs(self)
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