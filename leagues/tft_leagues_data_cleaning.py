import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from tft_leagues_match_data import data_collector_main
import pandas as pd

class TFTDataCleaner:

    def __init__(self, platform: str = 'na1', count: int = 5):
        """Initialize Data Cleaner"""
        self.file = data_collector_main(platform=platform, count=count)
        

    def set_identifier(self, set_number: int = 16):
        """Check for proper set number excludes any for fun gamemodes"""
        data = []
        for match in self.file[0]:
            if match['tft_set_number'] != set_number:
                del match
            else:
                data.append(match)
        filename = self.file[1]
        return data, filename


    def set_time_check(self, match_data: List):
        """Creates boundary for current patch time/date"""
        data = []
        # current_set_release = datetime(2025, 12, 9, 8, 15, 0) # patch 16.1b
        current_set_release = datetime(2025, 12, 16, 11, 30, 0) # patch 16.1c
        for match in match_data:
            match_datetime = datetime.fromisoformat(match['game_datetime'])
            if match_datetime < current_set_release:
                del match
            else:
                data.append(match)
        return data


    def top_4(self, match_data: List):
        data = []
        for match in match_data:
            placement = match['placement']
            if placement > 4:
                del match
            else:
                data.append(match)

        return data


    def dataframe_prep(self, match_data):
        """Prepares the list data to be turned in a dataframe for future analysis"""
        rows = []
        for record in match_data:
            row = {
                'riotIdGameName': record['riotIdGameName'],
                'match_id': record['match_id'],
                'placement': record['placement']
            }
            
            for i, unit in enumerate(record['units'], 1):
                row[f'unit_{i}_character_id'] = unit['character_id']
                row[f'unit_{i}_star_level'] = unit['star_level']
                
                items = unit['items']
                row[f'unit_{i}_item_1'] = items[0] if len(items) > 0 else None
                row[f'unit_{i}_item_2'] = items[1] if len(items) > 1 else None
                row[f'unit_{i}_item_3'] = items[2] if len(items) > 2 else None
            
            for i, trait in enumerate(record['traits'], 1):
                row[f'trait_{i}_name'] = trait['name']
                row[f'trait_{i}_num_units'] = trait['num_units']
                row[f'trait_{i}_tier'] = trait['tier']
            
            rows.append(row)

        df = pd.DataFrame(rows)
        return df
      

def main(platform: str, count: int):
    cleaner = TFTDataCleaner(platform=platform, count=count)
    set_id = cleaner.set_identifier()
    # print(set_id[0])
    set_time = cleaner.set_time_check(set_id[0])
    # top_4_matches = cleaner.top_4(set_time)
    # cleaned_file_json = 'tft_data/cleaned_matches/' + set_id[1] + '.json'
    # print(f"Saving Cleaned Match Data to {cleaned_file_json}")
    # with open(cleaned_file_json, 'w') as f:
    #     json.dump(top_4_matches, f, indent=2)
    # dataframe = cleaner.dataframe_prep(top_4_matches)
    dataframe = cleaner.dataframe_prep(set_time)
    csv = 'tft_data/cleaned_csv/' + set_id[1] + '.csv'
    dataframe.to_csv(csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TFT Data Cleaner')
    parser.add_argument('--platform', type=str, default='na1',
                        help='Platform (default: na1)')
    parser.add_argument('--count', type=int, default=5,
                        help='(default: count 5)')       

    args = parser.parse_args()
    main(platform=args.platform, count=args.count)