import csv
from datetime import datetime, timedelta
import json
import requests
import pandas as pd
import asyncio

LOCAL_PATH = "fishing_data.csv"

# # List of player names to collect data for
# import requests

# API_KEY = 'bd168ed7-453d-456f-93a1-dc5e32676213'
# GUILD_NAME = 'Water Hydras'

# # List of player names to update
# import requests
# import time

# API_KEY = 'bd168ed7-453d-456f-93a1-dc5e32676213'
# GUILD_NAME = 'Water Hydras'

# # List of player names to update
player_names = ["Smoothingo"]

# response = requests.get(f'https://api.hypixel.net/guild?key={API_KEY}&name={GUILD_NAME}')
# data = response.json()

# if data['success']:
#     guild = data['guild']
#     members = guild['members']
#     for member in members:
#         uuid = member['uuid']
#         retries = 0
#         while retries < 3:
#             try:
#                 mojang_data = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
#                 player_names.append(mojang_data['name'])
#                 break
#             except Exception as e:
#                 print(f"An error occurred while retrieving data for player with UUID {uuid}: {e}")
#                 retries += 1
#                 time.sleep(1)
#     print(player_names)
# else:
#     print('An error occurred:', data['cause'])

# Get the current date and time
now = datetime.now()

# Calculate the date and time one week ago
one_week_ago = now - timedelta(days=7)

# Format the dates as strings
now_str = now.strftime("%Y-%m-%d %H:%M:%S")
one_week_ago_str = one_week_ago.strftime("%Y-%m-%d %H:%M:%S")

# Check if it's Sunday and if the current time is between 17:50 and 18:00
if now.weekday() == 6 and 17 <= now.hour < 18 and now.minute >= 50:
    # Create an empty list to store the data
    data_list = []

    for player_name in player_names:
        api_url = f"https://sky.shiiyu.moe/api/v2/profile/{player_name}"
        data = {}

        try:
            response = requests.get(api_url)
            data = json.loads(response.text)
        except Exception as e:
            print(f"An error occurred while retrieving data for player {player_name}: {e}")
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
                
        # Add the data to the list
        data_list.append([player_name, total_fished, now_str])
        print(f"Player: {player_name}, Total Fished: {total_fished}")

    # Create a DataFrame from the data list
    df = pd.DataFrame(data_list, columns=['Player Name', 'Total Fished', 'Last Updated'])

    # Write the DataFrame to a CSV file
    df.to_csv(LOCAL_PATH, index=False)

    # Add this line at the end of your code, after the last except block
    print("Base data has been successfully updated!")
else:
    # Read the base data from the CSV file
    try:
        df = pd.read_csv(LOCAL_PATH)
        base_data = df.set_index('Player Name').to_dict('index')
    except Exception as e:
        print(f"An error occurred while reading the base data from the CSV file: {e}")
        base_data = {}

    # Create an empty list to store the data
    data_list = []

    for player_name in player_names:
        api_url = f"https://sky.shiiyu.moe/api/v2/profile/{player_name}"
        data = {}

        try:
            response = requests.get(api_url)
            data = json.loads(response.text)
        except Exception as e:
            print(f"An error occurred while retrieving data for player {player_name}: {e}")
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
            weekly_total_fished = 0

        # Add the data to the list
        data_list.append([player_name, total_fished, now_str, weekly_total_fished])
        print(f"Player: {player_name}, Total Fished: {total_fished}, Weekly Total Fished: {weekly_total_fished}")

        # Create a DataFrame from the data list
        df = pd.DataFrame(data_list, columns=['Player Name', 'Total Fished', 'Last Updated', 'Weekly Total Fished'])

        # Write the DataFrame to a CSV file
        df.to_csv(LOCAL_PATH, index=False)

        # Add this line at the end of your code, after the last except block
        print("Weekly data has been successfully updated!")