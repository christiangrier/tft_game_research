import json
from datetime import datetime
from typing import List, Dict, Optional
from tft_leagues_api_client import TFTAPIClient

class TFTDataCollector:

    def __init__(self, platform: str):
        self.client = TFTAPIClient()
        self.platform = platform

    def get_puuids(self):
        summoner = self.client.get_gm_league(self.platform)
        return summoner

    def collect_match_ids(self, puuid: str, count: int = 5) -> List[str]:
        match_ids = self.client.get_match_ids(puuid, self.platform, count)
        return match_ids

    def collect_match_data(self, match_ids, collect_raw_data: bool = True):
        match_data = self.client.get_multi_match_data(match_ids, self.platform)
        return match_data

    def parse_data(self, match_data):
        data = []
        for match in match_data:
            info = match['info']
            metadata = match['metadata']
            
            for player in info['participants']:
                units = []
                for unit in player['units']:
                    units.append({
                        'character_id': unit['character_id'],
                        'star_level': unit['tier'],
                        'items': unit.get('itemNames', [])
                    })
                
                traits = []
                for trait in player['traits']:
                    if trait['tier_current'] > 0: 
                        traits.append({
                            'name': trait['name'],
                            'num_units': trait['num_units'],
                            'tier': trait['tier_current']
                        })
                
                player_data = {
                    'match_id': metadata['match_id'],
                    'riotIdGameName': player['riotIdGameName'],
                    'game_datetime': datetime.fromtimestamp(info['game_datetime'] / 1000).isoformat(),
                    'game_length': info['game_length'],
                    'game_version': info['game_version'],
                    'tft_set_number': info['tft_set_number'],
                    'queue_id': info['queue_id'],
                    'placement': player['placement'],
                    'level': player['level'],
                    'last_round': player['last_round'],
                    'players_eliminated': player['players_eliminated'],
                    'gold_left': player['gold_left'],
                    'time_eliminated': player['time_eliminated'],
                    'total_damage_to_players': player['total_damage_to_players'],
                    'units': units,
                    'traits': traits,
                    'companion': player.get('companion', {})
                }
                data.append(player_data)        
        return data

def data_collector_main(platform: str = 'na1', count: int = 1):

    collector = TFTDataCollector(platform)
    puuid = collector.get_puuids()
    match_ids = collector.collect_match_ids(puuid[:10], count)
    match_data = collector.collect_match_data(match_ids)
    print(match_data)
    parsed_data = collector.parse_data(match_data)
    filename = f'{match_ids[0]}_{match_ids[-1]}_{len(parsed_data)}'
    parsed_file = 'test/tft_data/parsed_matches/' + filename + '.json'
    print(f"Saving Parsed Match Data to {parsed_file}")
    with open(parsed_file, 'w') as f:
        json.dump(parsed_data, f, indent=2)
    return parsed_data, filename


if __name__ == '__main__':
    data_collector_main('na1')