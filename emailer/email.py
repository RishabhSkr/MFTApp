from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from tkinter import messagebox

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