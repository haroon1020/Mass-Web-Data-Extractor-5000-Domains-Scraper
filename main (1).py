"""
main.py

Coordinates scraping, GPT extraction, and JSON output.
"""

import json
import requests
from scraper import collect_internal_links, clean_html, match_page_type, HEADERS, PROXIES
from gpt_utils import extract_contact_info

def main():
    input_file = r"C:\Users\dell\Downloads\random_5000_websites_from_master_database.txt"
    output_data = []

    with open(input_file, "r", encoding="utf-8") as f:
        domains = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(domains)} domains.")

    for idx, domain in enumerate(domains, 1):
        if not domain.startswith("http"):
            domain = "https://" + domain

        print(f"\n[{idx}/{len(domains)}] Processing {domain}...")

        links = collect_internal_links(domain)

        for link in links:
            page_type = match_page_type(link)
            if not page_type:
                continue

            print(f"  ➜ Matched {page_type}: {link}")

            try:
                resp = requests.get(link, headers=HEADERS, timeout=15, proxies=PROXIES)
                resp.raise_for_status()

                cleaned = clean_html(resp.text)
                contact = extract_contact_info(cleaned, page_type, link)

                if contact and ("first_name" in contact or "full_name" in contact):
                    output_data.append(contact)
            except Exception as e:
                print(f"  Error processing {link}: {e}")

    with open("extracted_contacts.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Done. {len(output_data)} records saved to extracted_contacts.json")

if __name__ == "__main__":
    main()
