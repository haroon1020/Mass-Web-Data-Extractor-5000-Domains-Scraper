"""
gpt_utils.py

Handles GPT calls to extract structured contact info from HTML.
"""

import json
import time
from datetime import datetime, timezone
import openai

# Direct API key assignment
openai.api_key = "your api key"

def extract_contact_info(html_content, page_type, url):
    """
    Sends HTML to GPT and parses JSON response.
    """
    prompt = f"""
You are a web data extraction engine.

From the HTML below, extract any publicly listed contact information about a person.
Return only a JSON object with these fields:
- first_name
- last_name
- full_name
- title
- email
- phone
- source_url
- page_type
- scraped_at

If no contact information is found, return an empty object: {{}}

HTML:
{html_content}
"""

    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            text = response.choices[0].message["content"].strip()
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            json_str = text[json_start:json_end]
            data = json.loads(json_str)

            clean_data = {
                k: v for k, v in data.items()
                if v and v.strip().lower() not in {"n/a", "unknown"}
            }

            clean_data["source_url"] = url
            clean_data["page_type"] = page_type
            clean_data["scraped_at"] = datetime.now(timezone.utc).isoformat()

            return clean_data
        except openai.error.RateLimitError:
            print("Rate limit hit, waiting...")
            time.sleep(5)
        except Exception as e:
            print(f"GPT error: {e}")
            return {}
    return {}
