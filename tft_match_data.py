import json
from datetime import datetime
from typing import List, Dict, Optional

from dotenv import load_dotenv
from tft_api_client import TFTAPIClient

class TFTDataCollector:

    def __init__(self, api_key: str, platform: str):
        self.client = TFTAPIClient(api_key)
        self.platform = platform

    def get_puuid_by_summoner(self, name: str, platform: str):
        splits = name.split('#')
        gamename = splits[0]
        tagline = splits[1]
        summoner = self.client.get_puuid(gamename, tagline, platform)
        return summoner['puuid']

    def collect_match_ids(self, puuid: str, count: int = 1) -> List[str]:
        match_ids = self.client.get_match_ids(puuid, self.platform, count)
        return match_ids

    def collect_match_data(self, match_ids, collect_raw_data: bool = True):
        if len(match_ids) > 1:
            match_data = self.client.get_multi_match_data(match_ids, self.platform)
        else:
            match_data = self.client.get_single_match_data(match_ids[0], self.platform)

        return match_data

    def parse_data(self, data_file: str, match_id: str, target_puuid: str):
        # Need to adjust function for processing. 
        file = f"{data_file}{match_id}.json"

        with open(file, 'r') as f:
            match_data = json.load(f)

        info = match_data['info']

        player_data = None
        for participant in info['participants']:
            if participant['puuid'] == target_puuid:
                player_data = participant
                break
        
        if not player_data:
            raise ValueError(f"Player with PUUID {target_puuid} not found in match")

        units = []
        for unit in player_data.get('units', []):
            units.append({
                'character_id': unit['character_id'],
                'tier': unit['tier'],
                'items': unit.get('itemNames', []),
                'rarity': unit['rarity']
            })

        traits = []
        for trait in player_data.get('traits', []):
            if trait['tier_current'] > 0:  # Only active traits
                traits.append({
                    'name': trait['name'],
                    'num_units': trait['num_units'],
                    'tier': trait['tier_current']
                })
        parsed = {
            'match_id': match_data['metadata']['match_id'],
            # 'game_datetime': datetime.fromtimestamp(info['game_datetime'] / 1000),
            'game_length': info['game_length'],
            'game_version': info['game_version'],
            'tft_set_number': info['tft_set_number'],
            'queue_id': info['queue_id'],
            'placement': player_data['placement'],
            'level': player_data['level'],
            'last_round': player_data['last_round'],
            'players_eliminated': player_data['players_eliminated'],
            'gold_left': player_data['gold_left'],
            'time_eliminated': player_data['time_eliminated'],
            'total_damage_to_players': player_data['total_damage_to_players'],
            'units': units,
            'traits': traits,
            'companion': player_data.get('companion', {})
        }
        parsed_file = f'tft_data/parsed_matches/{match_id}.json'
        
        if units:
            with open(parsed_file, 'w') as f:
                json.dump(parsed, f, indent=2)

        # return {
        #     'match_id': match_data['metadata']['match_id'],
            # 'game_datetime': datetime.fromtimestamp(info['game_datetime'] / 1000),
        #     'game_length': info['game_length'],
        #     'game_version': info['game_version'],
        #     'tft_set_number': info['tft_set_number'],
        #     'queue_id': info['queue_id'],
        #     'placement': player_data['placement'],
        #     'level': player_data['level'],
        #     'last_round': player_data['last_round'],
        #     'players_eliminated': player_data['players_eliminated'],
        #     'gold_left': player_data['gold_left'],
        #     'time_eliminated': player_data['time_eliminated'],
        #     'total_damage_to_players': player_data['total_damage_to_players'],
        #     'units': units,
        #     'traits': traits,
        #     'companion': player_data.get('companion', {})
        # }

def main():
    #Need to add processing information
    load_dotenv()

if __name__ == '__main__':
    main()
    # parse_data('tft_data/raw_matches/', 'NA1_5412498804','794yOzNOG1yjUZEBWnQKY3YNUA2MswWi67bfTnM1q4iRbhdLWhFjD0aZGHAN3S4bN8ZcWFApxf4voQ')