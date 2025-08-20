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
    """Check for resale tickets with improved anti-detection measures"""
    url = "https://www.tixr.com/groups/100x/events/valley-of-the-seven-stars-cosmic-campout-135703"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Add some persistence data to look more like a real browser
    session.cookies.set('session_id', f'gh_monitor_{random.randint(100000, 999999)}')
    
    try:
        # Longer random delay - be more patient
        initial_delay = random.uniform(3, 8)
        print(f"Waiting {initial_delay:.1f} seconds before request...")
        time.sleep(initial_delay)
        
        # Get randomized headers
        headers = get_random_headers()
        
        # Add referrer to look more natural
        headers['Referer'] = 'https://www.google.com/'
        
        # Make request with session
        response = session.get(url, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 403:
            print("❌ Access denied (403). Tixr is blocking the request.")
            # Try alternative approaches
            return try_alternative_methods(session, url)
        
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Debug: Print page title to confirm we got the right page
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text().strip()}")
        
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
            # Try alternative selectors
            element = soup.select_one("[state='RESALE']")
        
        if element:
            print("🎉 RESALE TICKETS AVAILABLE!")
            send_telegram_notification(url)
            send_notification(url)
            return True
        else:
            print("No resale tickets yet - still sold out")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False
    except Exception as e:
        print(f"Error checking page: {e}")
        return False
    finally:
        session.close()

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