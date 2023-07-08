import csv
from datetime import datetime, timedelta
import json

import pandas as pd
import asyncio
import time
import requests

player_names = []
API_KEY = 'bd168ed7-453d-456f-93a1-dc5e32676213'
GUILD_NAME = 'Water Hydras'
LOCAL_PATH = 'fishing_data.csv'
response = requests.get(f'https://api.hypixel.net/guild?key={API_KEY}&name={GUILD_NAME}')
data = response.json()

if data['success']:
    guild = data['guild']
    members = guild['members']
    for member in members:
        uuid = member['uuid']
        retries = 0
        while retries < 5:
            try:
                mojang_data = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
                player_names.append(mojang_data['name'])
                break
            except Exception as e:
                print(f"An error occurred while retrieving data for player with UUID {uuid}: {e}")
                retries += 1
                if retries == 5:
                    response = input("Do you want to retry this player again? (y/n): ")
                    if response.lower() == 'y':
                        retries = 0
    print(player_names)
else:
    print('An error occurred:', data['cause'])

# Create a dictionary to store the base data
base_data = {}

# Read the base data from the CSV file
try:
    df = pd.read_csv(LOCAL_PATH)
    base_data = df.set_index('Player Name').to_dict('index')
except Exception as e:
    print(f"An error occurred while reading the base data from the CSV file: {e}")

# Create an empty list to store the data
data_list = []

# Get the current time
now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

for player_name in player_names:
    api_url = f"https://sky.shiiyu.moe/api/v2/profile/{player_name}"
    data = {}

    retries = 0
    while retries < 5:
        try:
            response = requests.get(api_url)
            data = json.loads(response.text)
            break
        except Exception as e:
            print(f"An error occurred while retrieving data for player {player_name}: {e}")
            retries += 1
            if retries == 5:
                response = input("Do you want to retry this player again? (y/n): ")
                if response.lower() == 'y':
                    retries = 0

    if "profiles" not in data:
        print(f"No profiles found for player {player_name}")
        continue

    total_fished = 0

    for profile in data["profiles"]:
        if "stats" in data["profiles"][profile]["raw"]:
            stats = data["profiles"][profile]["raw"]["stats"]
            items_fished = stats.get("items_fished", 0)
            treasures_fished = stats.get("treasures_fished", 0)
            large_treasures_fished = stats.get("large_treasures_fished", 0)
            sea_creatures_killed = stats.get("pet_milestone_sea_creatures_killed", 0)
            total_fished += items_fished + treasures_fished + large_treasures_fished + sea_creatures_killed

    # Calculate the weekly total fished items using the base data
    if player_name in base_data:
        total_fished_one_week_ago = base_data[player_name]['Total Fished']
        weekly_total_fished = total_fished - total_fished_one_week_ago
    else:
        total_fished_one_week_ago = 0
        weekly_total_fished = 0

    # Add the data to the list
    data_list.append([player_name, total_fished_one_week_ago, total_fished, weekly_total_fished, now_str])
    print(f"Player: {player_name}, Total Fished: {total_fished}, Total Fished One Week Ago: {total_fished_one_week_ago}, Weekly Total Fished: {weekly_total_fished}")

# Create a DataFrame from the data list
df = pd.DataFrame(data_list, columns=['Player Name', 'Total Fished One Week Ago', 'Total Fished', 'Weekly Total Fished', 'Last Updated'])

# Write the DataFrame to a CSV file
df.to_csv(LOCAL_PATH, index=False)

# Add this line at the end of your code, after the last except block
print("Weekly data has been successfully updated!")