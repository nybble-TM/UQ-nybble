import requests
import json

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
    'details': '{"firstCall":true,"sortType":"date","desiredType":"events","limit":12,"offset":0,"sortDirection":"asc","searchQuery":"","eventsPeriodFilter":"All","countryCode":"AU","state":"Queensland","selectedUniversityId":"12","currentUrl":"https://campus.hellorubric.com/search?country=AU&state=Queensland&universityid=12&type=events","device":"web_portal","version":4}',
    'endpoint': 'getUnifiedSearch',
}

response = requests.post('https://api.hellorubric.com/', headers=headers, data=data)

try:
    results = response.json()
except json.JSONDecodeError:
    print("JSON decode error. Raw response:")
    print(response.text)
    exit()

print(json.dumps(results, indent=2))  # <-- Inspect the structure
with open("event_data.txt", 'w') as file:
    file.write(json.dumps(results,indent=2))

events = results.get("items", [])
print(f"Found {len(events)} events")

for event in events:
    name = event.get("name", "No name")
    time = event.get("formattedTime", "No time")
    location = event.get("location", "No location")
    description = event.get("description", "No description")
    
    print(f"📅 {name}")
    print(f"   🕒 {time}")
    print(f"   📍 {location}")
    print(f"   📝 {description}\n")