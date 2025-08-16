import requests
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def has_free_food(description):
    """Checks if the event description mentions free food."""
    food_keywords = ["free food", "pizza", "bbq", "snacks", "refreshments", "food provided"]
    description_lower = description.lower()
    for keyword in food_keywords:
        if keyword in description_lower:
            return True
    return False

headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://campus.hellorubric.com',
    'priority': 'u=1, i',
    'referer': 'https://campus.hellorubric.com/',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
}

# EXACT string taken from network request
data = {
    'details': '{"firstCall":true,"sortType":"date","desiredType":"events","limit":200,"offset":0,"sortDirection":"asc","searchQuery":"","eventsPeriodFilter":"All","countryCode":"AU","state":"Queensland","selectedUniversityId":"12","currentUrl":"https://campus.hellorubric.com/search?country=AU&state=Queensland&universityid=12&type=events","device":"web_portal","version":4}',
    'endpoint': 'getUnifiedSearch',
}

response = requests.post('https://api.hellorubric.com/', headers=headers, data=data)

try:
    results = response.json()
except json.JSONDecodeError:
    print("JSON decode error. Raw response:")
    print(response.text)
    exit()

with open("event_data.json", 'w') as file:
    file.write(json.dumps(results,indent=2))

events = results.get("results", [])
print(f"Found {len(events)} events")

with open("results.json", "w") as file:
    json.dump(events, file, indent=2)

free_events = [event for event in events if event.get("info") == "Free"]

food_events = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    for event in free_events:
        link_extension = event.get("destination")
        if link_extension:
            event_url = "https://campus.hellorubric.com" + link_extension
            try:
                page.goto(event_url)
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                description_element = soup.find("div", id="eventName2")
                if description_element:
                    description = description_element.get_text()
                    if has_free_food(description):
                        event["free_food"] = True
                        food_events.append(event)
            except Exception as e:
                print(f"Error fetching event page with playwright: {e}")
    browser.close()


with open("free_events.json", "w") as file:
    json.dump(food_events, file, indent=2)

with open("pretty_event_data.txt", "w") as file:
    for event in food_events:
        title = event.get("title", "No title")
        month = event.get("month", "No time")
        day = event.get("day", "no day")
        societyname = event.get("societyname", "No location")
        price = event.get("info", "No price found")
        link_extension = event.get("destination", "No link")
        
        print(f"📅 {title}")
        print(f"   🕒 {month} {day}")
        print(f"   📍 {societyname}")
        print(f"   📝 {price}")
        print(f"   ⛓️‍💥 {'https://campus.hellorubric.com' + link_extension}\n")

        file.write(f"📅 {title}\n")
        file.write(f"   🕒 {month} {day}\n")
        file.write(f"   📍 {societyname}\n")
        file.write(f"   📝 {price}\n")
        file.write(f"   ⛓️‍💥 {'https://campus.hellorubric.com' + link_extension}\n")

print(f"Found {len(food_events)} free events with food")
