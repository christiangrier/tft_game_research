import json
import sys
from typing import List, Dict, Optional
from tft_match_data import data_collector_main

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
    cleaned_file = set_id[1]
    print(f"Saving Cleaned Match Data to {cleaned_file}")
    with open(cleaned_file, 'w') as f:
        json.dump(top_4_matches, f, indent=2)

if __name__ == "__main__":
    main()