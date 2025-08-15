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
    'details': '{"firstCall":true,"sortType":"date","desiredType":"events","limit":100,"offset":0,"sortDirection":"asc","searchQuery":"","eventsPeriodFilter":"All","countryCode":"AU","state":"Queensland","selectedUniversityId":"12","currentUrl":"https://campus.hellorubric.com/search?country=AU&state=Queensland&universityid=12&type=events","device":"web_portal","version":4}',
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
with open("event_data.json", 'w') as file:
    file.write(json.dumps(results,indent=2))

events = results.get("results", [])
print(f"Found {len(events)} events")

with open("results.json", "w") as file:
    json.dump(events, file, indent=2)

with open("pretty_event_data.txt", "w") as file:
    for event in events:
        title = event.get("title", "No title")
        month = event.get("month", "No time")
        day = event.get("day", "no day")
        societyname = event.get("societyname", "No location")
        price = event.get("info", "No description")
        
        print(f"📅 {title}")
        print(f"   🕒 {month} {day}")
        print(f"   📍 {societyname}")
        print(f"   📝 {price}\n")

        file.write(f"📅 {title}\n")
        file.write(f"   🕒 {month} {day}\n")
        file.write(f"   📍 {societyname}\n")
        file.write(f"   📝 {price}\n\n")