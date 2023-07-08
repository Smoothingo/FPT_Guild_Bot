import requests
from datetime import datetime, timedelta

API_KEY = 'bd168ed7-453d-456f-93a1-dc5e32676213'
GUILD_NAME = 'Water Hydras'

response = requests.get(f'https://api.hypixel.net/guild?key={API_KEY}&name={GUILD_NAME}')
data = response.json()

if data['success']:
    guild = data['guild']
    members = guild['members']
    weekly_fish_stats = {}
    for member in members:
        uuid = member['uuid']
        name = member['name']
        weekly_fish_stats[name] = 0
        retries = 0
        while retries < 3:
            try:
                mojang_data = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
                player_name = mojang_data['name']
                player_stats = requests.get(f'https://api.hypixel.net/player?key={API_KEY}&name={player_name}').json()
                if player_stats['success']:
                    fishing_stats = player_stats['player']['stats']['SkyBlock']['collections']['FISHING']
                    weekly_fish = fishing_stats['total'] - fishing_stats['last_week']
                    weekly_fish_stats[name] = weekly_fish
                break
            except Exception as e:
                print(f"An error occurred while retrieving data for player with UUID {uuid}: {e}")
                retries += 1
        time.sleep(1)
    print(weekly_fish_stats)
else:
    print('An error occurred:', data['cause'])