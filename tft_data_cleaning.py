import json
import sys
from typing import List, Dict, Optional
from tft_match_data import data_collector_main
import pandas as pd

class TFTDataCleaner:

    def __init__(self):
        # self.file = file
        self.file = data_collector_main()
        

    def set_identifier(self, set_number: int = 16):
        # with open(self.file, 'r') as f:
        #     file = json.load(f)
        data = []
        for match in self.file[0]:
            if match['tft_set_number'] != set_number:
                del match
            else:
                data.append(match)
        set_corrected = self.file
        # with open(set_corrected, 'w') as f:
        #     json.dump(data, f, indent=2)
        filename = self.file[1]
        
        return data, filename

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

        rows = []
        for record in match_data:
            row = {
                'riotIdGameName': record['riotIdGameName'],
                'match_id': record['match_id'],
                'placement': record['placement']
            }
            
            # Add units (up to 10 units with 3 items each)
            for i, unit in enumerate(record['units'], 1):
                row[f'unit_{i}_character_id'] = unit['character_id']
                row[f'unit_{i}_star_level'] = unit['star_level']
                
                # Add items for this unit
                items = unit['items']
                row[f'unit_{i}_item_1'] = items[0] if len(items) > 0 else None
                row[f'unit_{i}_item_2'] = items[1] if len(items) > 1 else None
                row[f'unit_{i}_item_3'] = items[2] if len(items) > 2 else None
            
            # Add traits
            for i, trait in enumerate(record['traits'], 1):
                row[f'trait_{i}_name'] = trait['name']
                row[f'trait_{i}_num_units'] = trait['num_units']
                row[f'trait_{i}_tier'] = trait['tier']
            
            rows.append(row)

        df = pd.DataFrame(rows)
        return df

    def placement(self, match_data: List):
        data = []
        for match in match_data:
            placement = match["placement"]
            data.append(placement)
        return data

        

def main():
    # cleaner = TFTDataCleaner('tft_data/parsed_matches/100T DishsoapNA2_NA1_5432018735_10.json')
    cleaner = TFTDataCleaner()
    set_id = cleaner.set_identifier()
    top_4_matches = cleaner.top_4(set_id[0])
    cleaned_file_json = 'tft_data/cleaned_matches/' + set_id[1] + '.json'
    print(f"Saving Cleaned Match Data to {cleaned_file_json}")
    with open(cleaned_file_json, 'w') as f:
        json.dump(top_4_matches, f, indent=2)
    dataframe = cleaner.dataframe_prep(top_4_matches)
    csv = 'tft_data/cleaned_csv/' + set_id[1] + '.csv'
    dataframe.to_csv(csv)

if __name__ == "__main__":
    main()