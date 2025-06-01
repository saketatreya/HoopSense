import os
import pandas as pd
from nba_api.stats.endpoints import LeagueDashPlayerStats, LeagueDashTeamStats

# --- Configuration ---
SEASON = '2023-24' # Example: '2023-24'
SEASON_TYPE = 'Regular Season' # Options: 'Regular Season', 'Playoffs', 'Pre Season', 'All Star'
PER_MODE = 'PerGame' # Options: 'Totals', 'PerGame', 'MinutesPerGame', 'Per48', etc.
MEASURE_TYPE = 'Base' # Options: 'Base', 'Advanced', 'Misc', 'Four Factors', 'Scoring', etc.

# Determine the project root directory (one level up from the 'scripts' directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data') # Directory to store the CSV files

PLAYER_STATS_FILENAME = f'nba_player_stats_{SEASON.replace("-", "_")}_{SEASON_TYPE.replace(" ", "_").lower()}.csv'
TEAM_STATS_FILENAME = f'nba_team_stats_{SEASON.replace("-", "_")}_{SEASON_TYPE.replace(" ", "_").lower()}.csv'


def fetch_and_save_player_stats(season, season_type, per_mode, measure_type, output_path):
    """Fetches player statistics and saves them to a CSV file."""
    print(f"Fetching player stats for {season} ({season_type} - {per_mode} - {measure_type})...")
    try:
        player_stats = LeagueDashPlayerStats(
            season=season,
            season_type_all_star=season_type,
            per_mode_detailed=per_mode,
            measure_type_detailed_defense=measure_type
        )
        df_player_stats = player_stats.get_data_frames()[0]
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_player_stats.to_csv(output_path, index=False)
        print(f"Player stats saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error fetching or saving player stats: {e}")
        return False

def fetch_and_save_team_stats(season, season_type, per_mode, measure_type, output_path):
    """Fetches team statistics and saves them to a CSV file."""
    print(f"Fetching team stats for {season} ({season_type} - {per_mode} - {measure_type})...")
    try:
        team_stats = LeagueDashTeamStats(
            season=season,
            season_type_all_star=season_type,
            per_mode_detailed=per_mode,
            measure_type_detailed_defense=measure_type
        )
        df_team_stats = team_stats.get_data_frames()[0]
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_team_stats.to_csv(output_path, index=False)
        print(f"Team stats saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error fetching or saving team stats: {e}")
        return False

if __name__ == "__main__":
    # Create data directory if it doesn't exist (now relative to project root)
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")

    player_output_file = os.path.join(DATA_DIR, PLAYER_STATS_FILENAME)
    team_output_file = os.path.join(DATA_DIR, TEAM_STATS_FILENAME)

    # Fetch and save player stats
    fetch_and_save_player_stats(SEASON, SEASON_TYPE, PER_MODE, MEASURE_TYPE, player_output_file)

    print("\n" + "-"*30 + "\n")

    # Fetch and save team stats
    fetch_and_save_team_stats(SEASON, SEASON_TYPE, PER_MODE, MEASURE_TYPE, team_output_file)
    
    print("\nNBA data fetching complete.") 