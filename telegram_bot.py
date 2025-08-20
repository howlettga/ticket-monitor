import requests
import os
import json
import subprocess

def load_chat_ids():
    """Load chat IDs from file, return as list"""
    try:
        with open('chat_ids.txt', 'r') as f:
            chat_ids = [line.strip() for line in f.readlines() if line.strip()]
            return chat_ids
    except FileNotFoundError:
        return []

def save_chat_ids(chat_ids):
    """Save chat IDs to file and commit to git"""
    try:
        # Write to file
        with open('chat_ids.txt', 'w') as f:
            for chat_id in chat_ids:
                f.write(f"{chat_id}\n")
        
        # Commit to git
        subprocess.run(['git', 'config', '--local', 'user.email', 'action@github.com'], check=True)
        subprocess.run(['git', 'config', '--local', 'user.name', 'GitHub Action'], check=True)
        subprocess.run(['git', 'add', 'chat_ids.txt'], check=True)
        
        # Only commit if there are changes
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
        if result.returncode != 0:  # There are changes to commit
            subprocess.run(['git', 'commit', '-m', 'Update registered chat IDs'], check=True)
            subprocess.run(['git', 'push'], check=True)
            print("Chat IDs updated and committed to repository")
        else:
            print("No changes to chat IDs")
            
    except subprocess.CalledProcessError as e:
        print(f"Failed to commit chat IDs: {e}")
    except Exception as e:
        print(f"Error saving chat IDs: {e}")

def check_telegram_registrations():
    """Check for new /register commands and manage subscriber list"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("No Telegram bot token configured")
        return
    
    try:
        # Get updates from Telegram
        telegram_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(telegram_url)
        
        if response.status_code != 200:
            print(f"Failed to get Telegram updates: {response.status_code}")
            return
            
        data = response.json()
        
        if not data.get('ok'):
            print("Telegram API error")
            return
            
        # Process each message
        for update in data.get('result', []):
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '').strip()
            first_name = message.get('from', {}).get('first_name', 'User')
            
            if chat_id and text:
                if text.lower() == '/register':
                    handle_registration(bot_token, chat_id, first_name)
                elif text.lower() == '/unregister':
                    handle_unregistration(bot_token, chat_id, first_name)
                elif text.lower() == '/status':
                    handle_status_check(bot_token, chat_id)
        
        # Mark all updates as read by getting them with offset
        if data.get('result'):
            last_update_id = data['result'][-1]['update_id']
            mark_read_url = f"https://api.telegram.org/bot{bot_token}/getUpdates?offset={last_update_id + 1}"
            requests.get(mark_read_url)
            
    except Exception as e:
        print(f"Error checking Telegram registrations: {e}")

def handle_registration(bot_token, chat_id, first_name):
    """Handle /register command and automatically add to chat_ids.txt"""
    
    # Load current chat IDs from file
    chat_id_list = load_chat_ids()
    chat_id_str = str(chat_id)
    
    if chat_id_str in chat_id_list:
        # Already registered
        message = f"Hi {first_name}! 👋\n\nYou're already registered for festival pass notifications. You'll get alerted when resale tickets become available!"
    else:
        # New registration - add to list and save
        chat_id_list.append(chat_id_str)
        save_chat_ids(chat_id_list)
        message = f"Hi {first_name}! 👋\n\nYou've been successfully registered for festival pass notifications! 🎟️\n\nYou'll automatically get alerted when resale tickets become available. No further action needed!"
    
    send_telegram_message(bot_token, chat_id, message)

def handle_unregistration(bot_token, chat_id, first_name):
    """Handle /unregister command and automatically remove from chat_ids.txt"""
    
    # Load current chat IDs from file
    chat_id_list = load_chat_ids()
    chat_id_str = str(chat_id)
    
    if chat_id_str in chat_id_list:
        # Remove from list and save
        chat_id_list.remove(chat_id_str)
        save_chat_ids(chat_id_list)
        message = f"Hi {first_name}! 👋\n\nYou've been successfully unregistered from festival pass notifications.\n\nYou won't receive any more alerts. Send /register if you want to sign up again!"
    else:
        message = f"Hi {first_name}! 👋\n\nYou're not currently registered for notifications.\n\nSend /register to sign up for festival pass alerts!"
    
    send_telegram_message(bot_token, chat_id, message)

def handle_status_check(bot_token, chat_id):
    """Handle /status command"""
    chat_id_list = load_chat_ids()
    
    if str(chat_id) in chat_id_list:
        message = "✅ You are registered for notifications!\n\nCommands:\n/register - Register for notifications\n/unregister - Unregister\n/status - Check registration status"
    else:
        message = "❌ You are not registered for notifications.\n\nSend /register to sign up!\n\nCommands:\n/register - Register for notifications\n/unregister - Unregister\n/status - Check registration status"
    
    send_telegram_message(bot_token, chat_id, message)

def send_telegram_message(bot_token, chat_id, message):
    """Send a message to a specific chat ID"""
    try:
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(telegram_url, json=payload)
        if response.status_code == 200:
            print(f"Response sent to chat ID {chat_id}")
        else:
            print(f"Failed to send response to {chat_id}: {response.text}")
            
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")

def send_telegram_notification(event_url):
    """Send Telegram notification to all registered chat IDs when resale tickets are found"""
    
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("Telegram bot token not configured")
        return
    
    # Load chat IDs from file
    chat_id_list = load_chat_ids()
    
    if not chat_id_list:
        print("No registered chat IDs found")
        return
    
    message_text = f"🎟️ *FESTIVAL PASSES RESALE AVAILABLE!*\n\nCheck now: {event_url}\n\nHurry - they go fast!"
    
    try:
        # Send message to each registered chat ID
        for chat_id in chat_id_list:
            if chat_id:  # Skip empty strings
                try:
                    send_telegram_message(bot_token, chat_id, message_text)
                        
                except Exception as e:
                    print(f"Failed to send Telegram message to {chat_id}: {e}")
        
    except Exception as e:
        print(f"Failed to send Telegram messages: {e}")