import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

class TFTDataCleaner:

    def __init__(self, file: str):
        self.file = file

    def set_identifier(self, set_number: int = 16):
        with open(self.file, 'r') as f:
            file = json.load(f)
        data = []
        for match in file:
            if match['tft_set_number'] != set_number:
                del match
            else:
                data.append(match)
        set_corrected = self.file
        with open(set_corrected, 'w') as f:
            json.dump(data, f, indent=2)
        
        return data

    def placement(self, match_data: List):
        data = []
        for match in match_data:
            placement = match["placement"]
            data.append(placement)
        return data

        
        

if __name__ == "__main__":

    cleaner = TFTDataCleaner('tft_data/parsed_matches/Flancy1113_NA1_5427084272_4.json')
    set_id = cleaner.set_identifier()
    placement = cleaner.placement(set_id)
    print(placement)