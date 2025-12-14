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
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except:
            print('Request has timed out')

    def get_region_routing(self, platform: str) -> str:
        for region, platforms in self.Regions.items():
            if platform.lower() in platforms:
                return region
        raise ValueError(f"Unknown {platform}")

    def get_challenger_league(self, platform: str):
        url = f'https://{platform}.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT'
        challengers = self.make_request(url)
        challenger_puuids = []
        for challenger in challengers['entries']:
            each_challenger = challenger['puuid']
            challenger_puuids.append(each_challenger)
        return challenger_puuids

    def get_gm_league(self, platform: str):
        url = f'https://{platform}.api.riotgames.com/tft/league/v1/grandmaster?queue=RANKED_TFT'
        gms = self.make_request(url)
        gm_puuids = []
        for gm in gms['entries']:
            each_challenger = gm['puuid']
            gm_puuids.append(each_challenger)
        return gm_puuids

    def get_match_ids(self, puuid: List, platform: str, count: int = 1, start: int = 0):
        region = self.get_region_routing(platform)
        match_ids = []
        for player in puuid:
            url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{player}/ids?start={start}&count={count}"
            match_id = self.make_request(url)
            if match_id not in match_ids:
                match_ids.append(match_id)
        flat_match_ids = [ids for match_id in match_ids for ids in match_id]
        return flat_match_ids

    def get_multi_match_data(self, match_id: List, platform: str):
        region = self.get_region_routing(platform)
        filepath = f'test/tft_data/raw_matches/{match_id[0]}_{match_id[-1]}_{len(match_id)}.json'
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
    challengers = client.get_challenger_league('na1')
    gms = client.get_gm_league('na1')
    # print(gms)
    match_ids = client.get_match_ids(challengers, 'na1')
    # print(match_ids)
    client.get_multi_match_data(match_ids, 'na1')