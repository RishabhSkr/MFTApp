# File Scheduler - Windows Task Scheduler Integration

## PERSISTENT SCHEDULING SOLUTION ✅

This enhanced version integrates with **Windows Task Scheduler** to provide persistent scheduling that continues running even after closing the application. No more worrying about keeping the application running 24/7!

## Key Features

### 🔄 **Persistent Scheduling**
- Tasks continue running after application closes
- Uses Windows native Task Scheduler service
- Automatic system startup and recovery
- Background execution with full functionality

### 📊 **Enhanced Logging**  
- Fixed database logging with improved error handling
- Execution mode tracking (GUI vs BATCH)
- WAL mode for better database concurrency
- Comprehensive error logging and recovery

### 📧 **Robust Email Notifications**
- Notifications work in both GUI and scheduled modes
- Detailed execution context in emails
- Error handling for email failures

### 🗂️ **Date-Based Organization**
- All date folder functionality preserved
- Multiple format support maintained
- Real-time preview capabilities

## How Windows Task Scheduler Integration Works

### Traditional Python Scheduling (OLD)
```
Python App Running → Schedule Library → File Operations
       ↓
App Closes → Scheduling STOPS ❌
```

### Windows Task Scheduler Integration (NEW)
```
Python App → Creates Windows Task → Windows Task Scheduler
       ↓                                     ↓
App Closes                          Continues Running ✅
                                          ↓
                                 Executes Python Script
                                          ↓
                                   File Operations + Logging
```

## Installation & Setup

### 1. **Install Dependencies**
```bash
pip install schedule  # Still used for GUI preview
```

### 2. **Run Application**
```bash
python file_scheduler_persistent.py
```

### 3. **Configure Your Settings**
- Set source and destination paths
- Configure date folder options
- Set email notifications
- Choose schedule frequency and time

### 4. **Create Windows Task**
- Click **"Create Windows Task"** button
- Task will be registered with Windows Task Scheduler
- View confirmation and task details

### 5. **Close Application**
- Your scheduled task continues running!
- Check Windows Task Scheduler (taskschd.msc) anytime

## Windows Task Scheduler Tab

The new **"Windows Scheduler"** tab provides:

### Task Configuration
- **Task Name**: Unique identifier for your scheduled task
- **Schedule Time**: When to run (HH:MM format)
- **Frequency**: Daily, Weekly, Monthly, or Once

### Task Management
- **Create Windows Task**: Register new task with Windows
- **Delete Windows Task**: Remove task from Windows scheduler
- **Check Task Status**: View current task status and next run time
- **View Windows Tasks**: Open Windows Task Scheduler GUI

### Status Monitoring
- Real-time task status display
- Next execution time
- Task existence verification

## Command-Line Operation

The application supports batch execution for scheduled tasks:

### Automatic Batch Mode
When Windows Task Scheduler runs your task, it executes:
```bash
python file_scheduler_persistent.py --batch --config "config_path"
```

### Manual Testing
You can test batch mode manually:
```bash
python file_scheduler_persistent.py --batch
```

## Enhanced Database Logging

### Fixed Issues
- ✅ **Connection Handling**: Improved SQLite connection management
- ✅ **WAL Mode**: Write-Ahead Logging for better concurrency
- ✅ **Error Recovery**: Robust error handling and logging
- ✅ **Transaction Safety**: Proper commit/rollback handling

### New Database Schema
```sql
CREATE TABLE file_operations (
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
    execution_mode TEXT DEFAULT 'GUI'  -- NEW: Track GUI vs BATCH
);
```

### Enhanced Log Management
- **Real-time Updates**: Logs update automatically during operations
- **Export Functionality**: Export logs to CSV format
- **Cleanup Tools**: Remove old logs (30+ days)
- **Execution Mode Tracking**: See which operations were GUI vs scheduled

## Email Notifications

### Enhanced Email Features
- **Execution Context**: Emails indicate GUI vs BATCH execution
- **Detailed Information**: Complete operation details and timing
- **Error Recovery**: Continue operation even if email fails
- **Configuration Preservation**: All email settings work in batch mode

### Sample Success Email (Batch Mode)
```
Subject: File Scheduler - Copy Operation Successful (BATCH)

File copy operation completed successfully!

Execution Mode: BATCH
Details:
- Source: C:\Source\Documents
- Base Destination: C:\Backup
- Final Destination: C:\Backup\2025-09-22
- Operation: Copy
- Files processed: 127
- Duration: 3.45 seconds
- Date Folder: 2025-09-22
- Time: 2025-09-22 14:30:15

This is an automated message from File Scheduler Application.
```

## Task Scheduler Integration Details

### Windows Task Creation
The application uses `schtasks.exe` commands to:
```bash
# Daily task example
schtasks /create /tn "FileScheduler_Task" /tr "python script.py --batch" /sc daily /st 14:30 /f

# Weekly task example  
schtasks /create /tn "FileScheduler_Task" /tr "python script.py --batch" /sc weekly /st 09:00 /f
```

### Task Management Commands
```bash
# Check task status
schtasks /query /tn "FileScheduler_Task" /fo list

# Delete task
schtasks /delete /tn "FileScheduler_Task" /f

# Run task immediately
schtasks /run /tn "FileScheduler_Task"
```

## Permissions and Security

### Required Permissions
- **Standard User**: Can create tasks for current user
- **Administrator**: Can create system-wide tasks
- **Network Access**: For UNC path operations
- **Email Access**: For SMTP notifications

### Security Considerations
- **Credential Storage**: Email passwords stored in configuration files
- **Task Security**: Tasks run under current user context
- **File Permissions**: Respect existing file system security
- **Network Authentication**: Uses Windows integrated authentication

## Troubleshooting

### Common Issues and Solutions

#### 1. **Task Creation Fails**
```
Error: Access denied creating task
Solution: Run as Administrator or check user permissions
```

#### 2. **Task Runs But Files Not Copied**
```
Issue: Task shows success but no files copied
Solution: Check file paths and permissions in batch mode
```

#### 3. **Database Logging Not Working**
```
Issue: No log entries created
Solution: Check file permissions and database path
```

#### 4. **Email Notifications Not Sent**
```
Issue: Operations succeed but no emails
Solution: Verify SMTP settings and test email configuration
```

### Diagnostic Commands

#### Check Task Status
```bash
schtasks /query /tn "FileScheduler_Task"
```

#### Test Batch Execution
```bash
python file_scheduler_persistent.py --batch --config "path\to\config.json"
```

#### Verify Configuration
```bash
# Check if config file exists and is readable
type file_scheduler_config.json
```

## Migration from Previous Version

### Automatic Migration
- ✅ **Configuration**: Existing configs load automatically
- ✅ **Database**: Schema updates applied automatically  
- ✅ **Settings**: All previous settings preserved

### Recommended Steps
1. **Backup Data**: Save existing config and database files
2. **Test Configuration**: Verify all settings in new version
3. **Create Windows Task**: Set up persistent scheduling
4. **Validate Operation**: Test batch execution manually
5. **Monitor Results**: Check logs and email notifications

## Advanced Configuration

### Custom Task Names
Use descriptive task names for multiple schedules:
```
FileScheduler_Documents_Daily
FileScheduler_Photos_Weekly
FileScheduler_Backup_Monthly
```

### Network Drive Considerations
- Ensure network drives are mapped consistently
- Use UNC paths for better reliability: `\\server\share\folder`
- Test network connectivity in batch mode

### Multiple Configurations
Create separate config files for different tasks:
```bash
python file_scheduler_persistent.py --batch --config "daily_backup.json"
python file_scheduler_persistent.py --batch --config "weekly_archive.json"
```

## Performance Optimization

### Database Performance
- WAL mode enables concurrent access
- Regular cleanup of old logs recommended
- Database file size monitoring

### File Operations
- Progress logging every 10 files
- Efficient directory traversal
- Proper error handling for large file sets

### Memory Usage
- Minimal memory footprint in batch mode
- Efficient file processing algorithms
- Clean resource disposal

## Monitoring and Maintenance

### Regular Checks
- **Task Status**: Use "Check Task Status" button
- **Log Review**: Monitor operation logs regularly
- **Email Testing**: Periodic email configuration tests
- **Disk Space**: Monitor destination drive space

### Maintenance Tasks
- **Log Cleanup**: Clear old logs monthly
- **Config Backup**: Save configuration files
- **Task Validation**: Verify Windows tasks periodically
- **System Updates**: Test after Windows updates

## Best Practices

### Scheduling
- **Avoid Peak Hours**: Schedule during low-usage times
- **Test Thoroughly**: Always test manually before scheduling
- **Monitor Initially**: Watch first few scheduled runs closely
- **Backup Configuration**: Save settings before changes

### File Management
- **Path Length**: Keep paths under Windows limits
- **Permissions**: Verify access to all paths
- **Network Stability**: Ensure reliable network for UNC paths
- **Disk Space**: Monitor available space regularly

### Error Recovery
- **Email Alerts**: Configure email for failure notifications
- **Log Monitoring**: Review logs for recurring issues
- **Retry Logic**: Built-in error handling and recovery
- **Manual Intervention**: Be prepared for manual resolution

## Conclusion

The Windows Task Scheduler integration transforms the File Scheduler from a session-dependent tool into a robust, enterprise-ready automation solution. With persistent scheduling, enhanced logging, and comprehensive error handling, your file operations will continue reliably regardless of user sessions or application state.

**Ready for production use with full Windows integration!**
