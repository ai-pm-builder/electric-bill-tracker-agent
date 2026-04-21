# This PowerShell script creates a scheduled task to run the UPPCL Daily Tracker
# every morning at 9:00 AM.

$CurrentPath = $PSScriptRoot
$PythonPath = "$CurrentPath\.venv\Scripts\python.exe"
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "main.py" -WorkingDirectory $CurrentPath
$Trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

$TaskName = "UPPCL_Daily_Bill_Tracker"
$Description = "Runs the UPPCL Smart Meter daily bill scraper at 9:00 AM"

Register-ScheduledTask -TaskName $TaskName -Description $Description -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings

Write-Host "Scheduled task '$TaskName' has been created successfully!"
Write-Host "Please edit the action in Task Scheduler if you are using a virtual environment (e.g., point to the venv python.exe)."
