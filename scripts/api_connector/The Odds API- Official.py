#!/usr/bin/env python
# coding: utf-8

# In[1]:


######################


# In[2]:


##########################


# In[3]:


##########################


# In[4]:


import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import numpy as np

API_KEY = '442200d4267f89915aaa9c3024acebfe'  # Your actual API key
SPORTS = ['basketball_nba', 'baseball_mlb','americanfootball_nfl','icehockey_nhl']  # Add or remove sports as needed
REGIONS = 'us'  # Specify your region
BOOKMAKER = ['pinnacle','fanduel','draftkings']
MARKETS = 'h2h'  # Head to head market
ODDS_FORMAT = 'american'
DATE_FORMAT = 'iso'  # To get date in ISO format


# In[5]:


###The below will get the gameids for games listed in the sports section


# In[6]:


# Initialize game_ids dictionary
game_ids = {sport: [] for sport in SPORTS}

# Define today and tomorrow's date
today = datetime.now(tz=timezone.utc)
tomorrow = today + timedelta(days=2)

# Get the game ids for each sport
for sport in SPORTS:
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{sport}/odds', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'bookmaker': BOOKMAKER,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    })

    if odds_response.status_code != 200:
        print(f'Failed to get odds for {sport}: status_code {odds_response.status_code}, response body {odds_response.text}')
        continue

    odds_json = odds_response.json()

    # Store the game ids
    for event in odds_json:
        game_datetime = datetime.strptime(event['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
        # Check if the game is today or tomorrow
        if today.date() <= game_datetime.date() <= tomorrow.date():
            game_ids[sport].append(event['id'])


# In[7]:


print(game_ids)


# In[8]:


basketball_nba_df = pd.DataFrame(game_ids['basketball_nba'], columns=['GameID'])
baseball_mlb_df = pd.DataFrame(game_ids['baseball_mlb'], columns=['GameID'])
americanfootball_nfl_df = pd.DataFrame(game_ids['americanfootball_nfl'], columns=['GameID'])
icehockey_nhl_df = pd.DataFrame(game_ids['icehockey_nhl'], columns=['GameID'])


# In[9]:


def parse_data(data):
    events = []

    for bookmaker in data['bookmakers']:
        for market in bookmaker['markets']:
            for outcome in market['outcomes']:
                event = {
                    'player_name': outcome['description'],
                    'market': market['key'],
                    'line': outcome.get('point', None),  # Check if 'point' key exists
                    'over_under': outcome['name'],
                    'odds': outcome['price'],
                    'league': data['sport_title'],
                    'sport': data['sport_key'],
                    'bookmaker': bookmaker['title']
                }
                events.append(event)

    return pd.DataFrame(events)


# In[10]:


#######################
#The below gets all odds need for MLB Underdog Fantasy from Pinnacle, Fanduel, Draftkings
########################


# In[11]:


# Initialize an empty DataFrame to store all data
baseball_mlb_odds = pd.DataFrame()

for game_id in baseball_mlb_df['GameID']:
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/baseball_mlb/events/{game_id}/odds?apiKey=442200d4267f89915aaa9c3024acebfe&oddsFormat=american&markets=batter_hits,batter_total_bases,batter_runs_scored,batter_hits_runs_rbis,batter_singles,pitcher_strikeouts,batter_walks,pitcher_walks&bookmakers=draftkings,pinnacle,fanduel')

    if odds_response.status_code != 200:
        print(f'Failed to get odds for baseball_mlb and {game_id}: status_code {odds_response.status_code}, response body {odds_response.text}')
        continue

    odds_json = odds_response.json()
    df = parse_data(odds_json)  # assuming this function processes the JSON into a DataFrame
    baseball_mlb_odds = pd.concat([baseball_mlb_odds, df])

    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])

print(baseball_mlb_odds)
baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/all_odds_ind.csv")


# In[12]:


#Checks to see if the sport dataframe is empty. 
#If it is not empty, execute code. If it is empty, skip


# In[13]:


if not baseball_mlb_odds.empty:
    # Do some stuff when df is not empty
    print("DataFrame is not empty. Executing some code...")
    # Your code here
    #Separate the MLB odds into Pinnacle odds and DraftKings/Fanduel Odds

    # DataFrame where bookmaker is 'Pinnacle'
    pinnacle_baseball_mlb_odds = baseball_mlb_odds.loc[baseball_mlb_odds['bookmaker'] == 'Pinnacle']
    pinnacle_baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/Pinnacle/Odds.csv")

    # DataFrame where bookmaker is not 'Pinnacle'
    dkfd_baseball_mlb_odds = baseball_mlb_odds.loc[baseball_mlb_odds['bookmaker'] != 'Pinnacle']
    dkfd_baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/DraftKings:Fanduel/Odds.csv")
    
    #Reset Index, Calculate Implied Probability, Average Draftkings/Fanduel Lines

    # Reset the index
    pinnacle_baseball_mlb_odds = pinnacle_baseball_mlb_odds.reset_index(drop=True)
    dkfd_baseball_mlb_odds = dkfd_baseball_mlb_odds.reset_index(drop=True)

    #Calculate Implied Probability
    #Find the implied probability for each line and the assoicated odds
    pinnacle_baseball_mlb_odds['implied_probability'] = np.where(pinnacle_baseball_mlb_odds['odds'] < 0,
                                          -pinnacle_baseball_mlb_odds['odds'] / (-pinnacle_baseball_mlb_odds['odds'] + 100) * 100,
                                         100 / (pinnacle_baseball_mlb_odds['odds'] + 100) * 100)

    #Find the implied probability for each line and the assoicated odds
    dkfd_baseball_mlb_odds['implied_probability'] = np.where(dkfd_baseball_mlb_odds['odds'] < 0,
                                         -dkfd_baseball_mlb_odds['odds'] / (-dkfd_baseball_mlb_odds['odds'] + 100) * 100,
                                         100 / (dkfd_baseball_mlb_odds['odds'] + 100) * 100)

    #Send to file to look over
    dkfd_baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/DraftKings:Fanduel/Odds.csv")

    
    dkfd_baseball_mlb_odds['bookmaker'] = 'DraftKings/Fanduel'

    # # Group by player_name, market, line, over_under and calculate the mean of implied_probability
    dkfd_baseball_mlb_odds = dkfd_baseball_mlb_odds.groupby(['player_name', 'market', 'line', 'over_under'], as_index=False)['implied_probability'].mean()

    dkfd_baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/DraftKings:Fanduel/Odds.csv")

    
    # Assuming your dataframe is named 'all_data'
    dkfd_baseball_mlb_odds = dkfd_baseball_mlb_odds[dkfd_baseball_mlb_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 2]
    one_present_df = dkfd_baseball_mlb_odds[dkfd_baseball_mlb_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 1]

    dkfd_baseball_mlb_odds = dkfd_baseball_mlb_odds.reset_index(drop=True)
    dkfd_baseball_mlb_odds['bookmaker'] = 'Draftkings/Fanduel'
    dkfd_baseball_mlb_odds['league'] = 'MLB'


    dkfd_baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/DraftKings:Fanduel/Odds.csv")
    
    #Calculate no vig fair odds for pinncale odds and draftkings/fanduel odds
    def calculate_no_vig_prob(pinnacle_baseball_mlb_odds):
        pinnacle_baseball_mlb_odds['no_vig_prob'] = 0
        for i in range(0,len(pinnacle_baseball_mlb_odds)-1,2):
            pinnacle_baseball_mlb_odds.at[i, 'no_vig_prob'] = pinnacle_baseball_mlb_odds.iloc[i]['implied_probability']/(pinnacle_baseball_mlb_odds.iloc[i]['implied_probability'] + pinnacle_baseball_mlb_odds.iloc[i+1]['implied_probability'])
            pinnacle_baseball_mlb_odds.at[i+1, 'no_vig_prob'] = pinnacle_baseball_mlb_odds.iloc[i+1]['implied_probability']/(pinnacle_baseball_mlb_odds.iloc[i]['implied_probability'] + pinnacle_baseball_mlb_odds.iloc[i+1]['implied_probability'])
        return pinnacle_baseball_mlb_odds

    # # Calculate the 'No Vig Prob' column
    pinnacle_baseball_mlb_odds = calculate_no_vig_prob(pinnacle_baseball_mlb_odds)
    # both_present_df.dropna(inplace=True)
    pinnacle_baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/Pinnacle/Odds.csv")
    print(pinnacle_baseball_mlb_odds)

    def calculate_no_vig_prob(dkfd_baseball_mlb_odds):
        dkfd_baseball_mlb_odds['no_vig_prob'] = 0
        for i in range(0,len(dkfd_baseball_mlb_odds)-1,2):
            dkfd_baseball_mlb_odds.at[i, 'no_vig_prob'] = dkfd_baseball_mlb_odds.iloc[i]['implied_probability']/(dkfd_baseball_mlb_odds.iloc[i]['implied_probability'] + dkfd_baseball_mlb_odds.iloc[i+1]['implied_probability'])
            dkfd_baseball_mlb_odds.at[i+1, 'no_vig_prob'] = dkfd_baseball_mlb_odds.iloc[i+1]['implied_probability']/(dkfd_baseball_mlb_odds.iloc[i]['implied_probability'] + dkfd_baseball_mlb_odds.iloc[i+1]['implied_probability'])
        return dkfd_baseball_mlb_odds

    # Calculate the 'No Vig Prob' column
    dkfd_baseball_mlb_odds = calculate_no_vig_prob(dkfd_baseball_mlb_odds)
    #both_present_df.dropna(inplace=True)
    dkfd_baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/DraftKings:Fanduel/Odds.csv")

    print(dkfd_baseball_mlb_odds)
    
    #Concatenate dkfd_baseball_mlb_odds and pinnacle_baseball_mlb_odds. #Drop duplicate on playername, market
    #over_under, line. keeping pinnacle odds

    baseball_mlb_odds = pd.concat([pinnacle_baseball_mlb_odds, dkfd_baseball_mlb_odds])

    baseball_mlb_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/all_odds.csv")

    print(baseball_mlb_odds)
    
else:
    print("DataFrame is empty. Skipping the following code.")


# In[14]:


###############


# In[15]:


#################


# In[16]:


#######################
#The below gets all odds need for NBA Underdog Fantasy from Pinnacle, Fanduel, Draftkings
########################


# In[17]:


# Initialize an empty DataFrame to store all data
basketball_nba_odds = pd.DataFrame()

for game_id in basketball_nba_df['GameID']:
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{game_id}/odds?apiKey=442200d4267f89915aaa9c3024acebfe&oddsFormat=american&markets=player_points,player_rebounds,player_assists,player_threes,player_blocks,player_steals,player_points_rebounds_assists,player_points_rebounds,player_points_assists,player_rebounds_assists&bookmakers=draftkings,pinnacle,fanduel')

    if odds_response.status_code != 200:
        print(f'Failed to get odds for basketball_nba and {game_id}: status_code {odds_response.status_code}, response body {odds_response.text}')
        continue

    odds_json = odds_response.json()
    df = parse_data(odds_json)  # assuming this function processes the JSON into a DataFrame
    basketball_nba_odds = pd.concat([basketball_nba_odds, df])

    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])

print(basketball_nba_odds)


# In[18]:


#######################


# In[19]:


if not basketball_nba_odds.empty:
    # Do some stuff when df is not empty
    print("DataFrame is not empty. Executing some code...")
    # Your code here
    #Separate the NBA odds into Pinnacle odds and DraftKings/Fanduel Odds

    # DataFrame where bookmaker is 'Pinnacle'
    pinnacle_basketball_nba_odds = basketball_nba_odds.loc[basketball_nba_odds['bookmaker'] == 'Pinnacle']
    pinnacle_basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NBA/Pinnacle/Odds.csv")

    # DataFrame where bookmaker is not 'Pinnacle'
    dkfd_basketball_nba_odds = basketball_nba_odds.loc[basketball_nba_odds['bookmaker'] != 'Pinnacle']
    dkfd_basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NBA/DraftKings:Fanduel/Odds.csv")
    
    
    #Reset Index, Calculate Implied Probability, Average Draftkings/Fanduel Lines

    # Reset the index
    pinnacle_basketball_nba_odds = pinnacle_basketball_nba_odds.reset_index(drop=True)
    dkfd_basketball_nba_odds = dkfd_basketball_nba_odds.reset_index(drop=True)

    #Calculate Implied Probability
    #Find the implied probability for each line and the assoicated odds
    pinnacle_basketball_nba_odds['implied_probability'] = np.where(pinnacle_basketball_nba_odds['odds'] < 0,
                                         -pinnacle_basketball_nba_odds['odds'] / (-pinnacle_basketball_nba_odds['odds'] + 100) * 100,
                                         100 / (pinnacle_basketball_nba_odds['odds'] + 100) * 100)

    #Find the implied probability for each line and the assoicated odds
    dkfd_basketball_nba_odds['implied_probability'] = np.where(dkfd_basketball_nba_odds['odds'] < 0,
                                         -dkfd_basketball_nba_odds['odds'] / (-dkfd_basketball_nba_odds['odds'] + 100) * 100,
                                         100 / (dkfd_basketball_nba_odds['odds'] + 100) * 100)

    #Send to file to look over
    dkfd_basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/MLB/DraftKings:Fanduel/Odds.csv")
    
    
    
    dkfd_basketball_nba_odds['bookmaker'] = 'DraftKings/Fanduel'

    # # Group by player_name, market, line, over_under and calculate the mean of implied_probability
    dkfd_basketball_nba_odds = dkfd_basketball_nba_odds.groupby(['player_name', 'market', 'line', 'over_under'], as_index=False)['implied_probability'].mean()

    dkfd_basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NBA/DraftKings:Fanduel/Odds.csv")


    # Assuming your dataframe is named 'all_data'
    dkfd_basketball_nba_odds = dkfd_basketball_nba_odds[dkfd_basketball_nba_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 2]
    one_present_df = dkfd_basketball_nba_odds[dkfd_basketball_nba_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 1]

    dkfd_basketball_nba_odds = dkfd_basketball_nba_odds.reset_index(drop=True)
    dkfd_basketball_nba_odds['bookmaker'] = 'Draftkings/Fanduel'
    dkfd_basketball_nba_odds['league'] = 'NBA'


    dkfd_basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NBA/DraftKings:Fanduel/Odds.csv")

    #Calculate no vig fair odds for pinncale odds and draftkings/fanduel odds
    def calculate_no_vig_prob(pinnacle_basketball_nba_odds):
        pinnacle_basketball_nba_odds['no_vig_prob'] = 0
        for i in range(0,len(pinnacle_basketball_nba_odds)-1,2):
            pinnacle_basketball_nba_odds.at[i, 'no_vig_prob'] = pinnacle_basketball_nba_odds.iloc[i]['implied_probability']/(pinnacle_basketball_nba_odds.iloc[i]['implied_probability'] + pinnacle_basketball_nba_odds.iloc[i+1]['implied_probability'])
            pinnacle_basketball_nba_odds.at[i+1, 'no_vig_prob'] = pinnacle_basketball_nba_odds.iloc[i+1]['implied_probability']/(pinnacle_basketball_nba_odds.iloc[i]['implied_probability'] + pinnacle_basketball_nba_odds.iloc[i+1]['implied_probability'])
        return pinnacle_basketball_nba_odds

    # # Calculate the 'No Vig Prob' column
    pinnacle_basketball_nba_odds = calculate_no_vig_prob(pinnacle_basketball_nba_odds)
    # both_present_df.dropna(inplace=True)
    pinnacle_basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NBA/Pinnacle/Odds.csv")
    print(pinnacle_basketball_nba_odds)

    def calculate_no_vig_prob(dkfd_basketball_nba_odds):
        dkfd_basketball_nba_odds['no_vig_prob'] = 0
        for i in range(0,len(dkfd_basketball_nba_odds)-1,2):
            dkfd_basketball_nba_odds.at[i, 'no_vig_prob'] = dkfd_basketball_nba_odds.iloc[i]['implied_probability']/(dkfd_basketball_nba_odds.iloc[i]['implied_probability'] + dkfd_basketball_nba_odds.iloc[i+1]['implied_probability'])
            dkfd_basketball_nba_odds.at[i+1, 'no_vig_prob'] = dkfd_basketball_nba_odds.iloc[i+1]['implied_probability']/(dkfd_basketball_nba_odds.iloc[i]['implied_probability'] + dkfd_basketball_nba_odds.iloc[i+1]['implied_probability'])
        return dkfd_basketball_nba_odds

    # Calculate the 'No Vig Prob' column
    dkfd_basketball_nba_odds = calculate_no_vig_prob(dkfd_basketball_nba_odds)
    #both_present_df.dropna(inplace=True)
    dkfd_basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NBA/DraftKings:Fanduel/Odds.csv")

    print(dkfd_basketball_nba_odds)
    
    
    #Concatenate dkfd_baseball_mlb_odds and pinnacle_baseball_mlb_odds. #Drop duplicate on playername, market
    #over_under, line. keeping pinnacle odds

    basketball_nba_odds = pd.concat([pinnacle_basketball_nba_odds, dkfd_basketball_nba_odds])

    basketball_nba_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NBA/all_odds.csv")

    print(basketball_nba_odds)
    
else:
    print("DataFrame is empty. Skipping the following code.")


# In[20]:


######################


# In[21]:


################


# In[22]:


#######################
#The below gets all odds need for NHL Underdog Fantasy from Pinnacle, Fanduel, Draftkings
########################


# In[23]:


# Initialize an empty DataFrame to store all data
icehockey_nhl_odds = pd.DataFrame()

for game_id in icehockey_nhl_df['GameID']:
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/icehockey_nhl/events/{game_id}/odds?apiKey=442200d4267f89915aaa9c3024acebfe&oddsFormat=american&markets=player_points,player_assists,player_blocked_shots,player_shots_on_goal&bookmakers=draftkings,pinnacle,fanduel')

    if odds_response.status_code != 200:
        print(f'Failed to get odds for icehockey_nhl and {game_id}: status_code {odds_response.status_code}, response body {odds_response.text}')
        continue

    odds_json = odds_response.json()
    df = parse_data(odds_json)  # assuming this function processes the JSON into a DataFrame
    icehockey_nhl_odds = pd.concat([icehockey_nhl_odds, df])

    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])

print(icehockey_nhl_odds)


# In[24]:


##################


# In[25]:


if not icehockey_nhl_odds.empty:
    # Do some stuff when df is not empty
    print("DataFrame is not empty. Executing some code...")
    # Your code here
    #Separate the NBA odds into Pinnacle odds and DraftKings/Fanduel Odds

    # DataFrame where bookmaker is 'Pinnacle'
    pinnacle_icehockey_nhl_odds = icehockey_nhl_odds.loc[icehockey_nhl_odds['bookmaker'] == 'Pinnacle']
    pinnacle_icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/Pinnacle/Odds.csv")

    # DataFrame where bookmaker is not 'Pinnacle'
    dkfd_icehockey_nhl_odds = icehockey_nhl_odds.loc[icehockey_nhl_odds['bookmaker'] != 'Pinnacle']
    dkfd_icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/DraftKings:Fanduel/Odds.csv")
    
        #Reset Index, Calculate Implied Probability, Average Draftkings/Fanduel Lines

    # Reset the index
    pinnacle_icehockey_nhl_odds = pinnacle_icehockey_nhl_odds.reset_index(drop=True)
    dkfd_icehockey_nhl_odds = dkfd_icehockey_nhl_odds.reset_index(drop=True)

    #Calculate Implied Probability
    #Find the implied probability for each line and the assoicated odds
    pinnacle_icehockey_nhl_odds['implied_probability'] = np.where(pinnacle_icehockey_nhl_odds['odds'] < 0,
                                         -pinnacle_icehockey_nhl_odds['odds'] / (-pinnacle_icehockey_nhl_odds['odds'] + 100) * 100,
                                         100 / (pinnacle_icehockey_nhl_odds['odds'] + 100) * 100)

    #Find the implied probability for each line and the assoicated odds
    dkfd_icehockey_nhl_odds['implied_probability'] = np.where(dkfd_icehockey_nhl_odds['odds'] < 0,
                                         -dkfd_icehockey_nhl_odds['odds'] / (-dkfd_icehockey_nhl_odds['odds'] + 100) * 100,
                                         100 / (dkfd_icehockey_nhl_odds['odds'] + 100) * 100)

    #Send to file to look over
    dkfd_icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/DraftKings:Fanduel/Odds.csv")
    
    dkfd_icehockey_nhl_odds['bookmaker'] = 'DraftKings/Fanduel'

    # # Group by player_name, market, line, over_under and calculate the mean of implied_probability
    dkfd_icehockey_nhl_odds = dkfd_icehockey_nhl_odds.groupby(['player_name', 'market', 'line', 'over_under'], as_index=False)['implied_probability'].mean()

    dkfd_icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/DraftKings:Fanduel/Odds.csv")


    # Assuming your dataframe is named 'all_data'
    dkfd_icehockey_nhl_odds = dkfd_icehockey_nhl_odds[dkfd_icehockey_nhl_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 2]
    one_present_df = dkfd_icehockey_nhl_odds[dkfd_icehockey_nhl_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 1]

    dkfd_icehockey_nhl_odds = dkfd_icehockey_nhl_odds.reset_index(drop=True)
    dkfd_icehockey_nhl_odds['bookmaker'] = 'Draftkings/Fanduel'
    dkfd_icehockey_nhl_odds['league'] = 'MLB'


    dkfd_icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/DraftKings:Fanduel/Odds.csv")

    
        #Calculate no vig fair odds for pinncale odds and draftkings/fanduel odds
    def calculate_no_vig_prob(pinnacle_icehockey_nhl_odds):
        pinnacle_icehockey_nhl_odds['no_vig_prob'] = 0
        for i in range(0,len(pinnacle_icehockey_nhl_odds)-1,2):
            pinnacle_icehockey_nhl_odds.at[i, 'no_vig_prob'] = pinnacle_icehockey_nhl_odds.iloc[i]['implied_probability']/(pinnacle_icehockey_nhl_odds.iloc[i]['implied_probability'] + pinnacle_icehockey_nhl_odds.iloc[i+1]['implied_probability'])
            pinnacle_icehockey_nhl_odds.at[i+1, 'no_vig_prob'] = pinnacle_icehockey_nhl_odds.iloc[i+1]['implied_probability']/(pinnacle_icehockey_nhl_odds.iloc[i]['implied_probability'] + pinnacle_icehockey_nhl_odds.iloc[i+1]['implied_probability'])
        return pinnacle_icehockey_nhl_odds

    # # Calculate the 'No Vig Prob' column
    pinnacle_icehockey_nhl_odds = calculate_no_vig_prob(pinnacle_icehockey_nhl_odds)
    # both_present_df.dropna(inplace=True)
    pinnacle_icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/Pinnacle/Odds.csv")
    print(pinnacle_icehockey_nhl_odds)

    def calculate_no_vig_prob(dkfd_icehockey_nhl_odds):
        dkfd_icehockey_nhl_odds['no_vig_prob'] = 0
        for i in range(0,len(dkfd_icehockey_nhl_odds)-1,2):
            dkfd_icehockey_nhl_odds.at[i, 'no_vig_prob'] = dkfd_icehockey_nhl_odds.iloc[i]['implied_probability']/(dkfd_icehockey_nhl_odds.iloc[i]['implied_probability'] + dkfd_icehockey_nhl_odds.iloc[i+1]['implied_probability'])
            dkfd_icehockey_nhl_odds.at[i+1, 'no_vig_prob'] = dkfd_icehockey_nhl_odds.iloc[i+1]['implied_probability']/(dkfd_icehockey_nhl_odds.iloc[i]['implied_probability'] + dkfd_icehockey_nhl_odds.iloc[i+1]['implied_probability'])
        return dkfd_icehockey_nhl_odds

    # Calculate the 'No Vig Prob' column
    dkfd_icehockey_nhl_odds = calculate_no_vig_prob(dkfd_icehockey_nhl_odds)
    #both_present_df.dropna(inplace=True)
    dkfd_icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/DraftKings:Fanduel/Odds.csv")

    print(dkfd_icehockey_nhl_odds)
    
    
    #Concatenate dkfd_baseball_mlb_odds and pinnacle_baseball_mlb_odds. #Drop duplicate on playername, market
    #over_under, line. keeping pinnacle odds

    icehockey_nhl_odds = pd.concat([pinnacle_icehockey_nhl_odds, dkfd_icehockey_nhl_odds])

    icehockey_nhl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/all_odds.csv")

    print(icehockey_nhl_odds)
    
    
else:
    print("DataFrame is empty. Skipping the following code.")


# In[26]:


#################


# In[27]:


#######################
#The below gets all odds need for NFL Underdog Fantasy from Pinnacle, Fanduel, Draftkings
########################


# In[28]:


# Initialize an empty DataFrame to store all data
americanfootball_nfl_odds = pd.DataFrame()

for game_id in americanfootball_nfl_df['GameID']:
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/events/{game_id}/odds?apiKey=442200d4267f89915aaa9c3024acebfe&oddsFormat=american&markets=player_pass_tds,player_pass_yds,player_pass_completions,player_pass_attempts,player_pass_interceptions,player_rush_yds,player_rush_attempts,player_receptions,player_reception_yds&bookmakers=draftkings,pinnacle,fanduel')

    if odds_response.status_code != 200:
        print(f'Failed to get odds for icehockey_nhl and {game_id}: status_code {odds_response.status_code}, response body {odds_response.text}')
        continue

    odds_json = odds_response.json()
    df = parse_data(odds_json)  # assuming this function processes the JSON into a DataFrame
    americanfootball_nfl_odds = pd.concat([americanfootball_nfl_odds, df])

    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])

print(americanfootball_nfl_odds)
americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/all_odds.csv")


# In[29]:


##################


# In[30]:


if not americanfootball_nfl_odds.empty:
    # Do some stuff when df is not empty
    print("DataFrame is not empty. Executing some code...")
    # Your code here
    #Separate the NFL odds into Pinnacle odds and DraftKings/Fanduel Odds

    # DataFrame where bookmaker is 'Pinnacle'
    pinnacle_americanfootball_nfl_odds = americanfootball_nfl_odds.loc[americanfootball_nfl_odds['bookmaker'] == 'Pinnacle']
    pinnacle_americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/Pinnacle/Odds.csv")

    # DataFrame where bookmaker is not 'Pinnacle'
    dkfd_americanfootball_nfl_odds = americanfootball_nfl_odds.loc[americanfootball_nfl_odds['bookmaker'] != 'Pinnacle']
    dkfd_americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/DraftKings:Fanduel/Odds.csv")
    
        #Reset Index, Calculate Implied Probability, Average Draftkings/Fanduel Lines

    # Reset the index
    pinnacle_americanfootball_nfl_odds = pinnacle_americanfootball_nfl_odds.reset_index(drop=True)
    dkfd_basketball_nba_odds = dkfd_basketball_nba_odds.reset_index(drop=True)

    #Calculate Implied Probability
    #Find the implied probability for each line and the assoicated odds
    pinnacle_americanfootball_nfl_odds['implied_probability'] = np.where(pinnacle_americanfootball_nfl_odds['odds'] < 0,
                                         -pinnacle_americanfootball_nfl_odds['odds'] / (-pinnacle_americanfootball_nfl_odds['odds'] + 100) * 100,
                                         100 / (pinnacle_americanfootball_nfl_odds['odds'] + 100) * 100)

    #Find the implied probability for each line and the assoicated odds
    dkfd_americanfootball_nfl_odds['implied_probability'] = np.where(dkfd_americanfootball_nfl_odds['odds'] < 0,
                                         -dkfd_americanfootball_nfl_odds['odds'] / (-dkfd_americanfootball_nfl_odds['odds'] + 100) * 100,
                                         100 / (dkfd_americanfootball_nfl_odds['odds'] + 100) * 100)


    #Send to file to look over
    dkfd_americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/DraftKings:Fanduel/Odds.csv")
    
    dkfd_americanfootball_nfl_odds['bookmaker'] = 'DraftKings/Fanduel'

    # # Group by player_name, market, line, over_under and calculate the mean of implied_probability
    dkfd_americanfootball_nfl_odds = dkfd_americanfootball_nfl_odds.groupby(['player_name', 'market', 'line', 'over_under'], as_index=False)['implied_probability'].mean()

    dkfd_americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NHL/DraftKings:Fanduel/Odds.csv")

    # Assuming your dataframe is named 'all_data'
    dkfd_americanfootball_nfl_odds = dkfd_americanfootball_nfl_odds[dkfd_americanfootball_nfl_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 2]
    one_present_df = dkfd_americanfootball_nfl_odds[dkfd_americanfootball_nfl_odds.groupby(['player_name', 'market', 'line'])['over_under'].transform('nunique') == 1]

    dkfd_americanfootball_nfl_odds = dkfd_americanfootball_nfl_odds.reset_index(drop=True)
    dkfd_americanfootball_nfl_odds['bookmaker'] = 'Draftkings/Fanduel'
    dkfd_americanfootball_nfl_odds['league'] = 'NFL'


    dkfd_americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/DraftKings:Fanduel/Odds.csv")


        #Calculate no vig fair odds for pinncale odds and draftkings/fanduel odds
    def calculate_no_vig_prob(pinnacle_americanfootball_nfl_odds):
        pinnacle_americanfootball_nfl_odds['no_vig_prob'] = 0
        for i in range(0,len(pinnacle_americanfootball_nfl_odds)-1,2):
            pinnacle_americanfootball_nfl_odds.at[i, 'no_vig_prob'] = pinnacle_americanfootball_nfl_odds.iloc[i]['implied_probability']/(pinnacle_americanfootball_nfl_odds.iloc[i]['implied_probability'] + pinnacle_americanfootball_nfl_odds.iloc[i+1]['implied_probability'])
            pinnacle_americanfootball_nfl_odds.at[i+1, 'no_vig_prob'] = pinnacle_americanfootball_nfl_odds.iloc[i+1]['implied_probability']/(pinnacle_americanfootball_nfl_odds.iloc[i]['implied_probability'] + pinnacle_americanfootball_nfl_odds.iloc[i+1]['implied_probability'])
        return pinnacle_americanfootball_nfl_odds

    # # Calculate the 'No Vig Prob' column
    pinnacle_americanfootball_nfl_odds = calculate_no_vig_prob(pinnacle_americanfootball_nfl_odds)
    # both_present_df.dropna(inplace=True)
    pinnacle_americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/Pinnacle/Odds.csv")
    print(pinnacle_americanfootball_nfl_odds)

    def calculate_no_vig_prob(dkfd_americanfootball_nfl_odds):
        dkfd_americanfootball_nfl_odds['no_vig_prob'] = 0
        for i in range(0,len(dkfd_americanfootball_nfl_odds)-1,2):
            dkfd_americanfootball_nfl_odds.at[i, 'no_vig_prob'] = dkfd_americanfootball_nfl_odds.iloc[i]['implied_probability']/(dkfd_americanfootball_nfl_odds.iloc[i]['implied_probability'] + dkfd_americanfootball_nfl_odds.iloc[i+1]['implied_probability'])
            dkfd_americanfootball_nfl_odds.at[i+1, 'no_vig_prob'] = dkfd_americanfootball_nfl_odds.iloc[i+1]['implied_probability']/(dkfd_americanfootball_nfl_odds.iloc[i]['implied_probability'] + dkfd_americanfootball_nfl_odds.iloc[i+1]['implied_probability'])
        return dkfd_americanfootball_nfl_odds

    # Calculate the 'No Vig Prob' column
    dkfd_americanfootball_nfl_odds = calculate_no_vig_prob(dkfd_americanfootball_nfl_odds)
    #both_present_df.dropna(inplace=True)
    dkfd_americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/DraftKings:Fanduel/Odds.csv")

    print(dkfd_americanfootball_nfl_odds)
    
    
    #Concatenate dkfd_baseball_mlb_odds and pinnacle_baseball_mlb_odds. #Drop duplicate on playername, market
    #over_under, line. keeping pinnacle odds

    americanfootball_nfl_odds = pd.concat([pinnacle_americanfootball_nfl_odds, dkfd_americanfootball_nfl_odds])

    americanfootball_nfl_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/NFL/all_odds.csv")

    print(americanfootball_nfl_odds)
    
    
    
else:
    print("DataFrame is empty. Skipping the following code.")


# In[31]:


##################


# In[32]:


######################


# In[33]:


all_sport_odds = pd.concat([americanfootball_nfl_odds, icehockey_nhl_odds,basketball_nba_odds,baseball_mlb_odds])
all_sport_odds = all_sport_odds.reset_index(drop=True)
all_sport_odds = all_sport_odds[['player_name','market','line','over_under','league','bookmaker','no_vig_prob']]
all_sport_odds.columns = ['Name', 'Line_Category', 'Line','Over_Under','League','Bookmaker','No_Vig_Probability']
all_sport_odds = all_sport_odds.sort_values(by='Name', ascending=True)
all_sport_odds = all_sport_odds.reset_index(drop=True)
#all_sport_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/all_sport_odds.csv")

all_sport_odds['Line_Category'].replace({
    'player_points': 'Points', 
    'player_assists': 'Assists',
    'player_rebounds': 'Rebounds',
    'player_three': '3-Pointers Made',
    'player_points_rebounds_assists': 'Pts + Rebs + Asts',
    'player_shots_on_goal':'Shots',
    'batter_hits':'Hits',
    'batter_hits_runs_rbis':'Hits + Runs + RBIs',
    'batter_runs_scored':'Runs',
    'batter_singles':'Singles',
    'batter_total_bases':'Total Bases',
    'batter_walks':'Batter Walks',
    'pitcher_strikeouts':'Strikeouts',
    'pitcher_walks':'Walks Allowed',
    'player_blocks':'Blocks',
    'player_points_assists':'Points + Assists',
    'player_points_rebounds':'Points + Rebounds',
    'player_rebounds_assists':'Rebounds + Assists',
    'player_shots_on_goal':'Shots',
    'player_steals':'Steals'
    
}, inplace=True)

all_sport_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/all_sport_odds.csv")

print(all_sport_odds)


# In[34]:


#Add in Tennis
#all_sport_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/all_sport_odds.csv")
tennis_odds = pd.read_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/Tennis/Draftkings/tennis_higherlower.csv")

all_sport_odds = pd.concat([all_sport_odds, tennis_odds])

all_sport_odds = all_sport_odds.reset_index(drop=True)
all_sport_odds = all_sport_odds.drop(columns=["Unnamed: 0"])

all_sport_odds.to_csv(r"/Users/danielbrown/Desktop/Underdog WebApp/TheOddsAPI/all_sport_odds.csv")


# #### At this point I have player prop odds for the NFL,NBA,NHL,MLB from pinnacle, draftkings,and fanduel
# 
