import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from twilio.rest import Client

def check_tixr_resale():
    # Replace with your actual Tixr event URL
    url = "https://www.tixr.com/groups/100x/events/valley-of-the-seven-stars-cosmic-campout-135703"
    
    try:
        # Make request to the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the Festival Passes section and check for resale
        festival_passes_h2 = soup.find("h2", string="Festival Passes")
        if festival_passes_h2:
            # Get the next sibling div, then find the first li with state="RESALE"
            next_div = festival_passes_h2.find_next_sibling("div")
            if next_div:
                element = next_div.select_one("ul li:first-child [state='RESALE']")
            else:
                element = None
        else:
            element = None
        
        if element:
            print("🎉 RESALE TICKETS AVAILABLE!")
            send_sms_notification(url)
            send_notification(url)  # Also send email as backup
            return True
        else:
            print("No resale tickets yet - still sold out")
            return False
            
    except Exception as e:
        print(f"Error checking page: {e}")
        return False

def send_sms_notification(event_url):
    """Send SMS notification to multiple phones when resale tickets are found"""
    
    # Get Twilio credentials from environment variables (set in GitHub secrets)
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')  # Your Twilio phone number
    recipient_phones = os.getenv('RECIPIENT_PHONES')  # Comma-separated phone numbers
    
    if not all([account_sid, auth_token, twilio_phone, recipient_phones]):
        print("Twilio credentials not configured")
        return
    
    # Split the comma-separated phone numbers and clean them
    phone_numbers = [phone.strip() for phone in recipient_phones.split(',')]
    
    try:
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        message_body = f"🎟️ FESTIVAL PASSES RESALE AVAILABLE!\n\nCheck now: {event_url}\n\nHurry - they go fast!"
        
        # Send SMS to each phone number
        for phone in phone_numbers:
            if phone:  # Skip empty strings
                try:
                    message = client.messages.create(
                        body=message_body,
                        from_=twilio_phone,
                        to=phone
                    )
                    print(f"SMS sent to {phone}! Message SID: {message.sid}")
                except Exception as e:
                    print(f"Failed to send SMS to {phone}: {e}")
        
    except Exception as e:
        print(f"Failed to send SMS: {e}")

def send_notification(event_url):
    """Send email notification when resale tickets are found"""
    
    # Get email credentials from environment variables (set in GitHub secrets)
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')  # Use app password for Gmail
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("Email credentials not configured")
        return
    
    # Create message
    message = MimeMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "🎟️ Tixr Resale Tickets Available!"
    
    body = f"""
    Great news! Resale tickets are now available for your event.
    
    Check them out here: {event_url}
    
    Hurry - they might go fast!
    """
    
    message.attach(MimeText(body, "plain"))
    
    try:
        # Send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        print("Notification email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    check_tixr_resale()
