import os
from dotenv import load_dotenv
import requests
from typing import List, Dict, Optional
from datetime import datetime
import json
import time
from collections import deque

class RateLimiter:
    
    def __init__(self, max_requests_per_second: int = 20, max_requests_per_two_minutes: int = 100):
        self.max_per_second = max_requests_per_second
        self.max_per_two_minutes = max_requests_per_two_minutes
        
        self.requests_last_second = deque()
        self.requests_last_two_minutes = deque()
    

    def wait_if_needed(self):
        current_time = time.time()
        
        self._clean_old_requests(current_time)

        if len(self.requests_last_second) >= self.max_per_second:
            oldest_request = self.requests_last_second[0]
            wait_time = 1.0 - (current_time - oldest_request)
            if wait_time > 0:
                print(f"Rate limit approaching (1s window). Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                current_time = time.time()
                self._clean_old_requests(current_time)
        
        if len(self.requests_last_two_minutes) >= self.max_per_two_minutes:
            oldest_request = self.requests_last_two_minutes[0]
            wait_time = 120.0 - (current_time - oldest_request)
            if wait_time > 0:
                print(f"Rate limit approaching (2m window). Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                current_time = time.time()
                self._clean_old_requests(current_time)
        
        self.requests_last_second.append(current_time)
        self.requests_last_two_minutes.append(current_time)

    
    def _clean_old_requests(self, current_time: float):
        while self.requests_last_second and current_time - self.requests_last_second[0] > 1.0:
            self.requests_last_second.popleft()
        
        while self.requests_last_two_minutes and current_time - self.requests_last_two_minutes[0] > 120.0:
            self.requests_last_two_minutes.popleft()


class TFTAPIClient:

    Regions = {
        'americas': ['na1', 'br1', 'la1', 'la2'],
        'asia': ['kr', 'jp1'],
        'europe': ['eun1', 'euw1', 'tr1', 'ru'],
        'sea': ['oc1', 'ph2', 'sg2', 'th2', 'tw2', 'vn2']
    }

    def __init__(self, rate_limit_buffer: float = 0.9):
        load_dotenv()
        self.api_key = os.getenv('RIOT_API_KEY')

        max_per_second = int(20 * rate_limit_buffer)
        max_per_two_minutes = int(100 * rate_limit_buffer)
        self.rate_limiter = RateLimiter(max_per_second, max_per_two_minutes)


    def make_request(self, url: str) -> Dict:
        self.rate_limiter.wait_if_needed()
        headers = {
            "X-Riot-Token": self.api_key
        }
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 10))
                print(f"Rate limited by API. Waiting {retry_after}s...")
                time.sleep(retry_after)
                return self.make_request(url)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"Resource not found: {url}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise


    def get_region_routing(self, platform: str) -> str:
        for region, platforms in self.Regions.items():
            if platform.lower() in platforms:
                return region
        raise ValueError(f"Unknown {platform}")


    def get_challenger_league(self, platform: str):
        url = f'https://{platform}.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT'
        challengers = self.make_request(url)
        challenger_puuids = [entry['puuid'] for entry in challengers['entries']]
        return challenger_puuids


    def get_gm_league(self, platform: str):
        url = f'https://{platform}.api.riotgames.com/tft/league/v1/grandmaster?queue=RANKED_TFT'
        gms = self.make_request(url)
        gm_puuids = []
        gm_puuids = [entry['puuid'] for entry in gms['entries']]
        return gm_puuids


    def get_match_ids(self, puuids: List[str], platform: str, count: int = 1, start: int = 0) -> List[str]:
        region = self.get_region_routing(platform)
        match_ids = set()
        total_players = len(puuids)
        for idx, player in enumerate(puuids, 1):
            url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{player}/ids?start={start}&count={count}"
            
            try:
                player_matches = self.make_request(url)
                match_ids.update(player_matches)
                
                if idx % 10 == 0: 
                    print(f"Processed {idx}/{total_players} players. Found {len(match_ids)} unique matches.")
                    
            except Exception as e:
                print(f"Failed to get matches for player {idx}/{total_players}: {e}")
                continue
        
        print(f"Total unique matches found: {len(match_ids)}")
        return list(match_ids)


    def get_multi_match_data(self, match_ids: List, platform: str):
        region = self.get_region_routing(platform)
        filepath = f'tft_data/raw_matches/{match_ids[0]}_{match_ids[-1]}_{len(match_ids)}.json'
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = []
        total_matches = len(match_ids)
        for idx, match in enumerate(match_ids, 1):
            url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match}"
            
            try:
                match_data = self.make_request(url)
                data.append(match_data)
                print(f'Fetched match data for {match} ({idx}/{total_matches})')

            except Exception as e:
                print(f"Failed to get data for match {match}: {e}")
                continue

        print(f"Saving {len(data)} matches to {filepath}")
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