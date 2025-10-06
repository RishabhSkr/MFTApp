import sqlite3
import os
import shutil
from datetime import datetime
import threading
import tkinter as tk
from database.db import log_operation,refresh_logs
from emailer.email import send_notification_email
from utils.utils import get_date_folder_name


def perform_file_operation(self):
    try:
        conn = sqlite3.connect(self.db_path)
        print("DB connection opened in thread")
    except Exception as e:
        print(f"Failed to open DB connection: {e}")
        return False

    execution_mode = "GUI" if self.gui_mode else "BATCH"

    try:
        if self.gui_mode:
            source = self.source_path.get()
            base_destination = self.destination_path.get()
            network_path = self.network_path.get()
            network_user = self.network_user.get()
            network_pass = self.network_pass.get()
            network_drive = self.network_drive.get()

            unmapped = False
            if network_path and network_user and network_pass and network_drive:
                mapped = self.map_network_drive(network_drive, network_path, network_user, network_pass)
                if not mapped:
                    self.root.after(0, lambda: tk.messagebox.showerror("Error", "Failed to map network drive"))
                    return False
                unmapped = True
                operation = self.operation_type.get()
        else:
            source = self.config.get('source_path', '')
            base_destination = self.config.get('destination_path', '')
            operation = self.operation_type
            
        print(f"[{execution_mode}] Starting file operation: {operation}")
        print(f"[{execution_mode}] Source: {source}")
        print(f"[{execution_mode}] Base destination: {base_destination}")

        if not source or not base_destination:
            error_msg = "Source or destination path not specified"
            print(f"[{execution_mode}] Error: {error_msg}")

            log_operation(self, "ERROR", error_msg, 0, "Missing paths", "", execution_mode, conn=conn)
            return False

        operation_date = datetime.now()
        date_folder = self.get_date_folder_name(operation_date)

        if date_folder:
            final_destination = os.path.join(base_destination, date_folder)
            print(f"[{execution_mode}] Date folder: {date_folder}")
        else:
            final_destination = base_destination
            print(f"[{execution_mode}] No date folder")

        print(f"[{execution_mode}] Final destination: {final_destination}")

        os.makedirs(final_destination, exist_ok=True)
        print(f"[{execution_mode}] Created destination directory")

        files_processed = 0
        start_time = datetime.now()

        if os.path.isfile(source):
            files_to_process = [source]
        else:
            files_to_process = []
            for root, _, files in os.walk(source):
                for file in files:
                    files_to_process.append(os.path.join(root, file))
        print(f"[{execution_mode}] Found {len(files_to_process)} files to process")

        for file_path in files_to_process:
            try:
                if os.path.isfile(source):
                    dest_file = os.path.join(final_destination, os.path.basename(file_path))
                else:
                    rel_path = os.path.relpath(file_path, source)
                    dest_file = os.path.join(final_destination, rel_path)
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                if operation == "copy":
                    shutil.copy2(file_path, dest_file)
                else:
                    shutil.move(file_path, dest_file)

                files_processed += 1

                if files_processed % 10 == 0:
                    print(f"[{execution_mode}] Processed {files_processed} files...")

            except Exception as e:
                error_msg = f"Failed to {operation} {file_path}: {str(e)}"
                print(f"[{execution_mode}] File error: {error_msg}")

                log_operation(self, "ERROR", error_msg, files_processed, str(e), date_folder, execution_mode, conn=conn)
                return False

        if self.gui_mode and unmapped:
            self.unmap_network_drive(network_drive)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        success_msg = f"{operation.title()} operation completed"
        if date_folder:
            success_msg += f" to date folder '{date_folder}'"

        details = f"Processed {files_processed} files in {duration:.2f} seconds"
        print(f"[{execution_mode}] Success: {success_msg}")
        print(f"[{execution_mode}] {details}")

        log_operation(self, "SUCCESS", success_msg, files_processed, details, date_folder, execution_mode, conn=conn)

        send_notification_email(self, "SUCCESS", files_processed, duration, final_destination, date_folder, execution_mode)

        if self.gui_mode:
            self.root.after(0, lambda: self.status_var.set(f"Operation completed: {files_processed} files processed"))
            self.root.after(0, lambda: refresh_logs(self))

        return True

    except Exception as e:
        error_msg = f"Operation failed: {str(e)}"
        print(f"[{execution_mode}] Exception: {error_msg}")

        log_operation(self, "ERROR", error_msg, 0, str(e), date_folder if 'date_folder' in locals() else "", execution_mode, conn=conn)

        send_notification_email(self, "ERROR", 0, 0, "", "", execution_mode, str(e))

        if self.gui_mode:
            self.root.after(0, lambda: self.status_var.set(f"Error: {error_msg}"))

        return False

    finally:
        if conn:
            conn.close()
            print("DB connection closed in thread")


def run_once(self):
    if self.gui_mode:
        self.status_var.set("Running operation...")
        threading.Thread(target=lambda: perform_file_operation(self), daemon=True).start()
    else:
        perform_file_operation(self)
