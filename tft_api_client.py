import os
from dotenv import load_dotenv
import requests
from typing import List, Dict, Optional
from datetime import datetime
import json

class TFTAPIClient:
    load_dotenv()
    api_key = os.getenv('RIOT_API_KEY')

    Regions = {
        'americas': ['na1', 'br1', 'la1', 'la2'],
        'asia': ['kr', 'jp1'],
        'europe': ['eun1', 'euw1', 'tr1', 'ru'],
        'sea': ['oc1', 'ph2', 'sg2', 'th2', 'tw2', 'vn2']
    }

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('RIOT_API_KEY')


    def make_request(self, url: str) -> Dict:
        headers = {
            "X-Riot-Token": self.api_key
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def get_region_routing(self, platform: str) -> str:
        for region, platforms in self.Regions.items():
            if platform.lower() in platforms:
                return region
        raise ValueError(f"Unknown {platform}")

    def get_puuid(self, gamename: str, tagline: str, platform: str) -> str:
        region = self.get_region_routing(platform)
        url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gamename}/{tagline}"
        summoner = self.make_request(url)
        puuid = next(iter(summoner.values()))
        return str(puuid)

    def get_match_ids(self, puuid: str, platform: str, count: int = 1, start: int = 0):
        region = self.get_region_routing(platform)
        url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        match_id = self.make_request(url)
        return match_id

    def get_single_match_data(self, match_id: str, platform: str):
        region = self.get_region_routing(platform)
        url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
        match_data = self.make_request(url)
        print("Fetching match data...")
        filepath = f'tft_data/raw_matches/{match_id}.json'
        print(f"Saving Match Data to {filepath}")
        with open(filepath, 'w') as f:
            json.dump(match_data, f, indent=2)
        return match_data

    def get_multi_match_data(self, match_id: List, platform: str):
        region = self.get_region_routing(platform)
        # filepath = f'tft_data/raw_matches/{match_id[0]}_{match_id[-1]}_{len(match_id)}.json'
        filepath = f'tft_data/raw_matches/{len(match_id)}.json'
        data = []
        for match in match_id:
            url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match}"
            match_data = self.make_request(url)
            print(f'Fetched match data for {match}')
            data.append(match_data)
        print(f"Saving Match Data to {filepath}")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return data



if __name__ == "__main__":
    client = TFTAPIClient()

    print("Fetching summoner data...")
    puuid = client.get_puuid('Flancy', '1113', 'na1')
    print(puuid)
    print("Fatching match ids...")
    match_id = client.get_match_ids(puuid, 'na1', 10)
    print(match_id)
    # client.get_single_match_data(match_id, 'na1')
    client.get_multi_match_data(match_id, 'na1')

