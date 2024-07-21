import requests

# Provide ID of a game
# game_id = 1145360 # Hades
game_id = 1086940 # Hades

# Steam Web API URL
url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"

response = requests.get(url)
data = response.json()

if data[str(game_id)]["success"]:
    game_details = data[str(game_id)]["data"]
    print(game_details)
else:
    print(f"Failed to fetch game details for {game_id}")
