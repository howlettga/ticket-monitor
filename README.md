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

### 5. User Registration (Automatic!)
Users can now register themselves:
1. Find your bot in Telegram (search for the username you created)
2. Send `/register` to the bot
3. Bot automatically adds them to notifications - no manual steps needed!

### 6. Test the Setup
1. Register yourself by sending `/register` to your bot
2. Go to Actions tab in your GitHub repository
3. Click "Tixr Resale Monitor" workflow
4. Click "Run workflow" to test manually
5. Check the logs to see if it's working

### 6. Monitor Schedule
- Runs automatically every 15 minutes
- You can change the schedule in `.github/workflows/monitor.yml`
- Modify the cron expression: `*/15 * * * *` (every 15 min)

### File Structure
```
your-repo/
├── monitor.py                    # Main monitoring script
├── telegram_bot.py              # Telegram bot functionality
├── requirements.txt              # Python dependencies
├── .github/
│   └── workflows/
│       └── monitor.yml           # GitHub Actions workflow
└── README.md                     # This file
```

## Bot Commands
- **`/register`** - Automatically register for notifications
- **`/unregister`** - Remove yourself from notifications  
- **`/status`** - Check if you're registered

## How Registration Works
- Users send `/register` to your bot
- Bot automatically adds their chat ID to `chat_ids.txt`  
- File gets committed to your repository
- Next monitoring run picks up new registrations
- No manual intervention needed!

### Gmail App Password Setup (Optional)
If you want email backup notifications:
1. Go to your Google Account settings
2. Turn on 2-factor authentication if not already enabled
3. Go to Security → App Passwords
4. Generate an app password for "Mail"
5. Use this 16-character password as your SENDER_PASSWORD secret

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