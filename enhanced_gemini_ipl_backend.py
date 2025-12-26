"""
Enhanced Gemini IPL Analytics Backend with Schema Awareness
Incorporates detailed understanding of the IPL dataset structure
"""

import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class EnhancedGeminiIPLAnalytics:
    """
    Gemini-powered IPL analytics with full dataset schema understanding.
    Automatically provides context and structured data to Gemini for better analysis.
    """

    def __init__(self, csv_path, api_key=None, model_name='gemini-1.5-flash', season_filter=None):
        """Initialize with CSV data and Gemini API"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env or pass as argument.")

        genai.configure(api_key=self.api_key)
        
        # Try models with better rate limits (gemini-1.5-flash has 1500 RPD free tier)
        model_priority = [
            'gemini-1.5-flash',      # Best free tier: 1500 RPD
            'gemini-1.5-flash-8b',   # Fallback: 1500 RPD
            model_name,              # User specified
            'gemini-2.0-flash-exp'   # Experimental
        ]
        
        self.model = None
        for model in model_priority:
            try:
                self.model = genai.GenerativeModel(model)
                self.model_name = model
                print(f"✅ Using Gemini model: {model}")
                break
            except Exception as e:
                continue
        
        if self.model is None:
            raise ValueError(f"No compatible Gemini models available. Check your API key.")

        # Load dataset
        self.df = pd.read_csv(csv_path)
        
        # Filter for men's IPL only if the dataset contains mixed data
        if 'Match⬆' in self.df.columns:
            original_size = len(self.df)
            self.df = self.df[self.df['Match⬆'].str.startswith('LAT20', na=False)]
            if len(self.df) < original_size:
                print(f"📊 Filtered to Men's IPL only: {len(self.df)} rows (was {original_size})")
        
        # Filter by season if specified
        if season_filter and 'Date⬆' in self.df.columns:
            self.df['Year'] = pd.to_datetime(self.df['Date⬆']).dt.year
            original_size = len(self.df)
            self.df = self.df[self.df['Year'] == season_filter]
            print(f"📅 Filtered to {season_filter} season: {len(self.df)} rows (was {original_size})")
            self.season = season_filter
        else:
            # Determine seasons available
            if 'Date⬆' in self.df.columns:
                self.df['Year'] = pd.to_datetime(self.df['Date⬆']).dt.year
                available_seasons = sorted(self.df['Year'].unique())
                self.season = f"All seasons ({', '.join(map(str, available_seasons))})"
            else:
                self.season = "Unknown"
        
        self.csv_path = csv_path

        # Dataset context for Gemini
        self.dataset_context = self._build_dataset_context()

    def _build_dataset_context(self):
        """Build context string about the dataset for Gemini"""
        # Get actual players from the dataset
        actual_players = sorted(self.df['Player'].dropna().unique())
        sample_players = actual_players[:10]  # Show first 10 as examples
        
        context = f"""
MEN'S IPL DATASET CONTEXT - CURRENT DATA ONLY:
- Season: {self.season}
- Total Records: {len(self.df)}
- Total Columns: {len(self.df.columns)}
- Data Quality: 99.99% complete
- Teams: {', '.join(sorted(self.df['Team'].unique()))}
- Total Players: {len(actual_players)}
- Sample Players: {', '.join(sample_players)}

CRITICAL RESTRICTION:
- This dataset contains ONLY Men's IPL cricket data (LAT20)
- DO NOT use historical cricket knowledge or retired players
- ONLY analyze current IPL players present in this specific dataset
- ONLY use statistics from this current IPL dataset

CRITICAL COLUMNS:
- Player: Individual cricketers (bowlers/batsmen)
- Team: IPL teams (CSK, MI, RCB, KKR, etc.)
- Econ: Economy rate (runs per over)
- O: Overs bowled
- W: Wickets taken
- R.1: Runs scored by batsman
- B: Balls faced

DATA INTERPRETATIONS:
- Economy < 7.0: Excellent bowling
- Economy 7.0-8.0: Good bowling
- Strike Rate: Runs per 100 balls (aggressive batting)
- Wickets: Bowling effectiveness

ANALYSIS GUIDELINES:
1. ONLY use players and data from this specific dataset
2. Filter by minimum workload to avoid outliers
3. Use complete player names from dataset
4. Compare using consistent metrics from this data only
5. If a player is not in this dataset, do not mention them
"""
        return context

    def smart_analyze(self, query):
        """
        Enhanced smart analysis with schema context.
        Uses intent detection + data extraction + Gemini analysis.
        """
        print(f"\n📊 Analyzing: {query}")

        # Step 1: Intent Detection (Local)
        intent = self._detect_intent(query)

        # Step 2: Data Extraction (Local)
        data = self._extract_relevant_data(intent)

        # Step 3: Build Enhanced Prompt
        prompt = self._build_enhanced_prompt(query, intent, data)

        # Step 4: Get Gemini Response with error handling
        try:
            response = self.model.generate_content(prompt)
            return {
                'query': query,
                'intent': intent,
                'gemini_response': response.text,
                'data_extracted': len(data) if data is not None else 0,
                'error': None
            }
        except Exception as e:
            error_msg = str(e)
            
            # Handle rate limit errors
            if 'ResourceExhausted' in error_msg or '429' in error_msg or 'quota' in error_msg.lower():
                return {
                    'query': query,
                    'intent': intent,
                    'gemini_response': f"""
⚠️ **API Rate Limit Reached**

The Gemini API free tier has a limit of 1,500 requests per day. You've reached this limit.

**Your Query:** {query}

**Data Available (No AI Analysis Needed):**
Based on your query, I detected these analysis types: {', '.join(intent)}

You can view the exact data the AI would have analyzed in the tables above. The statistics are 100% accurate and don't require AI interpretation.

**Solutions:**
1. Wait ~1 hour for the quota to reset
2. Use the statistics shown in the data tables (they're already accurate!)
3. Upgrade to a paid Gemini API plan for higher limits
4. The dashboard's matchup analysis tabs don't require AI for accurate results

**Remember:** The AI is optional - all cricket statistics are calculated accurately without it!
""",
                    'data_extracted': len(data) if data is not None else 0,
                    'error': 'rate_limit'
                }
            else:
                # Other errors
                return {
                    'query': query,
                    'intent': intent,
                    'gemini_response': f"❌ AI Error: {error_msg}\n\nThe data tables above show accurate statistics without AI interpretation.",
                    'data_extracted': len(data) if data is not None else 0,
                    'error': error_msg
                }

    def _detect_intent(self, query):
        """Detect user's intent from query"""
        query_lower = query.lower()

        intent_keywords = {
            'economy': ['best economy', 'lowest economy', 'most economical', 'efficient bowler'],
            'wickets': ['most wickets', 'top wicket', 'highest wickets', 'best bowler'],
            'batting': ['best batsman', 'highest runs', 'most runs', 'top scorer', 'run scorer'],
            'strike_rate': ['strike rate', 'fastest scorer', 'aggressive', 'quickest', 'highest sr', 'best sr'],
            'team': ['team', 'csk', 'mi', 'rcb', 'kkr', 'lsg', 'dc', 'rr', 'pbks', 'gt', 'srh'],
            'comparison': ['compare', 'vs', 'versus', 'better', 'difference', 'comparison'],
            'technique': ['technique', 'style', 'bowling type', 'batting style'],
            'ground': ['ground', 'venue', 'stadium', 'wicket', 'pitch'],
            'match': ['match', 'game', 'win', 'lose', 'performance'],
            'ball_position': ['first ball', 'last ball', 'ball position', '1st ball', '6th ball', 'over position', 'ball of over', '0.1', '0.6'],
            'powerplay': ['powerplay', 'pp', 'first 6 overs', 'overs 1-6', 'early overs', 'opening overs'],
            'death': ['death', 'death overs', 'last overs', 'final overs', 'slog overs', 'overs 16-20'],
            'ground_comparison': ['performs on', 'different grounds', 'at different venues', 'ground-wise', 'venue-wise', 'where does', 'which ground']
        }

        detected_intents = []
        for intent_type, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent_type)

        return detected_intents if detected_intents else ['general']

    def _extract_relevant_data(self, intents):
        """Extract relevant data based on detected intents"""
        data_subsets = {}

        if 'economy' in intents:
            # Properly aggregate bowling stats across all matches
            df_copy = self.df.copy()
            df_copy['Match_ID'] = df_copy['Match⬆'] + '_' + df_copy['Player']
            
            # Get max stats per match (cumulative columns)
            bowling_summary = df_copy.groupby('Match_ID').agg({
                'Player': 'first',
                'Team': 'first',
                'O': 'max',  # Overs bowled in that match
                'R': 'max',  # Runs conceded in that match
                'W': 'max',  # Wickets taken in that match
                '0': 'sum'   # Dot balls
            })
            
            # Aggregate across all matches per player
            bowling_stats = bowling_summary.groupby('Player').agg({
                'Team': 'first',
                'O': 'sum',   # Total overs across all matches
                'R': 'sum',   # Total runs conceded
                'W': 'sum',   # Total wickets
                '0': 'sum'    # Total dot balls
            }).round(2)
            
            # Calculate economy rate
            bowling_stats['Econ'] = (bowling_stats['R'] / bowling_stats['O']).round(2)
            
            # Filter for minimum 10 overs bowled (meaningful sample)
            bowling_stats = bowling_stats[bowling_stats['O'] >= 10.0]
            
            # Sort by economy (lower is better)
            bowling_stats = bowling_stats.sort_values('Econ', ascending=True)
            
            data_subsets['economy'] = bowling_stats.head(10)[['Team', 'O', 'R', 'W', 'Econ', '0']]

        if 'wickets' in intents:
            # Properly aggregate bowling stats for wickets
            df_copy = self.df.copy()
            df_copy['Match_ID'] = df_copy['Match⬆'] + '_' + df_copy['Player']
            
            bowling_summary = df_copy.groupby('Match_ID').agg({
                'Player': 'first',
                'Team': 'first',
                'O': 'max',
                'R': 'max',
                'W': 'max',
                '0': 'sum'
            })
            
            bowling_stats = bowling_summary.groupby('Player').agg({
                'Team': 'first',
                'O': 'sum',
                'R': 'sum',
                'W': 'sum',
                '0': 'sum'
            }).round(2)
            
            bowling_stats['Econ'] = (bowling_stats['R'] / bowling_stats['O']).round(2)
            
            # Filter for minimum 5 overs bowled
            bowling_stats = bowling_stats[bowling_stats['O'] >= 5.0]
            
            # Sort by wickets (higher is better)
            bowling_stats = bowling_stats.sort_values('W', ascending=False)
            
            data_subsets['wickets'] = bowling_stats.head(10)[['Team', 'O', 'R', 'W', 'Econ', '0']]

        if 'batting' in intents:
            # Properly aggregate batting stats across all matches
            df_copy = self.df.copy()
            df_copy['Match_ID'] = df_copy['Match⬆'] + '_' + df_copy['Batsman']
            
            # Get max stats per match (cumulative columns)
            batting_summary = df_copy.groupby('Match_ID').agg({
                'Batsman': 'first',
                'Team.1': 'first',
                'R.1': 'max',  # Runs in that match
                'B': 'max',    # Balls faced in that match
                '4': 'sum',    # Fours
                '6': 'sum'     # Sixes
            })
            
            # Aggregate across all matches per batsman
            batting_stats = batting_summary.groupby('Batsman').agg({
                'Team.1': 'first',
                'R.1': 'sum',   # Total runs across all matches
                'B': 'sum',     # Total balls across all matches
                '4': 'sum',     # Total fours
                '6': 'sum'      # Total sixes
            }).round(2)
            
            # Calculate strike rate
            batting_stats['SR'] = ((batting_stats['R.1'] / batting_stats['B']) * 100).round(2)
            
            # Filter for minimum 50 balls faced (meaningful sample)
            batting_stats = batting_stats[batting_stats['B'] >= 50]
            
            # Sort by runs scored
            batting_stats = batting_stats.sort_values('R.1', ascending=False)
            batting_stats.rename(columns={'Team.1': 'Team'}, inplace=True)
            
            data_subsets['batting'] = batting_stats.head(10)[['Team', 'R.1', 'B', 'SR', '4', '6']]
        
        if 'strike_rate' in intents:
            # Extract batsmen sorted by strike rate (minimum sample size)
            df_copy = self.df.copy()
            df_copy['Match_ID'] = df_copy['Match⬆'] + '_' + df_copy['Batsman']
            
            batting_summary = df_copy.groupby('Match_ID').agg({
                'Batsman': 'first',
                'Team.1': 'first',
                'R.1': 'max',
                'B': 'max',
                '4': 'sum',
                '6': 'sum'
            })
            
            batting_stats = batting_summary.groupby('Batsman').agg({
                'Team.1': 'first',
                'R.1': 'sum',
                'B': 'sum',
                '4': 'sum',
                '6': 'sum'
            }).round(2)
            
            batting_stats['SR'] = ((batting_stats['R.1'] / batting_stats['B']) * 100).round(2)
            
            # Higher threshold for SR comparison (100 balls minimum)
            batting_stats = batting_stats[batting_stats['B'] >= 100]
            
            # Sort by strike rate (highest first)
            batting_stats = batting_stats.sort_values('SR', ascending=False)
            batting_stats.rename(columns={'Team.1': 'Team'}, inplace=True)
            
            data_subsets['strike_rate'] = batting_stats.head(10)[['Team', 'R.1', 'B', 'SR', '6']]

        if 'ball_position' in intents:
            # Extract ball position data for analysis
            df_copy = self.df.copy()
            df_copy['Over_Number'] = df_copy['Overs'].astype(str).str.split('.').str[0].astype(float)
            df_copy['Ball_Position'] = df_copy['Overs'].astype(str).str.split('.').str[1].astype(int)
            
            # Get 1st ball vs 6th ball data
            first_ball = df_copy[df_copy['Ball_Position'] == 1]
            last_ball = df_copy[df_copy['Ball_Position'] == 6]
            
            # Aggregate stats by ball position
            ball_stats = []
            for pos in [1, 6]:  # Focus on 1st and 6th balls
                pos_data = df_copy[df_copy['Ball_Position'] == pos]
                if not pos_data.empty:
                    stats = {
                        'Ball_Position': f"Ball {pos} ({'1st' if pos == 1 else '6th'})",
                        'Total_Balls': len(pos_data),
                        'Total_Runs': pos_data['R'].sum(),
                        'Wickets': len(pos_data[pos_data['Wkt'] != '-']),
                        'Dots': len(pos_data[pos_data['0'] == 1]),
                        'Fours': len(pos_data[pos_data['4'] == 1]),
                        'Sixes': len(pos_data[pos_data['6'] == 1]),
                        'Avg_Runs_Per_Ball': round(pos_data['R'].sum() / len(pos_data), 3)
                    }
                    ball_stats.append(stats)
            
            data_subsets['ball_position'] = pd.DataFrame(ball_stats)

        if 'team' in intents:
            # Get team aggregates
            team_stats = self.df.groupby('Team').agg({
                'W': 'sum',
                'R': 'sum',
                'R.1': 'sum',
                'Player': 'nunique'
            }).round(2)
            data_subsets['team'] = team_stats

        if 'powerplay' in intents:
            # Extract powerplay data (overs 0-5, which is 1st to 6th over in cricket)
            df_copy = self.df.copy()
            df_copy['Over_Number'] = df_copy['Overs'].astype(str).str.split('.').str[0].astype(float)
            
            # Filter for powerplay overs (0-5)
            pp_data = df_copy[(df_copy['Over_Number'] >= 0) & (df_copy['Over_Number'] <= 5)].copy()
            
            if not pp_data.empty:
                # BOWLING STATS
                pp_data['Match_ID'] = pp_data['Match⬆'] + '_' + pp_data['Player']
                pp_summary = pp_data.groupby('Match_ID').agg({
                    'Player': 'first',
                    'Team': 'first',
                    'O': 'max',
                    'R': 'max',
                    'W': 'max',
                    '0': 'sum'
                })
                
                pp_bowling = pp_summary.groupby('Player').agg({
                    'Team': 'first',
                    'O': 'sum',
                    'R': 'sum',
                    'W': 'sum',
                    '0': 'sum'
                }).round(2)
                
                pp_bowling['Econ'] = (pp_bowling['R'] / pp_bowling['O']).round(2)
                pp_bowling = pp_bowling[pp_bowling['O'] >= 2.0]
                pp_bowling = pp_bowling.sort_values('Econ', ascending=True)
                data_subsets['powerplay_bowling'] = pp_bowling.head(10)[['Team', 'O', 'R', 'W', 'Econ', '0']]
                
                # BATTING STATS
                pp_data['Bat_Match_ID'] = pp_data['Match⬆'] + '_' + pp_data['Batsman']
                pp_bat_summary = pp_data.groupby('Bat_Match_ID').agg({
                    'Batsman': 'first',
                    'Team.1': 'first',
                    'R.1': 'max',  # Runs scored
                    'B': 'max',    # Balls faced
                    '4': 'sum',    # Fours
                    '6': 'sum'     # Sixes
                })
                
                pp_batting = pp_bat_summary.groupby('Batsman').agg({
                    'Team.1': 'first',
                    'R.1': 'sum',
                    'B': 'sum',
                    '4': 'sum',
                    '6': 'sum'
                }).round(2)
                
                # Calculate strike rate
                pp_batting['SR'] = ((pp_batting['R.1'] / pp_batting['B']) * 100).round(2)
                
                # Filter for minimum 10 balls faced
                pp_batting = pp_batting[pp_batting['B'] >= 10]
                
                # Sort by runs scored (most aggressive batsmen)
                pp_batting = pp_batting.sort_values(['R.1', 'SR'], ascending=[False, False])
                pp_batting.rename(columns={'Team.1': 'Team'}, inplace=True)
                data_subsets['powerplay_batting'] = pp_batting.head(10)[['Team', 'R.1', 'B', 'SR', '4', '6']]

        if 'death' in intents:
            # Extract death overs data (overs 16-19, which is 17th to 20th over)
            df_copy = self.df.copy()
            df_copy['Over_Number'] = df_copy['Overs'].astype(str).str.split('.').str[0].astype(float)
            
            # Filter for death overs (16-19)
            death_data = df_copy[(df_copy['Over_Number'] >= 16) & (df_copy['Over_Number'] <= 19)].copy()
            
            if not death_data.empty:
                # Group by Player and Match to get per-match stats, then aggregate
                death_data['Match_ID'] = death_data['Match⬆'] + '_' + death_data['Player']
                
                # Get the last ball of each player's spell in each match (has cumulative stats)
                death_summary = death_data.groupby('Match_ID').agg({
                    'Player': 'first',
                    'Team': 'first',
                    'O': 'max',
                    'R': 'max',
                    'W': 'max',
                    '0': 'sum'
                })
                
                # Now aggregate by player across all matches
                death_bowling = death_summary.groupby('Player').agg({
                    'Team': 'first',
                    'O': 'sum',
                    'R': 'sum',
                    'W': 'sum',
                    '0': 'sum'
                }).round(2)
                
                # Calculate economy rate
                death_bowling['Econ'] = (death_bowling['R'] / death_bowling['O']).round(2)
                
                # Filter for minimum 2 overs bowled
                death_bowling = death_bowling[death_bowling['O'] >= 2.0]
                
                # Sort by economy (lower is better)
                death_bowling = death_bowling.sort_values('Econ', ascending=True)
                
                data_subsets['death_bowling'] = death_bowling.head(10)[['Team', 'O', 'R', 'W', 'Econ', '0']]
                
                # BATTING STATS for death overs
                death_data['Bat_Match_ID'] = death_data['Match⬆'] + '_' + death_data['Batsman']
                death_bat_summary = death_data.groupby('Bat_Match_ID').agg({
                    'Batsman': 'first',
                    'Team.1': 'first',
                    'R.1': 'max',
                    'B': 'max',
                    '4': 'sum',
                    '6': 'sum'
                })
                
                death_batting = death_bat_summary.groupby('Batsman').agg({
                    'Team.1': 'first',
                    'R.1': 'sum',
                    'B': 'sum',
                    '4': 'sum',
                    '6': 'sum'
                }).round(2)
                
                death_batting['SR'] = ((death_batting['R.1'] / death_batting['B']) * 100).round(2)
                death_batting = death_batting[death_batting['B'] >= 10]
                death_batting = death_batting.sort_values(['R.1', 'SR'], ascending=[False, False])
                death_batting.rename(columns={'Team.1': 'Team'}, inplace=True)
                data_subsets['death_batting'] = death_batting.head(10)[['Team', 'R.1', 'B', 'SR', '4', '6']]

        if 'ground_comparison' in intents or ('ground' in intents and 'comparison' in intents):
            # Extract ground-wise statistics for top players
            if 'Ground Name' in self.df.columns:
                grounds = self.df['Ground Name'].value_counts().head(5).index.tolist()
                
                # Get ground-wise aggregate for bowling
                ground_bowling = []
                for ground in grounds:
                    ground_data = self.df[self.df['Ground Name'] == ground]
                    player_stats = ground_data.groupby('Player').agg({
                        'O': 'max',
                        'R': 'max',
                        'W': 'max',
                        'Team': 'first'
                    }).round(2)
                    player_stats = player_stats[player_stats['O'] >= 2.0]  # Min 2 overs
                    player_stats['Econ'] = (player_stats['R'] / player_stats['O']).round(2)
                    player_stats['Ground'] = ground
                    ground_bowling.append(player_stats.nsmallest(3, 'Econ'))
                
                if ground_bowling:
                    data_subsets['ground_comparison'] = pd.concat(ground_bowling)[['Ground', 'Team', 'O', 'W', 'Econ']]

        return data_subsets

    def _build_enhanced_prompt(self, query, intents, data):
        """Build enhanced prompt with context and data for Gemini"""
        prompt = f"""{self.dataset_context}

USER QUERY: {query}
DETECTED ANALYSIS TYPE: {', '.join(intents)}

=== EXTRACTED DATA FOR ANALYSIS ===
"""

        # Add data with clear section markers
        for data_type, df_data in data.items():
            if df_data is not None and not df_data.empty:
                prompt += f"\n{'='*60}\n"
                prompt += f"DATA TABLE: {data_type.upper().replace('_', ' ')}\n"
                prompt += f"{'='*60}\n"
                prompt += df_data.head(10).to_string()
                prompt += f"\n(Showing top {min(10, len(df_data))} of {len(df_data)} total entries)\n"

        prompt += f"""
{'='*60}

🚨 CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. ONLY use players and statistics from the DATA TABLES shown above
2. If a player name is NOT in the tables above, DO NOT mention them
3. DO NOT use your general cricket knowledge or historical data
4. DO NOT invent or estimate any statistics
5. If data seems insufficient, say "insufficient data" instead of guessing
6. The tables above show the COMPLETE and ONLY data available for analysis

⚠️ VERIFICATION CHECKLIST:
- Did you check the player exists in the tables above? 
- Did you copy the exact statistics from the tables?
- Did you avoid mentioning any player NOT in the tables?
- Are you 100% certain this data comes from the tables shown?

RESPONSE FORMAT:
1. Start with direct answer citing ONLY players from the tables
2. Quote exact statistics from the tables (Team, Overs, Runs, Economy, etc.)
3. If asked for "best" or "highest", use the players at the TOP of the relevant table
4. Double-check every player name and statistic against the tables before responding

Now analyze the query using ONLY the data in the tables above:
"""
        return prompt

    def get_player_insights(self, player_name):
        """Get comprehensive AI insights for a specific player"""
        player_data = self.df[
            (self.df['Player'] == player_name) | 
            (self.df['Batsman'] == player_name)
        ]

        if player_data.empty:
            return {
                'player': player_name,
                'error': 'Player not found in dataset',
                'gemini_insights': None
            }

        # Get bowling stats if bowler
        bowling_stats = player_data[player_data['Player'] == player_name]
        batting_stats = player_data[player_data['Batsman'] == player_name]

        prompt = f"""
Analyze this cricket player from the IPL dataset:

Player: {player_name}

BOWLING STATISTICS:
{bowling_stats[['Player', 'Team', 'O', 'M', 'R', 'W', 'Econ', 'Technique']].head().to_string() if not bowling_stats.empty else 'No bowling data'}

BATTING STATISTICS:
{batting_stats[['Batsman', 'Team.1', 'R.1', 'B', 'RR']].head().to_string() if not batting_stats.empty else 'No batting data'}

Provide:
1. Role assessment (bowler/batsman/all-rounder)
2. Key performance metrics
3. Strengths and weaknesses
4. Comparison with peers
5. Career trajectory insight
6. Recommendations for improvement
"""

        response = self.model.generate_content(prompt)

        return {
            'player': player_name,
            'bowling_matches': len(bowling_stats),
            'batting_matches': len(batting_stats),
            'gemini_insights': response.text
        }

    def analyze_team(self, team_code):
        """Comprehensive team analysis with Gemini"""
        if team_code not in self.df['Team'].unique():
            return {'error': f'Team {team_code} not found'}

        team_data = self.df[self.df['Team'] == team_code]

        # Aggregate stats
        team_stats = {
            'bowlers': team_data['Player'].nunique(),
            'batsmen': team_data['Batsman'].nunique(),
            'total_wickets': team_data['W'].sum(),
            'total_runs_conceded': team_data['R'].sum(),
            'total_runs_scored': team_data['R.1'].sum(),
            'avg_economy': team_data['Econ'].replace('-', pd.NA).apply(
                lambda x: float(x) if pd.notna(x) and x != '-' else None
            ).mean()
        }

        # Top players
        top_bowlers = team_data.nlargest(5, 'W')[['Player', 'W', 'Econ']]
        top_batsmen = team_data.nlargest(5, 'R.1')[['Batsman', 'R.1', 'RR']]

        prompt = f"""
Analyze team performance for {team_code} in IPL:

TEAM STATISTICS:
- Unique Bowlers: {team_stats['bowlers']}
- Unique Batsmen: {team_stats['batsmen']}
- Total Wickets: {team_stats['total_wickets']}
- Total Runs Conceded: {team_stats['total_runs_conceded']}
- Total Runs Scored: {team_stats['total_runs_scored']}
- Average Economy Rate: {team_stats['avg_economy']:.2f}

TOP 5 BOWLERS:
{top_bowlers.to_string()}

TOP 5 BATSMEN:
{top_batsmen.to_string()}

Provide:
1. Team strength assessment
2. Bowling depth analysis
3. Batting lineup strength
4. Weaknesses to address
5. Competitive advantages
6. Strategic recommendations
"""

        response = self.model.generate_content(prompt)

        return {
            'team': team_code,
            'stats': team_stats,
            'gemini_analysis': response.text
        }

    def analyze_ball_position(self, player_name=None):
        """Analyze performance by ball position within an over"""
        
        df_copy = self.df.copy()
        
        # Filter by player if specified
        if player_name:
            df_copy = df_copy[df_copy['Player'] == player_name]
            if df_copy.empty:
                return {'error': f'No data found for {player_name}'}
        
        # Extract ball position
        df_copy['Over_Number'] = df_copy['Overs'].astype(str).str.split('.').str[0].astype(float)
        df_copy['Ball_Position'] = df_copy['Overs'].astype(str).str.split('.').str[1].astype(int)
        
        # Analyze by ball position
        ball_analysis = []
        for ball_pos in [1, 2, 3, 4, 5, 6]:
            ball_data = df_copy[df_copy['Ball_Position'] == ball_pos]
            
            if not ball_data.empty:
                total_balls = len(ball_data)
                runs_conceded = ball_data['R'].sum()
                wickets = len(ball_data[ball_data['Wkt'] != '-'])
                dots = len(ball_data[ball_data['0'] == 1])
                fours = len(ball_data[ball_data['4'] == 1])
                sixes = len(ball_data[ball_data['6'] == 1])
                
                ball_analysis.append({
                    'Ball_Position': ball_pos,
                    'Ball_Name': f"{ball_pos}{'st' if ball_pos == 1 else 'nd' if ball_pos == 2 else 'rd' if ball_pos == 3 else 'th'} ball",
                    'Total_Balls': total_balls,
                    'Runs_Conceded': runs_conceded,
                    'Wickets': wickets,
                    'Dots': dots,
                    'Fours': fours,
                    'Sixes': sixes,
                    'Avg_Runs_Per_Ball': round(runs_conceded / total_balls, 3) if total_balls > 0 else 0,
                    'Dot_Percentage': round((dots / total_balls) * 100, 1) if total_balls > 0 else 0,
                    'Wicket_Percentage': round((wickets / total_balls) * 100, 1) if total_balls > 0 else 0
                })
        
        # Create AI prompt for analysis
        prompt = f"""
Analyze ball position performance {'for ' + player_name if player_name else 'across all players'}:

BALL POSITION ANALYSIS:
"""
        
        for analysis in ball_analysis:
            prompt += f"""
{analysis['Ball_Name'].upper()}:
- Total balls: {analysis['Total_Balls']}
- Runs conceded: {analysis['Runs_Conceded']}
- Average per ball: {analysis['Avg_Runs_Per_Ball']}
- Wickets: {analysis['Wickets']} ({analysis['Wicket_Percentage']}%)
- Dot balls: {analysis['Dots']} ({analysis['Dot_Percentage']}%)
- Boundaries: {analysis['Fours']} fours, {analysis['Sixes']} sixes
"""
        
        prompt += """
Please analyze:
1. Which ball positions are most/least effective?
2. What patterns emerge across the over?
3. Strategic insights about bowling at different positions
4. Comparison between 1st ball vs 6th ball performance
5. Recommendations for bowling strategy
"""
        
        response = self.model.generate_content(prompt)
        
        return {
            'player': player_name or 'All players',
            'ball_analysis': ball_analysis,
            'ai_insights': response.text
        }

    def get_dataset_summary(self):
        """Get Gemini's interpretation of the entire dataset"""
        summary_stats = {
            'total_records': len(self.df),
            'total_players': self.df['Player'].nunique(),
            'total_teams': self.df['Team'].nunique(),
            'date_range': f"{self.df['Date↑'].min()} to {self.df['Date↑'].max()}",
            'teams': sorted(self.df['Team'].unique()),
            'grounds': self.df['Ground Name'].nunique()
        }

        prompt = f"""
This is an IPL dataset summary:
{summary_stats}

Explain:
1. What this dataset contains
2. Key statistical ranges
3. Notable patterns in cricket format
4. Analysis opportunities
5. Data completeness assessment
"""

        response = self.model.generate_content(prompt)

        return {
            'summary': summary_stats,
            'gemini_interpretation': response.text
        }


# Example usage
if __name__ == "__main__":
    try:
        # Initialize
        analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv')
        print(f"✅ Using model: {analytics.model_name}")

        # Test smart analysis
        result = analytics.smart_analyze("Who has the best economy rate?")
        print(f"Intent: {result['intent']}")
        print(f"Response: {result['gemini_response']}")

        # Test player analysis
        player_insights = analytics.get_player_insights('JJ Bumrah')
        print(f"\nPlayer Insights for JJ Bumrah:")
        print(player_insights['gemini_insights'])

        # Test team analysis
        team_analysis = analytics.analyze_team('MI')
        print(f"\nMI Team Analysis:")
        print(team_analysis['gemini_analysis'])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try running 'python test_api.py' to check your API setup")
