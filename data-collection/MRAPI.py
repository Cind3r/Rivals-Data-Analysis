import pandas as pd
import random
import requests
import json
import time
import numpy as np
from pandas import json_normalize
from requests.adapters import HTTPAdapter
import ast
import datetime
import os
import glob

class MRAPIClient:

    """
    A client for the MRAPI (My Rival API) to fetch player and team data.
    This class provides methods to interact with the MRAPI endpoints for retrieving player and team information. 
    You can find documentation for the MRAPI at https://docs.marvelrivalsapi.com/

    Attributes:
        api_key (str): The API key for authenticating with the MRAPI.
        request_params (dict): Parameters for the API requests. (e.g., season, page, limit, etc.) all set to default values
        request_params_boolean (dict): Boolean flags for enabling/disabling request parameters.  (all set to False by default)

    Methods:
        get_player_data(player_id): Fetches data for a specific player using their player ID.
        get_team_data(): Fetches data for a specific team using their team ID.
        build_url(api_version, endpoint, request_uid=None): Constructs the URL for the API request.
        get_data(api_version, endpoint, request_uid=None, season=None, page=None, limit=None, skip=None, gamemode=None, timestamp=None): Fetches data from the MRAPI using the specified API version and endpoint.
        set_request_params(season=None, page=None, limit=None, skip=None, gamemode=None, timestamp=None): Sets the request parameters for the MRAPI client.
        set_request_uid(request_uid): Sets the request UID for the MRAPI client.
        get_total_data(): Fetches total data from the MRAPI using the specified API version and endpoint.

    TODO:
        - Implement the randomizer for the player data to get a random player from the match data.
        - Implement the player data request for each player in the match data from the 'player' endpoint.
        - Add support for other endpoints (e.g., heroes, match-history).
        - Implement error handling for API requests.
        - Add more detailed documentation for each method.
        - Add support for different API versions (v1, v2).
        - Implement a caching mechanism to reduce API calls.
        
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://marvelrivalsapi.com/api/"
        self.request_uid = None
        self.api_versions = ["v1", "v2"] # defaults to v1 
        self.endpoint = None # current endpoint for the request
        self.endpoints = ['player', 'match', 'heroes', 'match-history']
        self.headers = {
            "x-api-key": self.api_key
        }

        # parameters for api/v2/Match, api/v1 has less params than listed here
        # check documentation for details on the default values
        # if request_params_boolean is false, the request param is not included in the request
        # the default values are just included here for reference 
        self.request_params = {
            "season": 2,                    # season to filter matches by, defaults to current season (2 as this file creation)
            "page": 1,                      # page number for pagination
            "limit": 40,                    # number of matches to return per page
            "skip": 20,                     # number of matches to skip (for pagination)
            "gamemode": 0,              # gamemode to filter matches by (0 = all, 1 = ranked, 2 = casual)
            "timestamp": 0              # timestamp to filter matches by, includes matches after the given timestamp
        }

        # turn request params on/off
        self.request_params_boolean = {
            "season": False,
            "page": False,
            "limit": False,
            "skip": False,
            "gamemode": False,
            "timestamp": False
        }

    # used to update request params
    def set_request_params(self, season=None, page=None, limit=None, skip=None, gamemode=None, timestamp=None):
        """
        Sets the request parameters for the MRAPI client.
        This method sets the base URL and headers for the API requests
        """
        if season is not None:
            print(f'\nSetting season... {season}')
            self.request_params["season"] = season
            self.request_params_boolean["season"] = True
        if page is not None:
            print(f'\nSetting page... {page}')
            self.request_params["page"] = page
            self.request_params_boolean["page"] = True
        if limit is not None:
            print(f'\nSetting limit... {limit}')
            self.request_params["limit"] = limit
            self.request_params_boolean["limit"] = True
        if skip is not None:
            print(f'\nSetting skip... {skip}')
            self.request_params["skip"] = skip
            self.request_params_boolean["skip"] = True
        if gamemode is not None:
            print(f'\nSetting gamemode... {gamemode}')
            self.request_params["gamemode"] = gamemode
            self.request_params_boolean["gamemode"] = True
        if timestamp is not None:
            print(f'\nSetting timestamp... {timestamp}')
            self.request_params["timestamp"] = timestamp
            self.request_params_boolean["timestamp"] = True


    def set_request_uid(self, request_uid):
        """
        Sets the request UID for the MRAPI client.
        
        request_uid (str): The unique identifier for the request (e.g. match_uid, player_uid).
        """
        print(f'Setting request UID... {request_uid}')
        self.request_uid = request_uid


    def set_request_endpoint(self, endpoint):
        """
        Sets the request endpoint for the MRAPI client.
        
        endpoint (str): The specific endpoint to access (e.g., "Player", "Match").
        """
        print(f'Setting endpoint... {endpoint}')

        if endpoint not in self.endpoints:
            raise ValueError(f"Invalid endpoint. Use one of the following: {self.endpoints}.")
        self.endpoint = endpoint


    # Builds the URL for the MRAPI client, only handles matchs and players for now
    def build_url(self, api_version, endpoint=None, request_uid=None):
        """
        Builds the URL for the MRAPI client.
        This method constructs the URL for the API requests using the base URL and request parameters.


        api_version (str): The version of the API to use (e.g., "v1", "v2").
        endpoint (str): The specific endpoint to access (e.g., "Player", "Match").

        """
        print('\nBuilding URL START...\n')

        # set the UID if not previously set
        if request_uid is not None:
            print(f'Updating request UID... {request_uid}')
            self.set_request_uid(request_uid)
        
        # set the endpoint if not previously set
        if endpoint is not None:
            print(f'Updating endpoint... {endpoint}')
            self.set_request_endpoint(endpoint)

        # check for valid enteries 
        if api_version not in ["v1", "v2"]:
            raise ValueError("Invalid API version. Use 'v1' or 'v2'.")
        
        if endpoint not in self.endpoints:
            raise ValueError(f"Invalid endpoint. Use one of the following: {self.endpoints}.")
        
        # build base url
        url = f"{self.base_url}{api_version}/"
        print(f'Building base URL... check: {url}')

        # This check if for when heroes is used as the endpoint, it does not require any parameters or uid
        if endpoint in ["match", "player"] and self.request_uid:
            url += f"{endpoint}/{self.request_uid}"
            print(f'Building URL with UID... check: {url}')

            query_params = []
            for param, value in self.request_params.items():
                if self.request_params_boolean.get(param, True):
                    query_params.append(f"{param}={value}")
            
            if query_params:
                url += "?" + "&".join(query_params)
                print(f'Adding query params... check: {url}')

        # structure of match-history is different, the query is before the final endpoint
        # e.g. https://marvelrivalsapi.com/api/v2/player/:query/match-history
        if endpoint == "match-history":

            url += f"player/{self.request_uid}/match-history"
            print(f'Building match-history URL... check: {url}')

            query_params = []
            for param, value in self.request_params.items():
                if self.request_params_boolean.get(param, True):
                    query_params.append(f"{param}={value}")
            
            if query_params:
                url += "?" + "&".join(query_params)
                print(f'Adding query params... check: {url}')

            print(f'Returning url... check: {url}')

        return url
    

    def get_data(self, api_version, endpoint=None, request_uid=None, season=None, page=None, limit=None, skip=None, gamemode=None, timestamp=None):
        """
        Fetches data from the MRAPI using the specified API version and endpoint.
        
        api_version (str): The version of the API to use (e.g., "v1", "v2").
        endpoint (str): The specific endpoint to access (e.g., "Player", "Match").
        request_uid (str): The unique identifier for the request (e.g. match_uid, player_uid).
        season (int): The season to filter matches by (optional).
        page (int): The page number for pagination (optional).
        limit (int): The number of matches to return per page (optional).
        skip (int): The number of matches to skip (for pagination) (optional).
        gamemode (int): The gamemode to filter matches by (optional).
        timestamp (int): The timestamp to filter matches by (optional).
        
        Returns:
            dict: The JSON response from the MRAPI.
        """

        print('Fetching data from MRAPI...')
        self.set_request_params(season, page, limit, skip, gamemode, timestamp)

        url = self.build_url(api_version, endpoint, request_uid)
        
        headers = {
            "x-api-key": self.api_key,
        }
        
        response = requests.get(url, headers=headers)
        print(f'response status code: {response.status_code}')
        print(f'response text: {response.text}')

        if response.status_code == 200:
            print('Data fetched successfully!')
            print(f'response data: {response.json()}')
            return response.json()
        
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")


    """
    Now we can create a function to gather the data how we need it for the analysis files. 

    Step 1: Request multiple pages from 'match-history' endpoint for a player
        - This will return a list of matches for the player, and the match_uids
        - We can then use this list of match_uids to request the match data from the 'match' endpoint
    
    Step 2: Request the match data for each match_uid from the 'match' endpoint
        - This will return a list of matches with all the data we need for the analysis
        - We can then use this data to create a dataframe and save it to a csv file
    
    Step 2.1: Randomly sample a player from the match data, then request a set of matches for that player other than the current match_uid (optional)
        - This will allow us to randomly sample data for players rather than having a constant player
        - This is better for data analysis as it will give us a more diverse set of data that isn't skewed by a single player

    Step 2.2: Request the player data for each player in the match data from the 'player' endpoint (optional)
        - This is where we can find the rank_history.[i].score_progression.total_score
        - This will give us another variable to predict outcomes with and create a model as `is_win` is not the best output variable to model with
        - SR gain/loss correlates strongly with performance but also game impact, so it can tell us more about the inner workings of a match

    Step 3: Create a dataframe from the match data and player data
        - This will give us a dataframe with all the data we need for the analysis
        - We can then save this dataframe to a csv file for cleaning

    Step 4: Use the DataCleaner class to clean the data
        - This will remove any unnecessary columns and rows from the dataframe
        - We can then save this dataframe to a csv file for analysis
    
    Step 5: Create a new dataframe which is a group aggregation of the match data based on teams (is_win) and match_uids
        - This will give us a dataframe with all the data we need for the analysis
        - We can then save this dataframe to a csv file for analysis
        - Will contain team total kills, dmg, healing, deaths, etc. as well as the roles. 
        
    """
    
    def get_total_data(self):
        """
        Fetches total data from the MRAPI using the specified API version and endpoint.
        
        This method will gather the data how we need it for the analysis files.

        Returns:
            dict: The JSON response from the MRAPI.
        """
        # Step 1: Request multiple pages from 'match-history' endpoint for a player
        player_uid = self.request_uid
        all_matches = []
        page = 1
        while True:
            print(f'Fetching match history for player {player_uid}... page: {page}')
            match_history = self.get_data(api_version="v2", endpoint="match-history", request_uid=player_uid, page=page)
            normalized_match_history = json_normalize(match_history['match_history'])
    
            print(f'Normalizing json data...')
            if normalized_match_history is None or len(normalized_match_history) == 0:
                print(f'No more matches found for player {player_uid}...')
                break
            matches = normalized_match_history['match_uid'].to_list()
            print(f'Found {len(matches)} matches on page {page}...')
            print(f'Adding {len(matches)} matches to all_matches ({len(all_matches)})... ')
            all_matches.append(normalized_match_history)
            page += 1

        # Extract match_uids
        all_matches = pd.concat(all_matches)
        matches_list = all_matches['match_uid'].to_list()

        # Verify the matches are unique
        matches_list = list(set(matches_list))
        print(f'\nFound {len(matches_list)} match_uids for player {player_uid}...\n')

        # Step 2: Request the match data for each match_uid from the 'match' endpoint
        match_data = []
        for match_uid in matches_list:

            print(f'Fetching match data for match_uid {match_uid}...')
            match = self.get_data(api_version="v1", endpoint="match", request_uid=match_uid)
            print(f'Normalizing json data...')
            normalized_match = json_normalize(match)
            print(f'Adding match data for match_uid {match_uid}...')
            match_data.append(normalized_match)

        # Step 2.1: Randomly sample a player from the match data (optional)
        """ sampled_player_uid = random.choice(match_data[0]["players"])["player_uid"]
        sampled_player_matches = []
        page = 1
        while True:
            sampled_history = self.get_data(api_version="v2", endpoint="match-history", request_uid=sampled_player_uid, page=page)
            sampled_matches = sampled_history.get("matches", [])
            if not sampled_matches:
                break
            sampled_player_matches.extend(sampled_matches)
            page += 1 """

        # Step 2.2: Request the player data for each player in the match data (optional)
        """ player_data = []
        for match in match_data:
            for player in match["players"]:
                player_uid = player["player_uid"]
            player_info = self.get_data(api_version="v2", endpoint="player", request_uid=player_uid)
            player_data.append(player_info) """

        # Step 3: Create a dataframe from the match data and player data
        print('\nCreating dataframes from match data...')
        match_df = pd.concat(match_data)
        #player_df = pd.DataFrame(player_data)

        print(f'Creating dataframe for player match history...')
        
        # Save raw dataframes to CSV
        print('\nSaving raw dataframes to CSV...')
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        match_df.to_csv(f"../data/match_data_{self.request_params['season']}_{self.request_uid}_{current_date}.csv", index=False)
        all_matches.to_csv(f"../data/match_history_{self.request_params['season']}_{self.request_uid}_{current_date}.csv", index=False)
        #player_df.to_csv("player_data.csv", index=False)


        print('\nDataframes saved to CSV, check the current directory in folder "data".')
        # Step 4: Use the DataCleaner class to clean the data (assuming DataCleaner is implemented elsewhere)
        cleaner = DataCleaner()


class DataCleaner:
    
    """
    A class for cleaning MRAPI dataframes.
    This class provides methods to clean the API dataframes by removing unnecessary columns and rows.
    This class also assumes you have the 'hero_info.csv' file in the same directory. The 'hero_info.csv' file contains information about the heroes in the game.

    Note: A lot of the data cleaning is a process I already had programmed in a notebook that I did NOT feel like going through
    and fixing. I'd honestly just rather create a new function to open the files and fix the column headers as the API outputs data
    in a weird way. I will fix this in the future (maybe), but for now, this is a quick and dirty way to get the data cleaned up.

    """
    def __init__(self):
        self.df_column_heads = [
            'match_uid', 
            'player_uid', 
            'name', 
            'hero_id', 
            'is_win', 
            'kills', 
            'deaths', 
            'assists', 
            'hero_damage', 
            'hero_healed', 
            'damage_taken', 
            'heroes']
        
        self.hero_column_heads = [
            'id',
            'name',	
            'attack_type',	
            'role']
        
        self.filename_prefix = 'match_data_'  # Prefix for the CSV files to be cleaned
        self.filename_suffix = None

        pass

    def clean(self, csv_file=None):
        """
        Cleans the given dataframe by removing unnecessary columns and rows.
        This method assumes you have the 'hero_info.csv' file in the same directory.

        csv_file (str): The path to the CSV file to be cleaned. Otherwise, it will load the most recent CSV file from the data folder.

        Returns:
            csv file: The cleaned dataframe.
        """
        # Load the CSV File
        print('\n\nLoading CSV file...')
        # Get the most recent CSV file from the data folder
     
        if csv_file is None:
            data_folder = '../data'
            csv_files = glob.glob(os.path.join(data_folder, 'match_data*.csv'))
            if not csv_files:
                raise FileNotFoundError("No CSV files with 'match_data' in the name found in the data folder.")
            latest_csv_file = max(csv_files, key=os.path.getmtime)
            print(f'Loading the most recent CSV file: {latest_csv_file}')
            csv_file = latest_csv_file

        # Extract the unique identifier from the file name
        unique_identifier = os.path.basename(csv_file).split('match_data', 1)[1].lstrip('_').split('.')[0]
        print(f'Extracted unique identifier: {unique_identifier}')
        self.filename_suffix = unique_identifier

        df = pd.read_csv(latest_csv_file)
        hero_id = pd.read_csv('hero_info.csv')


        # Ensure the 'match_details.match_players' column is properly converted to a list of dictionaries
        df['match_details.match_players'] = df['match_details.match_players'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

        # Convert the 'match_details.match_players' column to a DataFrame
        match_players_df = pd.json_normalize(df['match_details.match_players'].explode(), max_level=0)

        # Add the match_uid to each player by repeating the 'match_details.match_uid' for each exploded row
        match_players_df['match_uid'] = df.loc[df.index.repeat(df['match_details.match_players'].apply(len)), 'match_details.match_uid'].values

        df_output = pd.DataFrame(columns=self.df_column_heads)
        
        df_output['match_uid'] = match_players_df['match_uid']
        df_output['player_uid'] = match_players_df['player_uid']
        df_output['name'] = match_players_df['nick_name']
        df_output['hero_id']  = match_players_df['cur_hero_id']
        df_output['is_win'] = match_players_df['is_win']
        df_output['kills'] = match_players_df['kills']
        df_output['deaths'] = match_players_df['deaths']
        df_output['assists'] = match_players_df['assists']
        df_output['hero_damage'] = match_players_df['total_hero_damage']
        df_output['hero_healed'] = match_players_df['total_hero_heal']
        df_output['damage_taken'] = match_players_df['total_damage_taken']
        df_output['heroes'] = match_players_df['player_heroes']
        df_output['is_win'] = df_output['is_win'].astype(int)
        
        hero_info_df = hero_id[self.hero_column_heads]

        # Explode the 'heroes' column to create individual rows for each hero
        exploded_heroes = df_output['heroes'].explode()

        # Ensure the exploded data is a list of dictionaries
        exploded_heroes = exploded_heroes.dropna().apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

        # Normalize the exploded data
        normalized_df = pd.json_normalize(exploded_heroes)
        normalized_df = normalized_df.rename(columns={'play_time':'playtime.raw','session_hit_rate':'hit_rate'})

        # Explode the 'heroes' column to create individual rows for each hero
        exploded_heroes = df_output.explode('heroes').reset_index(drop=True)

        # Ensure the exploded data is a list of dictionaries
        exploded_heroes['heroes'] = exploded_heroes['heroes'].dropna().apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

        # Normalize the exploded data
        normalized_heroes = pd.json_normalize(exploded_heroes['heroes'])

        # Add the player_uid and match_uid columns back to the normalized data
        normalized_heroes['player_uid'] = exploded_heroes['player_uid'].reset_index(drop=True)
        normalized_heroes['match_uid'] = exploded_heroes['match_uid'].reset_index(drop=True)
        normalized_heroes = normalized_heroes.rename(columns={'play_time':'playtime.raw','session_hit_rate':'hit_rate'}) 
        normalized_heroes['playtime.raw'] = round(normalized_heroes['playtime.raw'])

        # Convert whole number value columns to integers
        columns_to_convert = ['hero_id', 'playtime.raw','kills', 'deaths', 'assists', 'player_uid']
        normalized_heroes[columns_to_convert] = normalized_heroes[columns_to_convert].astype('Int64')

        # Merge exploded_df with hero_info_df on the hero_id column
        merged_df = normalized_heroes.merge(hero_info_df[['id', 'attack_type', 'role']], left_on='hero_id', right_on='id', how='inner')

        # Drop the redundant 'id' column after the merge
        merged_df = merged_df.drop(columns=['id'])

        # Edit the data and remove heros to make other processes later easier
        merged_df['attack_type'] = merged_df['attack_type'].str.replace(' Heroes', '', regex=False)

        # Merge exploded_df with df on the appropriate columns
        combined_df = merged_df.merge(df_output, on=['player_uid', 'match_uid'], how='inner')

        # Drop columns if they exist
        columns_to_drop = ['playtime.minutes', 'playtime.seconds', 'heroes', 'hero_icon']
        combined_df = combined_df.drop(columns=[col for col in columns_to_drop if col in combined_df.columns])
        
        # Remove the null (0) enteries and round the playtime.raw value to the nearest whole number
        combined_df = combined_df[combined_df['playtime.raw'] == round(combined_df['playtime.raw'])]
        combined_df['playtime.raw'] = combined_df['playtime.raw'].astype('Int64')
        combined_df = combined_df[combined_df['playtime.raw'] != 0] # these are leavers
        
        # now output the same data but without breaking it down by unique hero_id played by a player
        filtered_df = combined_df[combined_df['hero_id_x'] == combined_df['hero_id_y']]     # this will be the original data row entery for the player
        
        # Group by match_uid and is_win
        grouped_df = filtered_df.groupby(['match_uid', 'is_win']).agg(
            num_vang=('role', lambda x: (x == 'VANGUARD').sum()),
            num_strat=('role', lambda x: (x == 'STRATEGIST').sum()),
            num_duel=('role', lambda x: (x == 'DUELIST').sum()),
            players_on_team=('player_uid', 'count'),
            avg_hitrate=('hit_rate', 'mean'),
            num_melee=('attack_type', lambda x: (x == 'Melee').sum()),
            num_hitscan=('attack_type', lambda x: (x == 'Hitscan').sum()),
            num_projectile=('attack_type', lambda x: (x == 'Projectile').sum()),
            total_damage=('hero_damage', 'sum'),
            total_healing=('hero_healed', 'sum'),
            total_damage_taken=('damage_taken', 'sum'),
            total_deaths=('deaths_x', 'sum'),
            total_assists=('assists_x', 'sum'),
            total_kills=('kills_x', 'sum')
        ).reset_index()

        # Add primary_attack_type column
        grouped_df['primary_attack_type'] = grouped_df[['num_melee', 'num_projectile', 'num_hitscan']].idxmax(axis=1).str.replace('num_', '')

        # Identify match_uids where players_on_team is greater than 6
        invalid_matches = grouped_df[grouped_df['players_on_team'] > 6]['match_uid'].unique()

        # Remove entries with these match_uids
        grouped_df = grouped_df[~grouped_df['match_uid'].isin(invalid_matches)]

        #----------------------------------------------------------------------------------------
        
        # output the cleaned dataframe to a csv file
        combined_df.to_csv(f'../data/cleaned_match_data_individual_stats_{self.filename_suffix}.csv', index=False)
        filtered_df.to_csv(f'../data/cleaned_match_data_{self.filename_suffix}.csv', index=False)
        grouped_df.to_csv(f'../data/cleaned_match_data_team_stats_{self.filename_suffix}.csv', index=False)

        self.fix_file_headers


    def fix_file_headers(self):
        """
        Fixes the headers of the CSV files to match the expected format.
        This method will rename the columns of the CSV files to match the expected format.
        """
        # Load the CSV files

        data_folder = '../data'

        cmdis_file = glob.glob(os.path.join(data_folder, 'cleaned_match_data_individual_stats*.csv'))
        cmdis_newest = max(cmdis_file, key=os.path.getmtime)
        cmd_file = glob.glob(os.path.join(data_folder, 'cleaned_match_data*.csv'))
        cmd_newest = max(cmd_file, key=os.path.getmtime)            
        cmdts_file = glob.glob(os.path.join(data_folder, 'cleaned_match_data_team_stats*.csv'))
        cmdts_newest = max(cmdts_file, key=os.path.getmtime)
        
        print(f'Loading the most recent CSV files... {cmd_newest}')
        cmd_df = pd.read_csv(cmd_newest)
        print(f'Loading the most recent CSV files... {cmdts_newest}')
        cmdts_df = pd.read_csv(cmdts_newest)
        print(f'Loading the most recent CSV files... {cmdis_newest}')
        cmdis_df = pd.read_csv(cmdis_newest)
        
        

        print('Removing suffixes...')
        # remove the suffix from the columns if they exist
        cmdis_df.columns = cmdis_df.columns.str.replace('_x', '', regex=False)
        cmdis_df.columns = cmdis_df.columns.str.replace('_y', '', regex=False)
        
        cmd_df.columns = cmd_df.columns.str.replace('_x', '', regex=False)
        cmd_df.columns = cmd_df.columns.str.replace('_y', '', regex=False)

        cmdts_df.columns = cmdts_df.columns.str.replace('_x', '', regex=False)
        cmdts_df.columns = cmdts_df.columns.str.replace('_y', '', regex=False)

        # Drop all duplicate columns from the cleaned_match_data_individual_stats.csv file if it exists
        # e.g. hero_id_x, hero_id_y, deaths_x, deaths_y, etc.
        
        print(f'Dropping duplicate columns...')
        cmdis_df = cmdis_df.loc[:, ~cmdis_df.columns.duplicated(keep='first')]
        cmd_df = cmd_df.loc[:, ~cmd_df.columns.duplicated(keep='last')]
        cmdts_df = cmdts_df.loc[:, ~cmdts_df.columns.duplicated(keep='last')]

        print('Overwriting and saving CSVs...')
        # Overwrite the CSV files with the updated headers
        cmdis_df.to_csv(cmdis_newest, index=False)
        cmd_df.to_csv(cmd_newest, index=False)
        cmdts_df.to_csv(cmdts_newest, index=False)