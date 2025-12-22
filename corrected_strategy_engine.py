"""
Corrected IPL Strategy Engine - Handles Cumulative Data Properly
"""

import pandas as pd
import numpy as np

class CorrectedIPLStrategyEngine:
    """Strategy engine that correctly handles cumulative data"""
    
    def __init__(self, filters=None):
        self.df = pd.read_csv('ipl_data.csv')
        self.filters = filters or {}
        
        self._prepare_data()
        self._apply_filters()
    
    def _prepare_data(self):
        """Prepare data by calculating actual runs per ball from cumulative data"""
        
        # Convert date
        self.df['date'] = pd.to_datetime(self.df['Date⬆'])
        self.df['year'] = self.df['date'].dt.year
        
        # Extract over info
        self.df['over_num'] = self.df['Overs'].astype(str).str.split('.').str[0].astype(float)
        self.df['ball_num'] = self.df['Overs'].astype(str).str.split('.').str[1].astype(float)
        self.df['phase'] = self.df['over_num'].apply(lambda x: 'Powerplay' if x <= 6 else 'Post Powerplay')
        
        # Sort by match, innings, and overs to ensure proper sequence
        self.df = self.df.sort_values(['Match⬆', 'I#', 'Overs']).reset_index(drop=True)
        
        # Calculate actual runs per ball from cumulative R.1 (batsman runs)
        self.df['runs_this_ball'] = 0
        
        # Group by match, innings, and batsman to calculate differences
        for (match, innings, batsman), group in self.df.groupby(['Match⬆', 'I#', 'Batsman']):
            if len(group) > 1:
                # Calculate difference between consecutive cumulative runs
                group = group.sort_values('Overs')
                runs_diff = group['R.1'].diff().fillna(group['R.1'].iloc[0])
                
                # Update the main dataframe
                self.df.loc[group.index, 'runs_this_ball'] = runs_diff
            else:
                # Single ball - use the cumulative value as actual runs
                self.df.loc[group.index, 'runs_this_ball'] = group['R.1'].iloc[0]
        
        # Ensure no negative runs (data quality check)
        self.df['runs_this_ball'] = self.df['runs_this_ball'].clip(lower=0)
        
        # Bowler categories
        style_mapping = {
            'right pace': 'RAF',
            'left pace': 'LAF', 
            'left orthodox': 'LAO',
            'off break': 'Off Break',
            'leg break': 'Leg Spin'
        }
        
        self.df['bowler_category'] = self.df['Technique'].fillna('Unknown').str.lower().map(style_mapping).fillna('Other')
        
        print(f"✅ Data prepared: {len(self.df)} records")
        print(f"📊 Average runs per ball: {self.df['runs_this_ball'].mean():.2f}")
        print(f"📊 Runs per ball distribution: {self.df['runs_this_ball'].value_counts().sort_index().to_dict()}")
    
    def _apply_filters(self):
        """Apply filters"""
        original_size = len(self.df)
        
        if 'season' in self.filters:
            self.df = self.df[self.df['year'] == self.filters['season']]
            print(f"📅 Season {self.filters['season']}: {len(self.df)} records")
        
        if 'ground' in self.filters:
            self.df = self.df[self.df['Ground Name'].str.contains(self.filters['ground'], case=False, na=False)]
            print(f"🏟️ Ground filter: {len(self.df)} records")
        
        if 'opposition' in self.filters:
            self.df = self.df[self.df['Team'] == self.filters['opposition']]
            print(f"🏏 Opposition filter: {len(self.df)} records")
        
        if 'min_balls' in self.filters:
            # Filter batsman-bowler combinations with minimum balls
            combo_counts = self.df.groupby(['Batsman', 'bowler_category']).size()
            valid_combos = combo_counts[combo_counts >= self.filters['min_balls']].index
            
            mask = self.df.set_index(['Batsman', 'bowler_category']).index.isin(valid_combos)
            self.df = self.df[mask]
            print(f"📊 Min balls filter: {len(self.df)} records")
        
        print(f"📊 Final dataset: {len(self.df)} records")
    
    def generate_scouting_brief(self, batsman_name, bowler_type='RAF', min_balls=20):
        """Generate accurate scouting brief with corrected calculations"""
        
        print(f"🎯 Scouting Brief: {batsman_name} vs {bowler_type}")
        print(f"Filters: {self.filters}")
        print("=" * 50)
        
        # Filter data
        data = self.df[
            (self.df['Batsman'] == batsman_name) & 
            (self.df['bowler_category'] == bowler_type)
        ].copy()
        
        if data.empty:
            return f"❌ No data found for {batsman_name} vs {bowler_type}"
        
        if len(data) < min_balls:
            return f"❌ Insufficient data: {len(data)} balls (need {min_balls}+)"
        
        # Calculate accurate metrics
        total_balls = len(data)
        total_runs = data['runs_this_ball'].sum()
        strike_rate = (total_runs / total_balls) * 100
        
        # Boundaries and dots (using the indicator columns)
        dots = len(data[data['0'] == 1])
        fours = len(data[data['4'] == 1])
        sixes = len(data[data['6'] == 1])
        dismissals = len(data[data['Wkt'] != '-'])
        
        # Phase analysis
        pp_data = data[data['phase'] == 'Powerplay']
        post_pp_data = data[data['phase'] == 'Post Powerplay']
        
        pp_runs = pp_data['runs_this_ball'].sum()
        pp_balls = len(pp_data)
        pp_sr = (pp_runs / pp_balls * 100) if pp_balls > 0 else 0
        
        post_pp_runs = post_pp_data['runs_this_ball'].sum()
        post_pp_balls = len(post_pp_data)
        post_pp_sr = (post_pp_runs / post_pp_balls * 100) if post_pp_balls > 0 else 0
        
        # Generate brief
        brief = f"""
# {batsman_name.upper()} VS {bowler_type} BOWLERS
{'=' * 50}

## FILTER CONTEXT
{self._format_filters()}

## OVERVIEW
- Total balls faced: {total_balls}
- Total runs scored: {total_runs}
- Strike Rate: {strike_rate:.1f}
- Dismissals: {dismissals} ({dismissals/total_balls*100:.1f}%)

## BOUNDARY ANALYSIS
- Dot balls: {dots} ({dots/total_balls*100:.1f}%)
- Fours: {fours} ({fours/total_balls*100:.1f}%)
- Sixes: {sixes} ({sixes/total_balls*100:.1f}%)
- Boundary %: {(fours+sixes)/total_balls*100:.1f}%

## PHASE COMPARISON
### POWERPLAY (Overs 1-6)
- Balls: {pp_balls}
- Runs: {pp_runs}
- Strike Rate: {pp_sr:.1f}
- Dots: {len(pp_data[pp_data['0'] == 1])} ({len(pp_data[pp_data['0'] == 1])/pp_balls*100:.1f}%)
- Boundaries: {len(pp_data[pp_data['4'] == 1]) + len(pp_data[pp_data['6'] == 1])}

### POST POWERPLAY (Overs 7-20)
- Balls: {post_pp_balls}
- Runs: {post_pp_runs}
- Strike Rate: {post_pp_sr:.1f}
- Dots: {len(post_pp_data[post_pp_data['0'] == 1])} ({len(post_pp_data[post_pp_data['0'] == 1])/post_pp_balls*100:.1f}%)
- Boundaries: {len(post_pp_data[post_pp_data['4'] == 1]) + len(post_pp_data[post_pp_data['6'] == 1])}

## LENGTH ANALYSIS
{self._analyze_by_length(data)}

## ZONE ANALYSIS
{self._analyze_by_zone(data)}

## TACTICAL SUMMARY
### DATA QUALITY
- Sample size: {total_balls} balls
- Reliability: {'High' if total_balls >= 50 else 'Medium' if total_balls >= 30 else 'Low'}

### KEY INSIGHTS
- Preferred phase: {'Powerplay' if pp_sr > post_pp_sr else 'Post-Powerplay'} (SR: {max(pp_sr, post_pp_sr):.1f})
- Weakness: {'Powerplay' if pp_sr < post_pp_sr else 'Post-Powerplay'} (SR: {min(pp_sr, post_pp_sr):.1f})
- Dot ball rate: {dots/total_balls*100:.1f}% ({'Low' if dots/total_balls < 0.3 else 'Average' if dots/total_balls < 0.5 else 'High'})
- Boundary threat: {'High' if (fours+sixes)/total_balls > 0.25 else 'Medium' if (fours+sixes)/total_balls > 0.15 else 'Low'}

### BOWLING STRATEGY
- Target phase: {'Powerplay' if pp_sr < post_pp_sr else 'Post-Powerplay'} (exploit weakness)
- Primary goal: {'Dot balls' if dots/total_balls < 0.4 else 'Wickets'} (current dot rate: {dots/total_balls*100:.1f}%)
- Boundary prevention: {'Critical' if (fours+sixes)/total_balls > 0.2 else 'Standard'} priority
"""
        
        return brief
    
    def _format_filters(self):
        """Format filters for display"""
        if not self.filters:
            return "All data (no filters applied)"
        
        parts = []
        if 'season' in self.filters:
            parts.append(f"Season {self.filters['season']}")
        if 'ground' in self.filters:
            parts.append(f"Ground: {self.filters['ground']}")
        if 'opposition' in self.filters:
            parts.append(f"vs {self.filters['opposition']}")
        if 'min_balls' in self.filters:
            parts.append(f"Min {self.filters['min_balls']} balls")
        
        return " | ".join(parts)
    
    def _analyze_by_length(self, data):
        """Analyze performance by ball length"""
        if 'Length' not in data.columns:
            return "Length data not available"
        
        length_analysis = []
        for length in data['Length'].dropna().unique():
            if length == '-':
                continue
            
            length_data = data[data['Length'] == length]
            if len(length_data) >= 3:  # Minimum 3 balls
                runs = length_data['runs_this_ball'].sum()
                balls = len(length_data)
                sr = (runs / balls) * 100
                dots = len(length_data[length_data['0'] == 1])
                
                length_analysis.append(f"- {length}: SR {sr:.1f} ({balls} balls, {dots} dots)")
        
        return "\n".join(sorted(length_analysis)) if length_analysis else "Insufficient data for length analysis"
    
    def _analyze_by_zone(self, data):
        """Analyze performance by scoring zone"""
        if 'Zone' not in data.columns:
            return "Zone data not available"
        
        zone_analysis = []
        for zone in data['Zone'].dropna().unique():
            if zone == '-':
                continue
            
            zone_data = data[data['Zone'] == zone]
            if len(zone_data) >= 3:  # Minimum 3 balls
                runs = zone_data['runs_this_ball'].sum()
                balls = len(zone_data)
                sr = (runs / balls) * 100
                boundaries = len(zone_data[(zone_data['4'] == 1) | (zone_data['6'] == 1)])
                
                zone_analysis.append(f"- Zone {zone}: SR {sr:.1f} ({balls} balls, {boundaries} boundaries)")
        
        # Sort by strike rate (descending)
        zone_analysis.sort(key=lambda x: float(x.split('SR ')[1].split(' ')[0]), reverse=True)
        
        return "\n".join(zone_analysis[:5]) if zone_analysis else "Insufficient data for zone analysis"  # Top 5 zones
    
    def get_sample_data(self, batsman_name, bowler_type, n=10):
        """Get sample data for verification"""
        data = self.df[
            (self.df['Batsman'] == batsman_name) & 
            (self.df['bowler_category'] == bowler_type)
        ].head(n)
        
        return data[['Batsman', 'Player', 'Overs', 'R.1', 'runs_this_ball', '0', '4', '6', 'Length', 'Zone']]

def main():
    """Test the corrected engine"""
    
    print("🏏 Testing Corrected Strategy Engine")
    print("=" * 50)
    
    # Test with 2024 season filter
    filters = {'season': 2024, 'min_balls': 30}
    engine = CorrectedIPLStrategyEngine(filters)
    
    # Show sample data for verification
    print("\n📊 Sample data verification:")
    sample = engine.get_sample_data('V Kohli', 'RAF', 5)
    print(sample.to_string())
    
    # Generate brief
    print("\n" + "="*60)
    brief = engine.generate_scouting_brief('V Kohli', 'RAF', 30)
    print(brief)

if __name__ == "__main__":
    main()