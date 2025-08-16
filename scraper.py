import requests
import json
from openai import OpenAI
import yaml

# Load the API key from the YAML file
with open("uqlink.yml", 'r') as stream:
    try:
        yaml_data = yaml.safe_load(stream)
        # Ensure that the 'ai_api' key exists and is not empty
        if 'ai_api' in yaml_data and yaml_data['ai_api']:
            OPENAI_API_KEY = yaml_data['ai_api']
        else:
            raise ValueError("API key not found or is empty in uqlink.yml")
    except yaml.YAMLError as exc:
        print(exc)
        exit()

client = OpenAI(api_key=OPENAI_API_KEY)

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
    'user-agent': 'Mozilla/50 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
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

events = results.get("results", [])
print(f"Found {len(events)} events")

# Iterate through each event
for event in events:
    description = event.get("description", "")
    if "food" in description.lower():
        # If "food" is in the description, use the LLM to check if it's free
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Does the following event description mention free food? Respond with 'free' or 'not free'.\n\nDescription: {description}",
                    }
                ],
                model="gpt-3.5-turbo",
            )
            response_text = chat_completion.choices[0].message.content.strip().lower()
            if "free" in response_text:
                event["free_food"] = "free"
            else:
                event["free_food"] = "not free"
        except Exception as e:
            print(f"An error occurred while communicating with OpenAI: {e}")
            # Default to "not free" in case of an error
            event["free_food"] = "not free"
    else:
        # If "food" is not in the description, mark as "not free"
        event["free_food"] = "not free"

# Save the updated event data to event_data.json
with open("event_data.json", 'w') as file:
    json.dump(results, file, indent=2)

print("Event data has been updated with free food information.")
