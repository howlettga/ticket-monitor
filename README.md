# Tixr Resale Ticket Monitor

Automatically monitors a Tixr event page for resale ticket availability and sends email notifications.

## Setup Instructions

### 1. Create GitHub Repository
1. Go to GitHub.com and create a new repository
2. Make it private (recommended) or public
3. Upload these files to your repository

### 2. Configure the Script
1. Edit `monitor.py`
2. Replace `YOUR_TIXR_EVENT_URL_HERE` with your actual Tixr event URL

### 3. Set up Email Notifications (GitHub Secrets)
1. Go to your repository Settings → Secrets and Variables → Actions
2. Add these secrets:

**SENDER_EMAIL**: Your Gmail address (e.g., yourname@gmail.com)
**SENDER_PASSWORD**: Your Gmail App Password (see instructions below)
**RECIPIENT_EMAIL**: Where to send notifications (can be same as sender)

### 4. Gmail App Password Setup
1. Go to your Google Account settings
2. Turn on 2-factor authentication if not already enabled
3. Go to Security → App Passwords
4. Generate an app password for "Mail"
5. Use this 16-character password as your SENDER_PASSWORD secret

### 5. Test the Setup
1. Go to Actions tab in your GitHub repository
2. Click "Tixr Resale Monitor" workflow
3. Click "Run workflow" to test manually
4. Check the logs to see if it's working

### 6. Monitor Schedule
- Runs automatically every 30 minutes
- You can change the schedule in `.github/workflows/monitor.yml`
- Modify the cron expression: `*/30 * * * *` (every 30 min)

### File Structure
```
your-repo/
├── monitor.py                    # Main monitoring script
├── requirements.txt              # Python dependencies
├── .github/
│   └── workflows/
│       └── monitor.yml           # GitHub Actions workflow
└── README.md                     # This file
```

### Customization
- Change check frequency by modifying the cron schedule
- Add SMS notifications using services like Twilio
- Modify the CSS selector if needed
- Add Discord/Slack webhooks instead of email

### Troubleshooting
- Check Actions tab for error logs
- Ensure your Tixr URL is correct
- Verify Gmail app password is set correctly
- Make sure secrets are configured properly
