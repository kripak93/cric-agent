"""
Simple Matchup Statistics Module
Accurate cricket statistics calculations from ball-by-ball data
"""

import pandas as pd
import numpy as np


class SimpleMatchupStats:
    """
    Accurate cricket statistics calculator for matchup analysis.
    Calculates per-ball runs from cumulative data and provides various matchup statistics.
    """
    
    def __init__(self, csv_path='ipl_data.csv'):
        """
        Initialize the statistics calculator with IPL data.
        
        Args:
            csv_path (str): Path to the CSV file containing ball-by-ball data
        """
        print(f"Loading data from {csv_path}...")
        self.df = pd.read_csv(csv_path)
        print(f"Loaded {len(self.df)} records")
        
        # Mapping between abbreviated and full team names
        self.team_name_map = {
            'CSK': 'Chennai Super Kings',
            'RCB': 'Royal Chal Bengaluru',
            'PBKS': 'Punjab Kings',
            'DC': 'Delhi Capitals',
            'SRH': 'Sunrisers Hyderabad',
            'KKR': 'Kolkata Knight Riders',
            'LSG': 'Lucknow Super Giants',
            'RR': 'Rajasthan Royals',
            'MI': 'Mumbai Indians',
            'GT': 'Gujarat Titans'
        }
        
        # Reverse mapping
        self.team_abbrev_map = {v: k for k, v in self.team_name_map.items()}
        
        # Prepare ball-level data
        self._prepare_ball_level_data()
        
    def _get_team_abbreviation(self, team_name):
        """Get abbreviated team name."""
        if team_name in self.team_abbrev_map:
            return self.team_abbrev_map[team_name]
        elif team_name in self.team_name_map:
            return team_name
        else:
            return team_name
    
    def _get_team_full_name(self, team_name):
        """Get full team name."""
        if team_name in self.team_name_map:
            return self.team_name_map[team_name]
        elif team_name in self.team_abbrev_map:
            return team_name
        else:
            return team_name
        
    def _prepare_ball_level_data(self):
        """
        Calculate runs scored on each ball from cumulative R.1 column.
        For each batsman's innings, calculates runs_this_ball by taking the difference
        between consecutive R.1 values.
        """
        print("Preparing ball-level data...")
        
        # Sort by match, innings, batsman, and overs to ensure proper ordering
        self.df = self.df.sort_values(['Match⬆', 'I#', 'Batsman', 'Overs'])
        
        # Initialize runs_this_ball column
        self.df['runs_this_ball'] = 0
        
        # Group by match, innings and batsman to calculate runs per ball
        for (match, innings, batsman), group in self.df.groupby(['Match⬆', 'I#', 'Batsman']):
            indices = group.index
            r1_values = group['R.1'].values
            
            # Calculate runs for each ball
            runs_per_ball = np.zeros(len(r1_values))
            
            # First ball: runs = R.1 value
            if len(r1_values) > 0:
                runs_per_ball[0] = r1_values[0] if pd.notna(r1_values[0]) else 0
            
            # Subsequent balls: runs = current R.1 - previous R.1
            for i in range(1, len(r1_values)):
                if pd.notna(r1_values[i]) and pd.notna(r1_values[i-1]):
                    runs_per_ball[i] = r1_values[i] - r1_values[i-1]
                elif pd.notna(r1_values[i]):
                    runs_per_ball[i] = r1_values[i]
                else:
                    runs_per_ball[i] = 0
            
            # Assign back to dataframe
            self.df.loc[indices, 'runs_this_ball'] = runs_per_ball
        
        # Ensure runs_this_ball is non-negative (handle any data anomalies)
        self.df.loc[self.df['runs_this_ball'] < 0, 'runs_this_ball'] = 0
        
        # Create indicators for dot balls, fours, and sixes based on runs_this_ball
        self.df['is_dot'] = (self.df['runs_this_ball'] == 0).astype(int)
        self.df['is_four'] = (self.df['runs_this_ball'] == 4).astype(int)
        self.df['is_six'] = (self.df['runs_this_ball'] == 6).astype(int)
        
        print("Ball-level data prepared successfully")
        
    def batsman_vs_bowling_type(self, batsman, bowling_type):
        """
        Get batsman statistics against a specific bowling type.
        
        Args:
            batsman (str): Name of the batsman
            bowling_type (str): Type of bowling (e.g., 'right pace', 'off break', 'leg break')
            
        Returns:
            dict: Statistics including balls, runs, strike rate, dismissals, boundaries, dots
        """
        # Filter data for the batsman and bowling type
        filtered = self.df[
            (self.df['Batsman'] == batsman) & 
            (self.df['Technique'] == bowling_type)
        ]
        
        if len(filtered) == 0:
            return {
                'error': f'No data found for {batsman} vs {bowling_type}',
                'balls': 0,
                'runs': 0
            }
        
        # Calculate statistics
        balls = len(filtered)
        runs = filtered['runs_this_ball'].sum()
        
        # Dismissals (where Wkt is not '-')
        dismissals = len(filtered[filtered['Wkt'] != '-'])
        
        # Boundaries (using calculated indicators)
        fours = filtered['is_four'].sum()
        sixes = filtered['is_six'].sum()
        boundaries = fours + sixes
        
        # Dot balls (using calculated indicator)
        dots = filtered['is_dot'].sum()
        
        # Calculate rates
        strike_rate = (runs / balls * 100) if balls > 0 else 0
        dot_percentage = (dots / balls * 100) if balls > 0 else 0
        boundary_percentage = (boundaries / balls * 100) if balls > 0 else 0
        average = (runs / dismissals) if dismissals > 0 else runs
        
        return {
            'batsman': batsman,
            'bowling_type': bowling_type,
            'balls': int(balls),
            'runs': int(runs),
            'strike_rate': round(strike_rate, 2),
            'dismissals': int(dismissals),
            'average': round(average, 2),
            'fours': int(fours),
            'sixes': int(sixes),
            'boundaries': int(boundaries),
            'dots': int(dots),
            'dot_percentage': round(dot_percentage, 2),
            'boundary_percentage': round(boundary_percentage, 2)
        }
    
    def batsman_vs_bowler(self, batsman, bowler):
        """
        Get head-to-head statistics between a batsman and bowler.
        
        Args:
            batsman (str): Name of the batsman
            bowler (str): Name of the bowler
            
        Returns:
            dict: Head-to-head statistics including balls, runs, strike rate, dismissals
        """
        # Filter data for the matchup
        filtered = self.df[
            (self.df['Batsman'] == batsman) & 
            (self.df['Player'] == bowler)
        ]
        
        if len(filtered) == 0:
            return {
                'error': f'No data found for {batsman} vs {bowler}',
                'balls': 0,
                'runs': 0
            }
        
        # Calculate statistics
        balls = len(filtered)
        runs = filtered['runs_this_ball'].sum()
        dismissals = len(filtered[filtered['Wkt'] != '-'])
        
        # Boundaries
        fours = filtered['is_four'].sum()
        sixes = filtered['is_six'].sum()
        
        # Calculate rates
        strike_rate = (runs / balls * 100) if balls > 0 else 0
        average = (runs / dismissals) if dismissals > 0 else runs
        
        # Determine dominance
        if dismissals > 0 and strike_rate < 100:
            dominance = 'Bowler'
        elif strike_rate >= 150:
            dominance = 'Batsman'
        elif strike_rate >= 120:
            dominance = 'Batsman (Slight)'
        elif dismissals > 0:
            dominance = 'Bowler (Slight)'
        else:
            dominance = 'Neutral'
        
        return {
            'batsman': batsman,
            'bowler': bowler,
            'balls': int(balls),
            'runs': int(runs),
            'strike_rate': round(strike_rate, 2),
            'dismissals': int(dismissals),
            'average': round(average, 2),
            'fours': int(fours),
            'sixes': int(sixes),
            'dominance': dominance
        }
    
    def bowler_vs_batting_hand(self, bowler, batting_hand):
        """
        Get bowler statistics against specific batting hand (R/L).
        
        Args:
            bowler (str): Name of the bowler
            batting_hand (str): 'R' for right-handed or 'L' for left-handed
            
        Returns:
            dict: Bowling statistics including balls, runs, economy, wickets, average, SR, dot%
        """
        # Filter data for the bowler and batting hand
        filtered = self.df[
            (self.df['Player'] == bowler) & 
            (self.df['RL'] == batting_hand)
        ]
        
        if len(filtered) == 0:
            return {
                'error': f'No data found for {bowler} vs {batting_hand}-handed batsmen',
                'balls': 0,
                'runs': 0
            }
        
        # Calculate statistics
        balls = len(filtered)
        runs = filtered['runs_this_ball'].sum()
        wickets = len(filtered[filtered['Wkt'] != '-'])
        dots = filtered['is_dot'].sum()
        
        # Calculate rates
        economy = (runs / (balls / 6)) if balls > 0 else 0
        bowling_average = (runs / wickets) if wickets > 0 else 0
        bowling_strike_rate = (balls / wickets) if wickets > 0 else 0
        dot_percentage = (dots / balls * 100) if balls > 0 else 0
        
        # Effectiveness rating
        if economy < 6.0 and dot_percentage > 40:
            effectiveness = 'Excellent'
        elif economy < 7.5 and dot_percentage > 35:
            effectiveness = 'Good'
        elif economy < 9.0:
            effectiveness = 'Average'
        else:
            effectiveness = 'Expensive'
        
        hand_name = 'Right-handed' if batting_hand == 'R' else 'Left-handed'
        
        return {
            'bowler': bowler,
            'batting_hand': hand_name,
            'balls': int(balls),
            'runs': int(runs),
            'economy': round(economy, 2),
            'wickets': int(wickets),
            'average': round(bowling_average, 2) if wickets > 0 else 'N/A',
            'bowling_strike_rate': round(bowling_strike_rate, 2) if wickets > 0 else 'N/A',
            'dot_percentage': round(dot_percentage, 2),
            'dots': int(dots),
            'effectiveness': effectiveness
        }
    
    def bowler_economy_by_phase(self, bowler):
        """
        Compare bowler's economy in powerplay vs post-powerplay.
        
        Args:
            bowler (str): Name of the bowler
            
        Returns:
            dict: Statistics for powerplay (overs 1-6) and post-powerplay (overs 7-20)
        """
        # Get all balls bowled by this bowler
        bowler_data = self.df[self.df['Player'] == bowler]
        
        if len(bowler_data) == 0:
            return {
                'error': f'No data found for {bowler}',
                'powerplay': {},
                'post_powerplay': {}
            }
        
        # Extract over number
        bowler_data = bowler_data.copy()
        bowler_data['over_num'] = bowler_data['Overs'].astype(str).str.split('.').str[0].astype(float)
        
        # Split into powerplay (overs 1-6) and post-powerplay (overs 7-20)
        powerplay = bowler_data[bowler_data['over_num'] <= 6]
        post_powerplay = bowler_data[bowler_data['over_num'] > 6]
        
        def calculate_phase_stats(phase_data, phase_name):
            if len(phase_data) == 0:
                return {
                    'phase': phase_name,
                    'balls': 0,
                    'runs': 0,
                    'economy': 0,
                    'wickets': 0,
                    'dots': 0,
                    'dot_percentage': 0
                }
            
            balls = len(phase_data)
            runs = phase_data['runs_this_ball'].sum()
            wickets = len(phase_data[phase_data['Wkt'] != '-'])
            dots = phase_data['is_dot'].sum()
            
            economy = (runs / (balls / 6)) if balls > 0 else 0
            dot_percentage = (dots / balls * 100) if balls > 0 else 0
            
            return {
                'phase': phase_name,
                'balls': int(balls),
                'runs': int(runs),
                'economy': round(economy, 2),
                'wickets': int(wickets),
                'dots': int(dots),
                'dot_percentage': round(dot_percentage, 2)
            }
        
        pp_stats = calculate_phase_stats(powerplay, 'Powerplay (1-6)')
        post_pp_stats = calculate_phase_stats(post_powerplay, 'Post-Powerplay (7-20)')
        
        # Analysis
        if pp_stats['balls'] > 0 and post_pp_stats['balls'] > 0:
            if pp_stats['economy'] < post_pp_stats['economy']:
                analysis = f"{bowler} is more effective in the powerplay (Econ: {pp_stats['economy']} vs {post_pp_stats['economy']})"
            elif pp_stats['economy'] > post_pp_stats['economy']:
                analysis = f"{bowler} is more effective post-powerplay (Econ: {post_pp_stats['economy']} vs {pp_stats['economy']})"
            else:
                analysis = f"{bowler} maintains consistent economy across phases"
        elif pp_stats['balls'] > 0:
            analysis = f"{bowler} bowls primarily in the powerplay"
        elif post_pp_stats['balls'] > 0:
            analysis = f"{bowler} bowls primarily post-powerplay"
        else:
            analysis = "No data available"
        
        return {
            'bowler': bowler,
            'powerplay': pp_stats,
            'post_powerplay': post_pp_stats,
            'analysis': analysis
        }
    
    def team_matchup(self, team1, team2):
        """
        Get team vs team batting statistics.
        
        Args:
            team1 (str): First team name (can be abbreviated or full name)
            team2 (str): Second team name (can be abbreviated or full name)
            
        Returns:
            dict: Batting statistics for each team against the other
        """
        # Get both abbreviated and full names
        team1_abbrev = self._get_team_abbreviation(team1)
        team1_full = self._get_team_full_name(team1)
        team2_abbrev = self._get_team_abbreviation(team2)
        team2_full = self._get_team_full_name(team2)
        
        # Team1 batting vs Team2 bowling
        # Team = bowling team (abbreviated), Opposition = batting team (full name)
        team1_batting = self.df[
            (self.df['Opposition'] == team1_full) & 
            (self.df['Team'] == team2_abbrev)
        ]
        
        # Team2 batting vs Team1 bowling
        team2_batting = self.df[
            (self.df['Opposition'] == team2_full) & 
            (self.df['Team'] == team1_abbrev)
        ]
        
        def calculate_team_stats(data, team_name, opponent):
            if len(data) == 0:
                return {
                    'team': team_name,
                    'opponent': opponent,
                    'balls': 0,
                    'runs': 0,
                    'run_rate': 0,
                    'strike_rate': 0,
                    'boundaries': 0
                }
            
            balls = len(data)
            runs = data['runs_this_ball'].sum()
            fours = data['is_four'].sum()
            sixes = data['is_six'].sum()
            boundaries = fours + sixes
            
            run_rate = (runs / balls * 6) if balls > 0 else 0
            strike_rate = (runs / balls * 100) if balls > 0 else 0
            
            return {
                'team': team_name,
                'opponent': opponent,
                'balls': int(balls),
                'runs': int(runs),
                'run_rate': round(run_rate, 2),
                'strike_rate': round(strike_rate, 2),
                'fours': int(fours),
                'sixes': int(sixes),
                'boundaries': int(boundaries)
            }
        
        team1_stats = calculate_team_stats(team1_batting, team1_full, team2_full)
        team2_stats = calculate_team_stats(team2_batting, team2_full, team1_full)
        
        # Determine advantage
        if team1_stats['balls'] > 0 and team2_stats['balls'] > 0:
            if team1_stats['run_rate'] > team2_stats['run_rate']:
                advantage = f"{team1_full} has batting advantage (RR: {team1_stats['run_rate']} vs {team2_stats['run_rate']})"
            elif team2_stats['run_rate'] > team1_stats['run_rate']:
                advantage = f"{team2_full} has batting advantage (RR: {team2_stats['run_rate']} vs {team1_stats['run_rate']})"
            else:
                advantage = "Evenly matched"
        else:
            advantage = "Insufficient data for comparison"
        
        return {
            'team1_batting': team1_stats,
            'team2_batting': team2_stats,
            'advantage': advantage
        }


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Simple Matchup Statistics - Example Usage")
    print("=" * 60)
    
    stats = SimpleMatchupStats('ipl_data.csv')
    
    print("\n1. Batsman vs Bowling Type")
    print("-" * 60)
    result = stats.batsman_vs_bowling_type('V Kohli', 'right pace')
    if 'error' not in result:
        print(f"Batsman: {result['batsman']}")
        print(f"Bowling Type: {result['bowling_type']}")
        print(f"Balls: {result['balls']}")
        print(f"Runs: {result['runs']}")
        print(f"Strike Rate: {result['strike_rate']}")
        print(f"Dismissals: {result['dismissals']}")
        print(f"Boundaries: {result['boundaries']} (4s: {result['fours']}, 6s: {result['sixes']})")
        print(f"Dot %: {result['dot_percentage']}")
    else:
        print(result['error'])
    
    print("\n2. Head-to-Head")
    print("-" * 60)
    result = stats.batsman_vs_bowler('V Kohli', 'DL Chahar')
    if 'error' not in result:
        print(f"Batsman: {result['batsman']}")
        print(f"Bowler: {result['bowler']}")
        print(f"Balls: {result['balls']}")
        print(f"Runs: {result['runs']}")
        print(f"Strike Rate: {result['strike_rate']}")
        print(f"Dismissals: {result['dismissals']}")
        print(f"Dominance: {result['dominance']}")
    else:
        print(result['error'])
    
    print("\n3. Bowler vs Batting Hand")
    print("-" * 60)
    result = stats.bowler_vs_batting_hand('DL Chahar', 'R')
    if 'error' not in result:
        print(f"Bowler: {result['bowler']}")
        print(f"Batting Hand: {result['batting_hand']}")
        print(f"Balls: {result['balls']}")
        print(f"Runs: {result['runs']}")
        print(f"Economy: {result['economy']}")
        print(f"Wickets: {result['wickets']}")
        print(f"Dot %: {result['dot_percentage']}")
        print(f"Effectiveness: {result['effectiveness']}")
    else:
        print(result['error'])
    
    print("\n4. Bowler Economy by Phase")
    print("-" * 60)
    result = stats.bowler_economy_by_phase('DL Chahar')
    if 'error' not in result:
        print(f"Bowler: {result['bowler']}")
        print(f"\nPowerplay: Econ {result['powerplay']['economy']}, Balls {result['powerplay']['balls']}")
        print(f"Post-Powerplay: Econ {result['post_powerplay']['economy']}, Balls {result['post_powerplay']['balls']}")
        print(f"\nAnalysis: {result['analysis']}")
    else:
        print(result['error'])
    
    print("\n5. Team Matchup")
    print("-" * 60)
    result = stats.team_matchup('CSK', 'RCB')  # Can use abbreviations now
    print(f"Team 1 ({result['team1_batting']['team']}): RR {result['team1_batting']['run_rate']}, {result['team1_batting']['runs']} runs in {result['team1_batting']['balls']} balls")
    print(f"Team 2 ({result['team2_batting']['team']}): RR {result['team2_batting']['run_rate']}, {result['team2_batting']['runs']} runs in {result['team2_batting']['balls']} balls")
    print(f"\n{result['advantage']}")
    
    print("\n" + "=" * 60)
    print("Example usage complete!")
    print("=" * 60)
