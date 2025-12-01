import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from tft_api_client import TFTAPIClient

class TFTDataCollector:

    def __init__(self):
        self.client = TFTAPIClient()

    def get_puuid_by_summoner(self, name: str, platform: str):
        splits = name.split('#')
        gamename = splits[0]
        tagline = splits[1]
        summoner = self.client.get_puuid(gamename, tagline, platform)
        # print(summoner)
        return summoner

    def collect_match_ids(self, puuid: str, platform: str, count: int = 1) -> List[str]:
        match_ids = self.client.get_match_ids(puuid, platform, count)
        # print(match_ids)
        return match_ids

    def collect_match_data(self, match_ids, platform: str, collect_raw_data: bool = True):
        if len(match_ids) > 1:
            match_data = self.client.get_multi_match_data(match_ids, platform)
        else:
            match_data = self.client.get_single_match_data(match_ids[0], platform)

        return match_data

    def parse_data(self, match_data, target_puuid: str):
        data = []
        for match in match_data:
            info = match['info']

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
            match_data_each = {
            'match_id': match_data[0]['metadata']['match_id'],
            'game_datetime': datetime.fromtimestamp(info['game_datetime'] / 1000).isoformat(),
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
            data.append(match_data_each)
        return data

def main(name: str = 'Flancy#1113', platform: str = 'na1'):

    collector = TFTDataCollector()

    player = name.replace('#','')

    puuid = collector.get_puuid_by_summoner(name, platform)
    match_ids = collector.collect_match_ids(puuid, platform, 3)
    match_data = collector.collect_match_data(match_ids, platform)
    parsed_data = collector.parse_data(match_data, puuid)

    parsed_file = f"tft_data/parsed_matches/{player}_{match_ids[0]}_{len(match_ids)}.json"
    with open(parsed_file, 'w') as f:
        json.dump(parsed_data, f, indent=2)


if __name__ == '__main__':
    main()