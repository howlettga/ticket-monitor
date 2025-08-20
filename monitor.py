import requests
import urllib.parse
try:
    import cloudscraper  # Optional
except ImportError:  # pragma: no cover
    cloudscraper = None
import time
import random
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram_bot import check_telegram_registrations, send_telegram_notification

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Origin': 'https://www.tixr.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }

def create_scraper_session():
    """Create a Cloudflare-capable session to reduce 403 responses"""
    if cloudscraper is not None:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'macos',
                'desktop': True
            }
        )
        logger.info("Using cloudscraper session")
        return scraper
    logger.info("cloudscraper not available; falling back to requests Session")
    return requests.Session()

# Event-specific constants and helpers
EVENT_PATH = "/groups/100x/events/valley-of-the-seven-stars-135703"
EVENT_QUERY = "col=&a=L&filter=55:NA|56:NA&sort=RECOMMENDED"
EVENT_PAGE_URL = f"https://www.tixr.com{EVENT_PATH}?{EVENT_QUERY}"
FESTIVAL_SITE_REFERER = "https://www.sevenstarsfest.com/"
EVENT_API_URL = "https://www.tixr.com/api/events/135703"

def build_requirements_url():
    url_param = urllib.parse.quote(EVENT_PATH, safe="")
    qp_param = urllib.parse.quote("?" + EVENT_QUERY, safe="")
    return f"https://www.tixr.com/api/page/requirements?url={url_param}&queryParams={qp_param}"

def seed_cookies_from_env(session: requests.Session) -> None:
    """Optionally seed session cookies from an env var containing a raw Cookie header."""
    raw_cookie = os.getenv('TIXR_COOKIES') or os.getenv('TIXR_COOKIE_HEADER')
    if not raw_cookie:
        return
    try:
        parts = [p.strip() for p in raw_cookie.split(';') if p.strip()]
        seeded_names = []
        for part in parts:
            if '=' in part:
                name, value = part.split('=', 1)
                session.cookies.set(name.strip(), value.strip(), domain='.tixr.com')
                seeded_names.append(name.strip())
        if seeded_names:
            logger.info(f"Seeded cookies from env: {', '.join(seeded_names)}")
    except Exception:
        # Best effort; ignore malformed cookie strings
        pass

def check_festival_passes_resale():
    """Check for resale tickets in Festival Passes collection via API"""
    
    api_url = EVENT_API_URL
    session = create_scraper_session()
    logger.info(f"HTTP session: {session.__class__.__name__}")
    
    try:
        # Add random delay to be respectful
        delay = random.uniform(2, 5)
        logger.info(f"Waiting {delay:.1f} seconds before API request...")
        time.sleep(delay)
        
        # Set up session with realistic browsing behavior
        session.cookies.set('session_id', f'monitor_{random.randint(100000, 999999)}')
        seed_cookies_from_env(session)
        
        # Step 1: Navigate to the event page with external referer
        logger.info("Navigating to event page with external referer...")
        nav_headers = get_random_headers()
        nav_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        nav_headers['Referer'] = FESTIVAL_SITE_REFERER
        nav_headers['Sec-GPC'] = '1'
        nav_headers['Sec-Fetch-Dest'] = 'document'
        nav_headers['Sec-Fetch-Mode'] = 'navigate'
        nav_headers['Sec-Fetch-Site'] = 'cross-site'
        nav_headers['Sec-Fetch-User'] = '?1'
        nav_headers['Upgrade-Insecure-Requests'] = '1'
        # Origin typically not sent for top-level navigations
        nav_headers.pop('Origin', None)
        nav_response = session.get(EVENT_PAGE_URL, headers=nav_headers, timeout=30)
        logger.info(f"Event page status: {nav_response.status_code}")
        # Log presence of key cookies after navigation
        try:
            has_datadome = 'datadome' in session.cookies.get_dict(domain='.tixr.com')
        except Exception:
            has_datadome = 'datadome' in session.cookies.get_dict()
        logger.info(f"Cookies after nav - datadome present: {bool(has_datadome)}")
        if nav_response.status_code != 200:
            logger.warning("Failed to load event page, continuing anyway...")
        
        # Step 2: Request page requirements
        time.sleep(random.uniform(0.8, 1.5))
        logger.info("Requesting page requirements...")
        req_headers = get_random_headers()
        req_headers['Accept'] = '*/*'
        req_headers['Referer'] = EVENT_PAGE_URL
        req_headers['X-Requested-With'] = 'XMLHttpRequest'
        req_headers['X-NewRelic-ID'] = 'Ug8CWVVXGwcEUlFVDwM='
        req_headers['Sec-GPC'] = '1'
        req_headers['Sec-Fetch-Dest'] = 'empty'
        req_headers['Sec-Fetch-Mode'] = 'cors'
        req_headers['Sec-Fetch-Site'] = 'same-origin'
        requirements_url = build_requirements_url()
        req_response = session.get(requirements_url, headers=req_headers, timeout=30)
        logger.info(f"Requirements response status: {req_response.status_code}")
        
        # Make the API call
        logger.info("Making API request to get event data...")
        api_headers = get_random_headers()
        api_headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        api_headers['Referer'] = EVENT_PAGE_URL
        api_headers['X-Requested-With'] = 'XMLHttpRequest'
        api_headers['X-NewRelic-ID'] = 'Ug8CWVVXGwcEUlFVDwM='
        api_headers['Sec-GPC'] = '1'
        api_headers['Sec-Fetch-Dest'] = 'empty'
        api_headers['Sec-Fetch-Mode'] = 'cors'
        api_headers['Sec-Fetch-Site'] = 'same-origin'
        
        response = session.get(api_url, headers=api_headers, timeout=30)
        logger.info(f"API response status: {response.status_code}")
        
        if response.status_code == 200:
            return process_api_response(response.json())
        elif response.status_code == 403:
            logger.warning("Got 403 - trying fallback methods...")
            return try_api_fallback_methods(session, api_url)
        else:
            logger.error(f"API request failed with status: {response.status_code}")
            return try_web_scraping_fallback(session)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return try_web_scraping_fallback(session)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        session.close()

def process_api_response(data):
    """Process the API response to check for Festival Passes resale availability"""
    try:
        logger.info("Processing API response for Festival Passes resale tickets...")
        
        # Find the Festival Passes collection
        collections = data.get('collectionConfiguration', {}).get('collections', [])
        festival_passes_collection = None
        
        for collection in collections:
            if collection.get('name') == 'Festival Passes':
                festival_passes_collection = collection
                logger.info(f"Found Festival Passes collection with ID: {collection.get('id')}")
                break
        
        if not festival_passes_collection:
            logger.warning("Festival Passes collection not found")
            # Log available collections for debugging
            collection_names = [col.get('name', 'Unknown') for col in collections]
            logger.info(f"Available collections: {collection_names}")
            return False
        
        # Get the sales IDs from the Festival Passes collection
        festival_sales_ids = festival_passes_collection.get('sales', [])
        if isinstance(festival_sales_ids, list) and len(festival_sales_ids) > 0:
            # Handle both formats: list of IDs or list of objects with 'id' field
            if isinstance(festival_sales_ids[0], dict):
                festival_sales_ids = [sale.get('id') for sale in festival_sales_ids if sale.get('id')]
        
        logger.info(f"Found {len(festival_sales_ids)} Festival Passes sales to check")
        
        if not festival_sales_ids:
            logger.warning("No sales found in Festival Passes collection")
            return False
        
        # Get all sales data
        all_sales = data.get('sales', [])
        logger.info(f"Total sales in response: {len(all_sales)}")
        
        # Check Festival Passes sales for resale availability
        available_resales = []
        
        for sale in all_sales:
            sale_id = sale.get('id')
            if sale_id in festival_sales_ids:
                sale_state = sale.get('state', '')
                resale_state = sale.get('resaleState', '')
                
                logger.info(f"Sale ID {sale_id}: state='{sale_state}', resaleState='{resale_state}'")
                
                if resale_state == 'AVAILABLE':
                    available_resales.append({
                        'id': sale_id,
                        'state': sale_state,
                        'resaleState': resale_state
                    })
        
        if available_resales:
            logger.info(f"🎉 FOUND {len(available_resales)} FESTIVAL PASSES RESALE TICKETS AVAILABLE!")
            
            # Log details of available resales
            for resale in available_resales:
                logger.info(f"Available resale - ID: {resale['id']}, State: {resale['state']}")
            
            # Send notifications
            event_url = EVENT_PAGE_URL
            send_telegram_notification(event_url)
            send_notification(event_url, len(available_resales))
            return True
        else:
            logger.info("No Festival Passes resale tickets currently available")
            
            # Log status of all Festival Passes for debugging
            for sale in all_sales:
                if sale.get('id') in festival_sales_ids:
                    logger.debug(f"Festival Pass {sale.get('id')}: {sale.get('state')} / {sale.get('resaleState')}")
            
            return False
            
    except Exception as e:
        logger.error(f"Error processing API response: {e}")
        return False

def try_api_fallback_methods(session, api_url):
    """Try alternative methods when API returns 403"""
    
    logger.info("Trying API fallback methods...")
    
    # Method 1: Try with different headers
    try:
        logger.info("Trying with minimal headers...")
        minimal_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Origin': 'https://www.tixr.com',
            'Referer': EVENT_PAGE_URL
        }
        
        time.sleep(random.uniform(3, 6))
        response = session.get(api_url, headers=minimal_headers, timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ Success with minimal headers")
            return process_api_response(response.json())
            
    except Exception as e:
        logger.error(f"Minimal headers method failed: {e}")
    
    # Method 2: Fresh session with longer delay
    try:
        logger.info("Trying with fresh session and longer delay...")
        session.close()
        session = create_scraper_session()
        
        delay = random.uniform(10, 20)
        logger.info(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
        
        # Try to establish session more naturally
        event_page_url = EVENT_PAGE_URL
        page_headers = get_random_headers()
        page_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        
        page_response = session.get(event_page_url, headers=page_headers, timeout=30)
        
        if page_response.status_code == 200:
            logger.info("Successfully loaded event page, now trying API...")
            time.sleep(random.uniform(2, 4))
            
            api_headers = get_random_headers()
            response = session.get(api_url, headers=api_headers, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ Success after loading event page first")
                return process_api_response(response.json())
                
    except Exception as e:
        logger.error(f"Fresh session method failed: {e}")
    
    logger.warning("All API fallback methods failed")
    return False

def try_web_scraping_fallback(session):
    """Fallback to web scraping if API completely fails"""
    logger.info("Falling back to web scraping...")
    
    from bs4 import BeautifulSoup
    
    try:
        url = EVENT_PAGE_URL
        headers = get_random_headers()
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        
        time.sleep(random.uniform(3, 7))
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for resale indicators in HTML
            resale_elements = soup.find_all(attrs={'data-state': 'RESALE'}) or \
                            soup.find_all(text=lambda x: x and 'resale' in x.lower()) or \
                            soup.select('[state="RESALE"]')
            
            if resale_elements:
                logger.info("🎉 Found resale indicators in HTML!")
                send_telegram_notification(url)
                send_notification(url, 1)
                return True
            else:
                logger.info("No resale indicators found in HTML")
                return False
        else:
            logger.error(f"Web scraping failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Web scraping fallback failed: {e}")
        return False

def send_notification(event_url, num_tickets=1):
    """Send email notification when resale tickets are found"""
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        logger.warning("Email credentials not configured")
        return
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"🎟️ {num_tickets} Festival Passes Resale Ticket(s) Available!"
    
    body = f"""
    Great news! {num_tickets} Festival Passes resale ticket(s) are now available for Valley of the Seven Stars!
    
    Check them out here: {event_url}
    
    Hurry - resale tickets usually go fast!
    
    This alert was sent by your Tixr ticket monitor.
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        logger.info("Notification email sent!")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    logger.info("Starting Tixr Festival Passes resale monitor...")
    
    # First check for new Telegram registrations
    try:
        logger.info("Checking for Telegram registrations...")
        check_telegram_registrations()
    except Exception as e:
        logger.error(f"Error checking Telegram registrations: {e}")
    
    # Check for Festival Passes resale tickets
    try:
        logger.info("Checking for Festival Passes resale tickets...")
        result = check_festival_passes_resale()
        if result:
            logger.info("✅ Resale tickets found and notifications sent!")
        else:
            logger.info("No resale tickets found at this time")
    except Exception as e:
        logger.error(f"Error in main check: {e}")
    
    logger.info("Monitor check complete")