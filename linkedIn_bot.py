"""
LINKEDIN AUTOMATED OUTREACH BOT
================================
Automatically sends personalized connection requests and follow-up messages.

⚠️ IMPORTANT: Use responsibly. LinkedIn has daily limits:
   - Max 100 connection requests per week
   - Max 20-30 messages per day
   - Always add delays between actions

Requirements:
pip install selenium webdriver-manager pandas
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from typing import List, Dict
import json
from datetime import datetime


class LinkedInAutomation:
    """
    Automated LinkedIn outreach system

    Features:
    - Send personalized connection requests
    - Send follow-up messages
    - Track responses
    - Export results
    """

    def __init__(self, email: str, password: str):
        """
        Initialize LinkedIn automation

        Args:
            email: Your LinkedIn email
            password: Your LinkedIn password
        """
        self.email = email
        self.password = password
        self.driver = None
        self.results = []

    def start_browser(self, headless: bool = False):
        """Start Chrome browser"""
        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument('--headless')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        print("✅ Browser started")

    def login(self):
        """Login to LinkedIn"""
        print("🔐 Logging in to LinkedIn...")

        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)

            # Enter email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(self.email)

            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)

            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            time.sleep(5)

            # Check if login successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed. Please check credentials.")
                return False

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def search_prospects(self, search_term: str, location: str = "", limit: int = 20) -> List[str]:
        """
        Search for prospects on LinkedIn

        Args:
            search_term: e.g., "cannabis dispensary owner"
            location: e.g., "Colorado, United States"
            limit: Number of profiles to collect

        Returns:
            List of profile URLs
        """
        print(f"🔍 Searching LinkedIn for: {search_term}")

        profile_urls = []

        try:
            # Build search URL
            search_query = search_term.replace(" ", "%20")
            url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"

            if location:
                location_query = location.replace(" ", "%20")
                url += f"&origin=FACETED_SEARCH&geoUrn=%5B%22{location_query}%22%5D"

            self.driver.get(url)
            time.sleep(5)

            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Extract profile URLs
            results = self.driver.find_elements(By.CSS_SELECTOR, "a.app-aware-link")

            for result in results:
                href = result.get_attribute('href')
                if href and '/in/' in href and href not in profile_urls:
                    profile_urls.append(href.split('?')[0])  # Clean URL

                    if len(profile_urls) >= limit:
                        break

            print(f"✅ Found {len(profile_urls)} profiles")
            return profile_urls

        except Exception as e:
            print(f"❌ Search error: {e}")
            return profile_urls

    def send_connection_request(self, profile_url: str, message: str = "") -> bool:
        """
        Send connection request to a profile

        Args:
            profile_url: LinkedIn profile URL
            message: Optional personalized message (max 300 chars)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.get(profile_url)
            time.sleep(random.uniform(3, 5))

            # Try to find and click Connect button
            connect_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Connect')]")

            if not connect_buttons:
                print(f"  ⚠️ No Connect button found (might be already connected)")
                return False

            connect_buttons[0].click()
            time.sleep(2)

            # If message provided, add note
            if message:
                try:
                    add_note_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Add a note']")
                    add_note_btn.click()
                    time.sleep(1)

                    note_field = self.driver.find_element(By.ID, "custom-message")
                    note_field.send_keys(message[:300])  # LinkedIn limit
                    time.sleep(1)

                    send_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send now']")
                    send_btn.click()

                except:
                    # If can't add note, send without
                    send_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send without a note']")
                    send_btn.click()
            else:
                # Send without note
                send_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send without a note']")
                send_btn.click()

            time.sleep(2)
            print(f"  ✅ Connection request sent")
            return True

        except Exception as e:
            print(f"  ❌ Error sending request: {e}")
            return False

    def send_message(self, profile_url: str, message: str) -> bool:
        """
        Send direct message to a connection

        Args:
            profile_url: LinkedIn profile URL
            message: Message content

        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.get(profile_url)
            time.sleep(random.uniform(3, 5))

            # Click Message button
            message_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Message')]")
            message_btn.click()
            time.sleep(2)

            # Type message
            message_box = self.driver.find_element(By.CSS_SELECTOR, "div.msg-form__contenteditable")
            message_box.click()
            message_box.send_keys(message)
            time.sleep(1)

            # Send message
            send_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            send_btn.click()

            time.sleep(2)
            print(f"  ✅ Message sent")
            return True

        except Exception as e:
            print(f"  ❌ Error sending message: {e}")
            return False

    def bulk_connect(self, prospects: List[Dict], message_template: str = "", limit: int = 20):
        """
        Send bulk connection requests with personalization

        Args:
            prospects: List of prospect dictionaries with 'business_name', 'owner_name', 'city', etc.
            message_template: Template with placeholders like {business_name}, {city}
            limit: Maximum requests to send
        """
        print(f"📧 Starting bulk connection campaign (limit: {limit})")

        sent_count = 0

        for i, prospect in enumerate(prospects[:limit]):
            try:
                print(
                    f"\n[{i + 1}/{min(len(prospects), limit)}] Processing: {prospect.get('business_name', 'Unknown')}")

                # Search for the person
                search_term = f"{prospect.get('business_name', '')} {prospect.get('city', '')} owner"
                profile_urls = self.search_prospects(search_term, limit=1)

                if not profile_urls:
                    print("  ⚠️ No profile found")
                    continue

                profile_url = profile_urls[0]

                # Personalize message
                message = message_template.format(
                    business_name=prospect.get('business_name', ''),
                    city=prospect.get('city', ''),
                    name=prospect.get('owner_name', '')
                )

                # Send connection request
                success = self.send_connection_request(profile_url, message)

                if success:
                    sent_count += 1

                    # Log result
                    self.results.append({
                        "profile_url": profile_url,
                        "business_name": prospect.get('business_name'),
                        "action": "connection_sent",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "message": message
                    })

                # Random delay to avoid detection (30-60 seconds)
                delay = random.uniform(30, 60)
                print(f"  ⏳ Waiting {delay:.0f} seconds before next request...")
                time.sleep(delay)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        print(f"\n✅ Campaign complete! Sent {sent_count} connection requests")

    def bulk_message(self, connections: List[str], message_template: str, limit: int = 20):
        """
        Send bulk messages to existing connections

        Args:
            connections: List of profile URLs (must be existing connections)
            message_template: Message template
            limit: Maximum messages to send
        """
        print(f"📧 Starting bulk messaging campaign (limit: {limit})")

        sent_count = 0

        for i, profile_url in enumerate(connections[:limit]):
            try:
                print(f"\n[{i + 1}/{min(len(connections), limit)}] Messaging: {profile_url}")

                # Send message
                success = self.send_message(profile_url, message_template)

                if success:
                    sent_count += 1

                    # Log result
                    self.results.append({
                        "profile_url": profile_url,
                        "action": "message_sent",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "message": message_template
                    })

                # Random delay (20-40 seconds)
                delay = random.uniform(20, 40)
                print(f"  ⏳ Waiting {delay:.0f} seconds...")
                time.sleep(delay)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        print(f"\n✅ Campaign complete! Sent {sent_count} messages")

    def export_results(self, filename: str = "linkedin_campaign_results.csv"):
        """Export campaign results to CSV"""
        if not self.results:
            print("⚠️ No results to export")
            return

        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"✅ Exported {len(self.results)} results to {filename}")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")


def main():
    """
    Main execution function

    Usage:
        python linkedin_automation.py
    """

    print("=" * 60)
    print("🔗 LINKEDIN AUTOMATION BOT")
    print("=" * 60)
    print()

    # Get credentials
    email = input("LinkedIn Email: ").strip()
    password = input("LinkedIn Password: ").strip()

    # Initialize bot
    bot = LinkedInAutomation(email, password)

    try:
        # Start browser
        bot.start_browser(headless=False)

        # Login
        if not bot.login():
            return

        # Menu
        print("\nWhat would you like to do?")
        print("1. Search for prospects")
        print("2. Send bulk connection requests")
        print("3. Send bulk messages to connections")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            search_term = input("Search term (e.g., 'cannabis dispensary owner'): ").strip()
            location = input("Location (e.g., 'Colorado, United States'): ").strip()
            limit = int(input("How many profiles to find? ").strip())

            profiles = bot.search_prospects(search_term, location, limit)

            print(f"\n📋 Found {len(profiles)} profiles:")
            for i, url in enumerate(profiles, 1):
                print(f"{i}. {url}")

        elif choice == "2":
            # Load prospects from CSV
            prospects_file = input("Prospects CSV file (default: prospects.csv): ").strip() or "prospects.csv"

            try:
                df = pd.read_csv(prospects_file)
                prospects = df.to_dict('records')
                print(f"✅ Loaded {len(prospects)} prospects")
            except:
                print("❌ Could not load prospects file")
                return

            # Message template
            print("\nDefault message template:")
            print(
                "Hi {business_name} team! Noticed you're in {city}. I help dispensaries with compliance docs. Would love to connect!")

            use_default = input("Use default template? (y/n): ").strip().lower()

            if use_default == 'y':
                message = "Hi! Noticed your dispensary in {city}. I help with compliance documentation. Would love to connect!"
            else:
                message = input("Enter your message template: ").strip()

            limit = int(input("How many connection requests to send? (max 20): ").strip())

            # Send requests
            bot.bulk_connect(prospects, message, min(limit, 20))

        elif choice == "3":
            # Load connections
            connections_file = input("Connections file (list of URLs, one per line): ").strip()

            try:
                with open(connections_file, 'r') as f:
                    connections = [line.strip() for line in f if line.strip()]
                print(f"✅ Loaded {len(connections)} connections")
            except:
                print("❌ Could not load connections file")
                return

            message = input("Enter your message: ").strip()
            limit = int(input("How many messages to send? (max 20): ").strip())

            # Send messages
            bot.bulk_message(connections, message, min(limit, 20))

        # Export results
        bot.export_results()

        print("\n✅ All done!")

    finally:
        # Clean up
        bot.close()


if __name__ == "__main__":
    main()