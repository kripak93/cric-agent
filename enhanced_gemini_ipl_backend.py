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

    def __init__(self, csv_path, api_key=None, model_name='gemini-2.5-flash', season_filter=None):
        """Initialize with CSV data and Gemini API"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env or pass as argument.")

        genai.configure(api_key=self.api_key)
        
        # Try the specified model, fallback to alternatives if needed
        try:
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name
        except Exception as e:
            print(f"Warning: {model_name} not available, trying gemini-2.5-flash-lite...")
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
                self.model_name = 'gemini-2.5-flash-lite'
            except Exception as e2:
                raise ValueError(f"No compatible Gemini models available. Error: {e2}")

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

        # Step 4: Get Gemini Response
        response = self.model.generate_content(prompt)

        return {
            'query': query,
            'intent': intent,
            'gemini_response': response.text,
            'data_extracted': len(data) if data is not None else 0
        }

    def _detect_intent(self, query):
        """Detect user's intent from query"""
        query_lower = query.lower()

        intent_keywords = {
            'economy': ['best economy', 'lowest economy', 'most economical', 'efficient bowler'],
            'wickets': ['most wickets', 'top wicket', 'highest wickets', 'best bowler'],
            'batting': ['best batsman', 'highest runs', 'strike rate', 'aggressive'],
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
            # Get top 10 by economy (lowest is best) with minimum workload
            valid_econ = self.df[self.df['Econ'] != '-'].copy()
            valid_econ['Econ'] = pd.to_numeric(valid_econ['Econ'], errors='coerce')
            # Filter for minimum 2 overs to get meaningful results
            valid_econ = valid_econ[valid_econ['O'] >= 2.0]
            data_subsets['economy'] = valid_econ.nsmallest(10, 'Econ')[
                ['Player', 'Team', 'O', 'R', 'W', 'Econ']
            ]

        if 'wickets' in intents:
            # Get top 10 by wickets with minimum workload
            valid_wickets = self.df[self.df['O'] >= 1.0]  # Minimum 1 over
            data_subsets['wickets'] = valid_wickets.nlargest(10, 'W')[
                ['Player', 'Team', 'O', 'W', 'R', 'Econ']
            ]

        if 'batting' in intents:
            # Get top 10 batsmen by runs with minimum workload
            valid_batting = self.df[self.df['B'] >= 10]  # Minimum 10 balls faced
            data_subsets['batting'] = valid_batting.nlargest(10, 'R.1')[
                ['Batsman', 'Team.1', 'R.1', 'B', 'RR']
            ]

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
                # Group by Player and Match to get per-match stats, then aggregate
                # This prevents counting cumulative stats multiple times
                pp_data['Match_ID'] = pp_data['Match⬆'] + '_' + pp_data['Player']
                
                # Get the last ball of each player's spell in each match (has cumulative stats)
                pp_summary = pp_data.groupby('Match_ID').agg({
                    'Player': 'first',
                    'Team': 'first',
                    'O': 'max',  # Overs bowled in powerplay
                    'R': 'max',  # Runs conceded (cumulative max)
                    'W': 'max',  # Wickets taken (cumulative max)
                    '0': 'sum'   # Count of dot balls
                })
                
                # Now aggregate by player across all matches
                pp_bowling = pp_summary.groupby('Player').agg({
                    'Team': 'first',
                    'O': 'sum',     # Total overs in powerplay
                    'R': 'sum',     # Total runs conceded
                    'W': 'sum',     # Total wickets
                    '0': 'sum'      # Total dot balls
                }).round(2)
                
                # Calculate economy rate
                pp_bowling['Econ'] = (pp_bowling['R'] / pp_bowling['O']).round(2)
                
                # Filter for minimum 2 overs bowled
                pp_bowling = pp_bowling[pp_bowling['O'] >= 2.0]
                
                # Sort by economy (lower is better)
                pp_bowling = pp_bowling.sort_values('Econ', ascending=True)
                
                data_subsets['powerplay'] = pp_bowling.head(10)[['Team', 'O', 'R', 'W', 'Econ', '0']]

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
                
                data_subsets['death'] = death_bowling.head(10)[['Team', 'O', 'R', 'W', 'Econ', '0']]

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

EXTRACTED DATA FOR ANALYSIS:
"""

        for data_type, df_data in data.items():
            if df_data is not None and not df_data.empty:
                prompt += f"\n{data_type.upper()}:\n"
                prompt += df_data.head(10).to_string()
                prompt += "\n"

        prompt += """
CRITICAL INSTRUCTIONS:
- ONLY use data from the tables above - DO NOT use external cricket knowledge
- ONLY mention players that appear in the provided data
- ONLY use statistics from the provided dataset
- If a player is not in the data above, DO NOT mention them
- Base ALL analysis strictly on the provided statistics

ANALYSIS TASK:
1. Analyze ONLY the above data based on the user's query
2. Provide insights using ONLY the statistics shown above
3. Compare players using ONLY the data provided
4. Do not reference any cricket knowledge outside this dataset
5. If insufficient data, say so rather than using external knowledge

RESPONSE FORMAT:
- Start with direct answer using ONLY the provided data
- Show supporting statistics from the tables above
- Highlight findings from the actual data shown
- Compare using only the players and stats provided
- End with insights based strictly on this dataset

Please provide analysis using ONLY the data shown above:
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
