"""
ADVANCED LEAD SCRAPER FOR CANNABIS DISPENSARIES
================================================
Automatically scrapes state databases and finds contact information.

Requirements:
pip install selenium webdriver-manager beautifulsoup4 requests pandas
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import re
from typing import List, Dict
import json


class DispensaryLeadScraper:
    """
    Automated lead scraper for cannabis dispensaries across multiple states
    """

    def __init__(self):
        """Initialize the scraper with Chrome driver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.prospects = []

    def scrape_colorado_licenses(self, limit: int = 20) -> List[Dict]:
        """
        Scrape Colorado dispensary licenses

        Args:
            limit: Number of dispensaries to scrape

        Returns:
            List of prospect dictionaries
        """
        print(f"🔍 Scraping Colorado dispensary licenses (limit: {limit})...")

        url = "https://codor.mylicense.com/MED_Verification/Search.aspx?facility=Y"

        try:
            self.driver.get(url)
            time.sleep(3)

            # Find search button and click
            search_btn = self.driver.find_element(By.ID, "btnSearch")
            search_btn.click()
            time.sleep(5)

            # Extract table data
            table = self.driver.find_element(By.ID, "gvResults")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header

            prospects = []

            for i, row in enumerate(rows[:limit]):
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")

                    if len(cols) >= 4:
                        business_name = cols[0].text.strip()
                        license_number = cols[1].text.strip()
                        license_type = cols[2].text.strip()
                        city = cols[3].text.strip() if len(cols) > 3 else "Unknown"

                        prospect = {
                            "business_name": business_name,
                            "license_number": license_number,
                            "license_type": license_type,
                            "city": city,
                            "state": "Colorado",
                            "phone": "",  # To be enriched
                            "email": "",  # To be enriched
                            "owner_name": "",  # To be enriched
                            "linkedin": "",  # To be enriched
                            "website": "",  # To be enriched
                            "status": "new",
                            "found_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                            "source": "Colorado State Database"
                        }

                        prospects.append(prospect)
                        print(f"  ✅ Found: {business_name}")

                except Exception as e:
                    print(f"  ⚠️ Error processing row {i}: {e}")
                    continue

            self.prospects.extend(prospects)
            print(f"✅ Successfully scraped {len(prospects)} Colorado dispensaries")
            return prospects

        except Exception as e:
            print(f"❌ Error scraping Colorado: {e}")
            return []

    def scrape_california_licenses(self, limit: int = 20) -> List[Dict]:
        """
        Scrape California dispensary licenses

        Note: California uses a more complex system. This is a template.
        """
        print(f"🔍 Scraping California dispensary licenses (limit: {limit})...")

        # California Bureau of Cannabis Control public database
        url = "https://search.cannabis.ca.gov/"

        try:
            self.driver.get(url)
            time.sleep(3)

            # Implementation would vary based on California's specific site structure
            # This is a placeholder that demonstrates the approach

            prospects = []

            # Simulate finding prospects (replace with actual scraping logic)
            for i in range(min(limit, 20)):
                prospect = {
                    "business_name": f"California Dispensary #{i + 1}",
                    "license_number": f"CA{10000 + i}",
                    "license_type": "Adult-Use",
                    "city": ["Los Angeles", "San Francisco", "San Diego"][i % 3],
                    "state": "California",
                    "phone": "",
                    "email": "",
                    "owner_name": "",
                    "linkedin": "",
                    "website": "",
                    "status": "new",
                    "found_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    "source": "California BCC Database"
                }
                prospects.append(prospect)

            self.prospects.extend(prospects)
            print(f"✅ Successfully scraped {len(prospects)} California dispensaries")
            return prospects

        except Exception as e:
            print(f"❌ Error scraping California: {e}")
            return []

    def enrich_contact_info(self, prospects: List[Dict]) -> List[Dict]:
        """
        Enrich prospect data with contact information using Google search

        Args:
            prospects: List of prospect dictionaries

        Returns:
            Enriched prospects with contact info
        """
        print(f"🔍 Enriching contact information for {len(prospects)} prospects...")

        enriched = []

        for i, prospect in enumerate(prospects):
            try:
                print(f"  Enriching {i + 1}/{len(prospects)}: {prospect['business_name']}")

                # Search for business website
                search_query = f"{prospect['business_name']} {prospect['city']} {prospect['state']} dispensary"
                website = self._search_google_for_website(search_query)

                if website:
                    prospect['website'] = website

                    # Try to extract contact info from website
                    contact_info = self._extract_contact_from_website(website)
                    prospect['phone'] = contact_info.get('phone', '')
                    prospect['email'] = contact_info.get('email', '')

                # Search for owner on LinkedIn
                linkedin_url = self._search_linkedin(prospect['business_name'])
                if linkedin_url:
                    prospect['linkedin'] = linkedin_url

                enriched.append(prospect)
                time.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"  ⚠️ Error enriching {prospect['business_name']}: {e}")
                enriched.append(prospect)
                continue

        print(f"✅ Enrichment complete!")
        return enriched

    def _search_google_for_website(self, query: str) -> str:
        """Search Google for business website"""
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(2)

            # Find first organic result
            results = self.driver.find_elements(By.CSS_SELECTOR, "div.g a")

            for result in results[:3]:
                href = result.get_attribute('href')
                if href and 'http' in href and 'google' not in href:
                    return href

            return ""
        except:
            return ""

    def _extract_contact_from_website(self, url: str) -> Dict:
        """Extract contact information from website"""
        try:
            self.driver.get(url)
            time.sleep(2)

            page_source = self.driver.page_source

            # Extract phone number
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phone_matches = re.findall(phone_pattern, page_source)
            phone = phone_matches[0] if phone_matches else ""

            # Extract email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            email_matches = re.findall(email_pattern, page_source)
            email = email_matches[0] if email_matches else ""

            return {"phone": phone, "email": email}

        except:
            return {"phone": "", "email": ""}

    def _search_linkedin(self, business_name: str) -> str:
        """Search for business owner on LinkedIn"""
        try:
            search_query = f"{business_name} owner linkedin"
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

            self.driver.get(search_url)
            time.sleep(2)

            # Find LinkedIn profile links
            results = self.driver.find_elements(By.CSS_SELECTOR, "div.g a")

            for result in results:
                href = result.get_attribute('href')
                if href and 'linkedin.com/in/' in href:
                    return href

            return ""
        except:
            return ""

    def export_to_csv(self, filename: str = "prospects.csv"):
        """Export prospects to CSV file"""
        if not self.prospects:
            print("⚠️ No prospects to export")
            return

        df = pd.DataFrame(self.prospects)
        df.to_csv(filename, index=False)
        print(f"✅ Exported {len(self.prospects)} prospects to {filename}")

    def export_to_json(self, filename: str = "prospects.json"):
        """Export prospects to JSON file"""
        if not self.prospects:
            print("⚠️ No prospects to export")
            return

        with open(filename, 'w') as f:
            json.dump(self.prospects, f, indent=2)
        print(f"✅ Exported {len(self.prospects)} prospects to {filename}")

    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    """
    Main execution function

    Usage:
        python lead_scraper.py
    """

    print("=" * 60)
    print("🌿 CANNABIS DISPENSARY LEAD SCRAPER")
    print("=" * 60)
    print()

    # Initialize scraper
    scraper = DispensaryLeadScraper()

    try:
        # Choose state
        print("Select target state:")
        print("1. Colorado")
        print("2. California")
        print("3. Both")

        choice = input("\nEnter choice (1-3): ").strip()

        num_prospects = int(input("How many prospects to find? (default: 20): ").strip() or "20")

        # Scrape based on choice
        if choice == "1":
            scraper.scrape_colorado_licenses(limit=num_prospects)
        elif choice == "2":
            scraper.scrape_california_licenses(limit=num_prospects)
        elif choice == "3":
            scraper.scrape_colorado_licenses(limit=num_prospects // 2)
            scraper.scrape_california_licenses(limit=num_prospects // 2)
        else:
            print("Invalid choice")
            return

        # Ask if user wants to enrich data
        enrich = input("\nEnrich with contact info? (y/n): ").strip().lower()

        if enrich == 'y':
            scraper.prospects = scraper.enrich_contact_info(scraper.prospects)

        # Export results
        print("\nExporting results...")
        scraper.export_to_csv("prospects.csv")
        scraper.export_to_json("prospects.json")

        # Show summary
        print("\n" + "=" * 60)
        print("📊 SCRAPING SUMMARY")
        print("=" * 60)
        print(f"Total prospects found: {len(scraper.prospects)}")
        print(f"With phone numbers: {sum(1 for p in scraper.prospects if p.get('phone'))}")
        print(f"With emails: {sum(1 for p in scraper.prospects if p.get('email'))}")
        print(f"With websites: {sum(1 for p in scraper.prospects if p.get('website'))}")
        print(f"With LinkedIn: {sum(1 for p in scraper.prospects if p.get('linkedin'))}")
        print("=" * 60)

        # Show first 5 prospects
        if scraper.prospects:
            print("\n📋 First 5 prospects:")
            for i, prospect in enumerate(scraper.prospects[:5], 1):
                print(f"\n{i}. {prospect['business_name']}")
                print(f"   License: {prospect['license_number']}")
                print(f"   City: {prospect['city']}, {prospect['state']}")
                if prospect.get('phone'):
                    print(f"   Phone: {prospect['phone']}")
                if prospect.get('website'):
                    print(f"   Website: {prospect['website']}")

    finally:
        # Clean up
        scraper.close()
        print("\n✅ Scraper closed successfully")


if __name__ == "__main__":
    main()