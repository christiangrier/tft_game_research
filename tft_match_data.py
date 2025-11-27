import json
from datetime import datetime
from typing import List, Dict, Optional
from tft_single_player import TFTAPIClient

def parse_data(data_file: str, match_id: str, target_puuid: str):
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

if __name__ == '__main__':
    parse_data('tft_data/raw_matches/', 'NA1_5412498804','794yOzNOG1yjUZEBWnQKY3YNUA2MswWi67bfTnM1q4iRbhdLWhFjD0aZGHAN3S4bN8ZcWFApxf4voQ')