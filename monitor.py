# Method 4: Try API-first approach as standalone
    try:
        print("Trying standalone API approach...")
        session.close()
        session = requests.Session()
        
        time.sleep(random.uniform(3, 7))
        
        # Make API call first
        api_url = "https://www.tixr.com/api/events?eventName=seven%20stars&page=1&pageSize=20"
        api_headers = get_random_headers()
        api_headers['Accept'] = 'application/json, text/plain, */*'
        api_headers['Referer'] = 'https://www.tixr.com/'
        
        api_response = session.get(api_url, headers=api_headers, timeout=30)
        print(f"Standalone API status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            # Try to get ticket info directly from API if possible
            try:
                api_data = api_response.json()
                print(f"API returned {len(api_data.get('events', []))} events")
                # You could potentially check for resale info in the API response here
            except:
                pass
                
            # Now try event page
            time.sleep(random.uniform(1, 3))
            event_headers = get_random_headers()
            event_headers['Referer'] = 'https://www.tixr.com/'
            
            response = session.get(url, headers=event_headers, timeout=30)
            if response.status_code == 200:
                print("✅ Success with standalone API approach")
                return parse_response(response)
                
    except Exception as e:
        print(f"Standalone API approach failed: {e}")
    try:
        print("Trying alternative detection method...")
        
        # Sometimes the page loads but tickets info is loaded via JavaScript
        # Try to detect this and look for different indicators
        
        session.close()
        session = requests.Session()
        time.sleep(random.uniform(5, 10))
        
        headers = get_random_headers()
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        headers['Referer'] = 'https://www.google.com/search?q=tixr+100x+valley+seven+stars'
        
        response = session.get(url, headers=headers, timeout=30)
        
        print(f"Final attempt status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success with Google search referer")
            return parse_response(response)
        elif response.status_code == 403:
            print("Still getting 403 - may need to try different times or approach")
        else:
            print(f"Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"Final attempt failed: {e}")
    
    # Method 5: Check if we can get any useful info even from blocked responses
    try:
        print("Checking if any partial data is available...")
        headers = {'User-Agent': 'curl/7.68.0'}  # Try with curl user agent
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 403:
            # Sometimes 403 pages still contain some info
            if len(response.content) > 1000:  # If we got substantial content
                print("Got substantial content even with 403 - checking for clues...")
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"403 page title: {title.get_text().strip()}")
                    
    except Exception as e:
        print(f"Partial data check failed: {e}")import requests
from bs4 import BeautifulSoup
import os
import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram_bot import check_telegram_registrations, send_telegram_notification

def get_random_headers():
    """Return randomized headers to avoid detection"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

def check_tixr_resale():
    """Check for resale tickets using Tixr's API endpoints"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Add some persistence data to look more like a real browser
    session.cookies.set('session_id', f'gh_monitor_{random.randint(100000, 999999)}')
    
    try:
        # Longer random delay - be more patient
        initial_delay = random.uniform(3, 8)
        print(f"Waiting {initial_delay:.1f} seconds before request...")
        time.sleep(initial_delay)
        
        # First, visit the main page to establish session
        headers = get_random_headers()
        headers['Referer'] = 'https://www.google.com/'
        
        main_response = session.get('https://www.tixr.com/', headers=headers, timeout=30)
        print(f"Main page status: {main_response.status_code}")
        
        if main_response.status_code == 200:
            print("✅ Successfully visited main page")
            
            # Small delay
            time.sleep(random.uniform(1, 3))
            
            # Now call the API endpoints like the real site does
            api_headers = get_random_headers()
            api_headers['Accept'] = 'application/json, text/plain, */*'
            api_headers['Referer'] = 'https://www.tixr.com/'
            api_headers['X-Requested-With'] = 'XMLHttpRequest'
            
            # First API call - page requirements
            requirements_url = "https://www.tixr.com/api/page/requirements?url=/groups/100x/events/valley-of-the-seven-stars-cosmic-campout-135703"
            print("Calling requirements API...")
            req_response = session.get(requirements_url, headers=api_headers, timeout=30)
            print(f"Requirements API status: {req_response.status_code}")
            
            if req_response.status_code == 200:
                print("✅ Requirements API successful")
                
                # Small delay before next API call
                time.sleep(random.uniform(0.5, 2))
                
                # Second API call - event details
                event_api_url = "https://www.tixr.com/api/events/135703"
                print("Calling event API...")
                event_response = session.get(event_api_url, headers=api_headers, timeout=30)
                print(f"Event API status: {event_response.status_code}")
                
                if event_response.status_code == 200:
                    print("✅ Event API successful")
                    
                    # Parse the JSON response to check for resale tickets
                    try:
                        event_data = event_response.json()
                        return check_resale_in_json(event_data)
                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        return False
                else:
                    print(f"❌ Event API failed with status {event_response.status_code}")
                    return try_html_fallback(session)
            else:
                print(f"❌ Requirements API failed with status {req_response.status_code}")
                return try_html_fallback(session)
        else:
            print(f"❌ Main page failed with status {main_response.status_code}")
            return try_html_fallback(session)
            
    except Exception as e:
        print(f"Error in API approach: {e}")
        return try_html_fallback(session)
    finally:
        session.close()

def check_resale_in_json(event_data):
    """Check for resale tickets in the JSON API response"""
    try:
        print("Analyzing event data for resale tickets...")
        
        # Print some debug info about what we received
        if 'name' in event_data:
            print(f"Event: {event_data['name']}")
        
        # Look for ticket types or variants
        ticket_sections = []
        
        # Check common API response structures
        for key in ['ticketTypes', 'variants', 'tickets', 'products']:
            if key in event_data:
                ticket_sections.extend(event_data[key] if isinstance(event_data[key], list) else [event_data[key]])
        
        # Check for any tickets that might be resale
        for ticket in ticket_sections:
            if isinstance(ticket, dict):
                # Look for resale indicators
                state = ticket.get('state', '').upper()
                status = ticket.get('status', '').upper()
                availability = ticket.get('availability', '').upper()
                ticket_type = ticket.get('type', '').upper()
                
                print(f"Ticket found - State: {state}, Status: {status}, Type: {ticket_type}")
                
                if any(indicator in [state, status, availability, ticket_type] for indicator in ['RESALE', 'SECONDARY', 'RESOLD']):
                    print("🎉 RESALE TICKETS FOUND IN API!")
                    url = "https://www.tixr.com/groups/100x/events/valley-of-the-seven-stars-cosmic-campout-135703"
                    send_telegram_notification(url)
                    send_notification(url)
                    return True
        
        print("No resale tickets found in API response")
        return False
        
    except Exception as e:
        print(f"Error checking JSON for resale: {e}")
        return False

def try_html_fallback(session):
    """Fallback to HTML scraping if API fails"""
    print("Falling back to HTML scraping...")
    
    url = "https://www.tixr.com/groups/100x/events/valley-of-the-seven-stars-cosmic-campout-135703"
    
    try:
        headers = get_random_headers()
        headers['Referer'] = 'https://www.tixr.com/'
        
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return parse_response(response)
        else:
            print(f"HTML fallback failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"HTML fallback error: {e}")
        return False

def try_alternative_methods(session, url):
    """Try alternative methods when getting 403"""
    
    # Method 1: Try with minimal headers
    try:
        print("Trying with minimal headers...")
        minimal_headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; TicketMonitor/1.0)'
        }
        response = session.get(url, headers=minimal_headers, timeout=30)
        if response.status_code == 200:
            print("✅ Success with minimal headers")
            return parse_response(response)
    except Exception as e:
        print(f"Minimal headers failed: {e}")
    
    # Method 2: Try without any custom headers
    try:
        print("Trying with default headers...")
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            print("✅ Success with default headers")
            return parse_response(response)
    except Exception as e:
        print(f"Default headers failed: {e}")
    
    # Method 3: Try with a much longer delay and different approach
    try:
        print("Trying with much longer delay and clean session...")
        session.close()  # Close old session
        session = requests.Session()  # Fresh session
        
        # Much longer delay
        delay = random.uniform(15, 30)
        print(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
        
        # Try to mimic coming from the main Tixr page first
        main_page_headers = get_random_headers()
        main_page_headers['Referer'] = 'https://www.tixr.com/'
        
        # Visit main page first
        main_response = session.get('https://www.tixr.com/', headers=main_page_headers, timeout=30)
        if main_response.status_code == 200:
            print("✅ Successfully visited main page")
            
            # Now call their API like the real site does
            time.sleep(random.uniform(1, 3))
            api_url = "https://www.tixr.com/api/events?eventName=seven%20stars&page=1&pageSize=20"
            
            api_headers = get_random_headers()
            api_headers['Referer'] = 'https://www.tixr.com/'
            api_headers['Accept'] = 'application/json, text/plain, */*'
            api_headers['X-Requested-With'] = 'XMLHttpRequest'
            
            print("Making API call...")
            api_response = session.get(api_url, headers=api_headers, timeout=30)
            print(f"API response status: {api_response.status_code}")
            
            if api_response.status_code == 200:
                print("✅ API call successful")
                
                # Now try the event page with more realistic navigation
                time.sleep(random.uniform(1, 3))
                event_headers = get_random_headers() 
                event_headers['Referer'] = 'https://www.tixr.com/'
                
                response = session.get(url, headers=event_headers, timeout=30)
                if response.status_code == 200:
                    print("✅ Success after API call + navigation")
                    return parse_response(response)
                else:
                    print(f"Event page still blocked: {response.status_code}")
            else:
                print(f"API call failed: {api_response.status_code}")
                # Continue with fallback approach
            
            # Now try the event page with more realistic navigation
            time.sleep(random.uniform(2, 5))
            
            # First try to visit the group page
            group_url = "https://www.tixr.com/groups/100x"
            group_headers = get_random_headers()
            group_headers['Referer'] = 'https://www.tixr.com/'
            
            group_response = session.get(group_url, headers=group_headers, timeout=30)
            if group_response.status_code == 200:
                print("✅ Successfully visited group page")
                time.sleep(random.uniform(1, 3))
                
                # Now try the event page
                event_headers = get_random_headers() 
                event_headers['Referer'] = group_url  # Come from group page
                event_headers['Cache-Control'] = 'no-cache'
                event_headers['Pragma'] = 'no-cache'
                
                response = session.get(url, headers=event_headers, timeout=30)
                if response.status_code == 200:
                    print("✅ Success after realistic navigation path")
                    return parse_response(response)
                else:
                    print(f"Event page returned: {response.status_code}")
            else:
                print(f"Group page returned: {group_response.status_code}")
                
                # Fallback: try event page directly from main page
                time.sleep(random.uniform(1, 3))
                event_headers = get_random_headers() 
                event_headers['Referer'] = 'https://www.tixr.com/'
                
                response = session.get(url, headers=event_headers, timeout=30)
                if response.status_code == 200:
                    print("✅ Success with direct approach from main page")
                    return parse_response(response)
    
    except Exception as e:
        print(f"Main page approach failed: {e}")
    
    print("❌ All alternative methods failed")
    return False

def parse_response(response):
    """Parse the response to check for resale tickets"""
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for resale indicators
        resale_element = soup.select_one("[state='RESALE']")
        if resale_element:
            print("🎉 RESALE TICKETS FOUND!")
            return True
        
        # Alternative check - look for sold out vs available
        sold_out_indicators = soup.find_all(text=lambda text: text and 'sold out' in text.lower())
        if not sold_out_indicators:
            print("🤔 No 'sold out' text found - tickets might be available")
            # You might want to send a notification here too
        
        return False
    except Exception as e:
        print(f"Error parsing response: {e}")
        return False

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
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "🎟️ Tixr Resale Tickets Available!"
    
    body = f"""
    Great news! Resale tickets are now available for your event.
    
    Check them out here: {event_url}
    
    Hurry - they might go fast!
    """
    
    message.attach(MIMEText(body, "plain"))
    
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
    # First check for new registrations
    print("Checking for Telegram registrations...")
    check_telegram_registrations()
    
    # Then check for resale tickets
    print("Checking for resale tickets...")
    check_tixr_resale()