# TFT Riot Games API Client

A Python client for collecting Team Fight Tactics match data from the Riot Games API for machine learning projects.

## Features

- ✅ Complete TFT API wrapper
- ✅ Match history and detailed match data retrieval
- ✅ Automatic data parsing and storage
- ✅ Handing of rate limiting for maximum output 

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` | Get PUUID from Riot ID |
| `/tft/summoner/v1/summoners/by-puuid/{puuid}` | Get summoner data |
| `/tft/match/v1/matches/by-puuid/{puuid}/ids` | Get match history |
| `/tft/match/v1/matches/{matchId}` | Get match details |
| `//tft/league/v1/challenger` | Get challengers players PUUID |
| `/tft/league/v1/grandmaster` | Get grandmasters players PUUID |

## Rate Limiting 

- Development API Key: 20 requests per second, 100 requests per 2 minutes
- The client implements automatic rate limiting with a default 1.2s delay between requests
- For production use, apply for a Personal or Production API key

## Regional Routing

The API uses regional routing. Supported regions:

- Americas: NA1, BR1, LA1, LA2
- Asia: KR, JP1
- Europe: EUN1, EUW1, TR1, RU
- SEA: OC1, PH2, SG2, TH2, TW2, VN2


## Resources

- [Riot Games API Documentation](https://developer.riotgames.com/docs/tft)


## License

MIT License
