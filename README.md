# veracode-pdf-reports
This script will pull the latest PDF reports from Veracode for recent Static and Dynamic scans since the previous day.  Running this within a cron task will allow you to keep your Veracode daily PDF reports updated with the latest available reports.

<b>Prerequisites:</b>

  • Python

  • Veracode Account

  • API Credentials file correctly installed


<b>Usage:</b>

Summary Report

<code>python getreports.py</code>

Detailed Report

<code>python getreports.py --detailed</code>

