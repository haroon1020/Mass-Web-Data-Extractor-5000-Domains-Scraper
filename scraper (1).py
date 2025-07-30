"""
scraper.py

Contains scraping logic to:
- Download pages
- Extract internal links
- Match page types
- Clean HTML
"""

import re
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

PAGE_TYPE_PATTERNS = {
    "Team & People": r"/(team|our[-_]team)",
    "Leadership / Exec": r"/(leadership|executives?)",
    "Board / Advisors": r"/(board|board[-]of[-]directors)",
    "Faculty / Research": r"/(faculty|faculty[-_]directory)",
    "Authors / Contributors": r"/(authors?|contributors?)",
    "Contact / Support": r"/(contact|contact[-_]us)",
    "About / Company": r"/(about|about[-_]us)",
    "Careers / HR": r"/(careers?|jobs?)",
    "Partners / Affiliates": r"/(partners?|affiliates?)",
    "Media / Press": r"/(press|media)",
    "Locations / Offices": r"/(locations?|offices?)",
    "Lawyers": r"/(attorneys?|lawyers?)",
    "Events / Speakers": r"/(events?|conference)",
    "Departments / Administration": r"/(departments?|academic[-_]departments?)",
    "Services Sections": r"/(services?|treatments?)"
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0 Safari/537.36"
    )
}

PROXIES = {
    "http": "http://YOUR_PROXY_HERE",
    "https": "http://YOUR_PROXY_HERE"
}

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.extract()
    return str(soup)[:30000]

def collect_internal_links(base_url):
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=15, proxies=PROXIES)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {base_url}: {e}")
        return set()

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        parsed = urlparse(href)
        if not parsed.netloc or parsed.netloc == urlparse(base_url).netloc:
            links.add(urljoin(base_url, href))
    return links

def match_page_type(url):
    path = urlparse(url).path.lower()
    for group, pattern in PAGE_TYPE_PATTERNS.items():
        if re.search(pattern, path):
            return group
    return None
