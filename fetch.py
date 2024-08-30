import requests
import csv

# The base URL to send the POST request to
url = "https://client.warpcast.com/v2/feed-items"

# Initialize variables
authors = []
exclude_item_id_prefixes = []
latest_timestamp = None


# Function to fetch feed items
def fetch_feed_items(payload):
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


# Loop until exhaustion
while True:
    # Prepare the payload for the request
    payload = {
        "feedKey": "trending",
        "feedType": "default",
        "castViewEvents": [],
        "updateState": True
    }

    if latest_timestamp:
        payload.update({
            "olderThan": latest_timestamp,
            "latestMainCastTimestamp": latest_timestamp,
            "excludeItemIdPrefixes": exclude_item_id_prefixes
        })

    # Fetch feed items
    data = fetch_feed_items(payload)
    if not data:
        break
    # Stop if there are no more items
    if not data.get("result", {}).get("items"):
        break

    # Process the fetched items
    for item in data.get("result", {}).get("items", []):
        cast = item.get("cast", {})
        author = cast.get("author", {})

        # Add author to the list
        authors.append({
            "fid": author.get("fid"),
            "username": author.get("username"),
            "displayName": author.get("displayName"),
            "pfp": author.get("pfp", {}).get("url"),
            "followerCount": author.get("followerCount"),
            "followingCount": author.get("followingCount"),
            "location": author.get("profile", {}).get("location", {}).get("description")
        })

        # Track excludeItemIdPrefixes
        cast_hash = cast.get("hash", "")
        if len(cast_hash) > 10:
            exclude_item_id_prefixes.append(cast_hash[2:10])

    # Update latest timestamp for next request
    latest_timestamp = data.get("result", {}).get("latestMainCastTimestamp")

# Save the collected authors to a CSV file
with open('authors.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=authors[0].keys())
    writer.writeheader()
    writer.writerows(authors[:100])  # Save only the first 100 authors

print("Authors data saved to authors.csv")

# Print the excludeItemIdPrefixes for reference
print("\nFinal ExcludeItemIdPrefixes:")
print(exclude_item_id_prefixes)
