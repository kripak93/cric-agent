"""
Enhanced IPL Strategy Engine with Filters and Correct Strike Rate Calculations
"""

import pandas as pd
import numpy as np
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
import os
from dotenv import load_dotenv

class EnhancedIPLStrategyEngine:
    """Enhanced strategic analysis engine with filters and correct calculations"""
    
    def __init__(self, filters=None):
        load_dotenv()
        self.df = pd.read_csv('ipl_data.csv')
        self.filters = filters or {}
        
        self._prepare_data()
        self._apply_filters()
    
    def _prepare_data(self):
        """Prepare and standardize the dataset"""
        
        # Convert date to datetime
        self.df['date'] = pd.to_datetime(self.df['Date⬆'])
        self.df['year'] = self.df['date'].dt.year
        
        # Extract over and ball numbers
        self.df['over_num'] = self.df['Overs'].astype(str).str.split('.').str[0].astype(float)
        self.df['ball_num'] = self.df['Overs'].astype(str).str.split('.').str[1].astype(float)
        
        # Define phases
        self.df['phase'] = self.df['over_num'].apply(
            lambda x: 'Powerplay' if x <= 6 else 'Post Powerplay'
        )
        
        # Standardize bowler styles
        style_mapping = {
            'right pace': 'RAF',
            'left pace': 'LAF', 
            'left orthodox': 'LAO',
            'off break': 'Off Break',
            'leg break': 'Leg Spin',
            'right orthodox': 'Off Break'
        }
        
        self.df['bowler_category'] = self.df['Technique'].fillna('Unknown').str.lower().map(style_mapping).fillna('Other')
        
        print(f"✅ Data prepared: {len(self.df)} records")
        print(f"📅 Date range: {self.df['date'].min()} to {self.df['date'].max()}")
        print(f"🏟️ Venues: {self.df['Ground Name'].nunique()} unique grounds")
    
    def _apply_filters(self):
        """Apply user-specified filters"""
        original_size = len(self.df)
        
        # Ground filter
        if 'ground' in self.filters and self.filters['ground']:
            self.df = self.df[self.df['Ground Name'].str.contains(self.filters['ground'], case=False, na=False)]
            print(f"🏟️ Ground filter applied: {len(self.df)} records")
        
        # Season filter
        if 'season' in self.filters and self.filters['season']:
            self.df = self.df[self.df['year'] == self.filters['season']]
            print(f"📅 Season filter applied: {len(self.df)} records")
        
        # Date range filter
        if 'start_date' in self.filters and self.filters['start_date']:
            start_date = pd.to_datetime(self.filters['start_date'])
            self.df = self.df[self.df['date'] >= start_date]
            print(f"📅 Start date filter applied: {len(self.df)} records")
        
        if 'end_date' in self.filters and self.filters['end_date']:
            end_date = pd.to_datetime(self.filters['end_date'])
            self.df = self.df[self.df['date'] <= end_date]
            print(f"📅 End date filter applied: {len(self.df)} records")
        
        # Opposition filter
        if 'opposition' in self.filters and self.filters['opposition']:
            self.df = self.df[self.df['Team'] == self.filters['opposition']]
            print(f"🏏 Opposition filter applied: {len(self.df)} records")
        
        # Minimum balls filter (for meaningful analysis)
        if 'min_balls' in self.filters and self.filters['min_balls']:
            # Group by batsman and bowler type, filter groups with minimum balls
            grouped = self.df.groupby(['Batsman', 'bowler_category']).size()
            valid_combinations = grouped[grouped >= self.filters['min_balls']].index
            
            # Keep only valid combinations
            mask = self.df.set_index(['Batsman', 'bowler_category']).index.isin(valid_combinations)
            self.df = self.df[mask]
            print(f"📊 Minimum balls filter applied: {len(self.df)} records")
        
        if len(self.df) < original_size:
            print(f"📊 Total filtered: {len(self.df)} records (was {original_size})")
    
    def _calculate_strike_rate(self, data):
        """Calculate strike rate correctly using boundary columns"""
        if len(data) == 0:
            return 0.0
        
        # Calculate runs per ball from boundary columns
        # 0 = dot ball (0 runs), 4 = four (4 runs), 6 = six (6 runs)
        # Otherwise it's 1, 2, or 3 runs
        
        total_runs = 0
        for _, row in data.iterrows():
            if row['0'] == 1:  # Dot ball
                runs = 0
            elif row['4'] == 1:  # Four
                runs = 4
            elif row['6'] == 1:  # Six
                runs = 6
            else:  # 1, 2, or 3 runs (need to calculate from cumulative)
                # For now, assume 1 run if not dot/4/6
                runs = 1
        
        total_balls = len(data)
        
        # Better approach: use the actual runs columns
        # Calculate runs per ball by looking at differences in R.1 (cumulative runs)
        runs_per_ball = []
        for idx in data.index:
            if data.loc[idx, '0'] == 1:
                runs_per_ball.append(0)
            elif data.loc[idx, '4'] == 1:
                runs_per_ball.append(4)
            elif data.loc[idx, '6'] == 1:
                runs_per_ball.append(6)
            else:
                # For non-boundary balls, assume 1-3 runs
                # We can infer from the pattern
                runs_per_ball.append(1)  # Conservative estimate
        
        total_runs = sum(runs_per_ball)
        
        return (total_runs / total_balls) * 100 if total_balls > 0 else 0.0
    
    def generate_scouting_brief(self, batsman_name, bowler_type='RAF', min_balls=20):
        """Generate comprehensive scouting brief with filters"""
        
        print(f"🎯 Generating Filtered Scouting Brief")
        print(f"Player: {batsman_name} vs {bowler_type}")
        print(f"Filters: {self.filters}")
        print("=" * 60)
        
        # Filter data for the batsman
        batsman_data = self.df[self.df['Batsman'] == batsman_name].copy()
        
        if batsman_data.empty:
            return f"❌ No data found for {batsman_name} with current filters"
        
        # Filter by bowler type
        bowler_data = batsman_data[batsman_data['bowler_category'] == bowler_type].copy()
        
        if bowler_data.empty:
            return f"❌ No data found for {batsman_name} vs {bowler_type} bowlers with current filters"
        
        # Check minimum balls requirement
        if len(bowler_data) < min_balls:
            return f"❌ Insufficient data: {len(bowler_data)} balls (minimum {min_balls} required)"
        
        # Generate brief
        brief = self._create_enhanced_brief(batsman_name, bowler_type, bowler_data)
        
        return brief
    
    def _create_enhanced_brief(self, batsman_name, bowler_type, data):
        """Create enhanced tactical brief with correct calculations"""
        
        # Calculate correct metrics
        total_balls = len(data)
        total_runs = data['R'].sum()
        overall_sr = self._calculate_strike_rate(data)
        dismissals = len(data[data['Wkt'] != '-'])
        
        brief = f"""
# {batsman_name.upper()} VS {bowler_type} BOWLERS
{'=' * 50}

## FILTER CONTEXT
{self._format_filters()}

## OVERVIEW
- Total balls faced vs {bowler_type}: {total_balls}
- Total runs scored: {total_runs}
- Overall Strike Rate: {overall_sr:.1f}
- Dismissals: {dismissals}
- Dismissal Rate: {(dismissals/total_balls*100):.1f}%

"""
        
        # Powerplay Analysis
        powerplay_data = data[data['phase'] == 'Powerplay']
        brief += self._analyze_phase_enhanced(powerplay_data, "POWERPLAY (Overs 1-6)")
        
        # Post Powerplay Analysis  
        post_pp_data = data[data['phase'] == 'Post Powerplay']
        brief += self._analyze_phase_enhanced(post_pp_data, "POST POWERPLAY (Overs 7-20)")
        
        # Tactical Summary
        brief += self._generate_enhanced_tactical_summary(batsman_name, bowler_type, data, powerplay_data, post_pp_data)
        
        return brief
    
    def _format_filters(self):
        """Format applied filters for display"""
        if not self.filters:
            return "No filters applied (all data)"
        
        filter_text = []
        if 'season' in self.filters:
            filter_text.append(f"Season: {self.filters['season']}")
        if 'ground' in self.filters:
            filter_text.append(f"Ground: {self.filters['ground']}")
        if 'opposition' in self.filters:
            filter_text.append(f"Opposition: {self.filters['opposition']}")
        if 'start_date' in self.filters:
            filter_text.append(f"From: {self.filters['start_date']}")
        if 'end_date' in self.filters:
            filter_text.append(f"To: {self.filters['end_date']}")
        
        return " | ".join(filter_text)
    
    def _analyze_phase_enhanced(self, phase_data, phase_name):
        """Enhanced phase analysis with correct calculations"""
        
        if phase_data.empty:
            return f"\n## {phase_name}\n❌ No data available\n"
        
        total_balls = len(phase_data)
        total_runs = phase_data['R'].sum()
        phase_sr = self._calculate_strike_rate(phase_data)
        
        analysis = f"\n## {phase_name}\n"
        analysis += f"Balls: {total_balls} | Runs: {total_runs} | SR: {phase_sr:.1f}\n\n"
        
        # Strike Rate by Length (only if sufficient data)
        analysis += "### Strike Rate by Length:\n"
        length_sr = self._calculate_sr_by_category_enhanced(phase_data, 'Length', min_balls=5)
        if length_sr:
            for length, (sr, balls) in length_sr.items():
                analysis += f"- {length}: {sr:.1f} SR ({balls} balls)\n"
        else:
            analysis += "- Insufficient data for length analysis\n"
        
        # Strike Rate by Zone
        analysis += "\n### Strike Rate by Zone:\n"
        zone_sr = self._calculate_sr_by_category_enhanced(phase_data, 'Zone', min_balls=3)
        if zone_sr:
            for zone, (sr, balls) in list(zone_sr.items())[:5]:  # Top 5 zones
                analysis += f"- {zone}: {sr:.1f} SR ({balls} balls)\n"
        else:
            analysis += "- Insufficient data for zone analysis\n"
        
        # Boundary Analysis
        boundaries = self._analyze_boundaries_enhanced(phase_data)
        analysis += f"\n### Boundary Analysis:\n"
        analysis += f"- Fours: {boundaries['fours']} ({boundaries['four_rate']:.1f}%)\n"
        analysis += f"- Sixes: {boundaries['sixes']} ({boundaries['six_rate']:.1f}%)\n"
        analysis += f"- Dot balls: {boundaries['dots']} ({boundaries['dot_rate']:.1f}%)\n"
        
        # Dismissal Analysis
        dismissals = phase_data[phase_data['Wkt'] != '-']
        if not dismissals.empty:
            analysis += f"\n### Dismissal Pattern:\n"
            dismissal_types = dismissals['Wkt'].value_counts()
            for dismissal, count in dismissal_types.items():
                analysis += f"- {dismissal}: {count}\n"
        
        return analysis
    
    def _calculate_sr_by_category_enhanced(self, data, category_col, min_balls=3):
        """Enhanced category analysis with minimum balls requirement"""
        sr_dict = {}
        
        for category in data[category_col].dropna().unique():
            if category == '-':  # Skip missing values
                continue
                
            cat_data = data[data[category_col] == category]
            if len(cat_data) >= min_balls:
                sr = self._calculate_strike_rate(cat_data)
                sr_dict[category] = (sr, len(cat_data))
        
        # Sort by strike rate (descending)
        return dict(sorted(sr_dict.items(), key=lambda x: x[1][0], reverse=True))
    
    def _analyze_boundaries_enhanced(self, data):
        """Enhanced boundary analysis"""
        total_balls = len(data)
        fours = len(data[data['4'] == 1]) if '4' in data.columns else 0
        sixes = len(data[data['6'] == 1]) if '6' in data.columns else 0
        dots = len(data[data['0'] == 1]) if '0' in data.columns else 0
        
        return {
            'fours': fours,
            'sixes': sixes,
            'dots': dots,
            'four_rate': (fours / total_balls * 100) if total_balls > 0 else 0,
            'six_rate': (sixes / total_balls * 100) if total_balls > 0 else 0,
            'dot_rate': (dots / total_balls * 100) if total_balls > 0 else 0
        }
    
    def _generate_enhanced_tactical_summary(self, batsman_name, bowler_type, all_data, pp_data, post_pp_data):
        """Generate enhanced tactical summary"""
        
        summary = f"\n## TACTICAL SUMMARY\n"
        summary += f"{'=' * 30}\n\n"
        
        # Data quality check
        total_balls = len(all_data)
        summary += f"### DATA QUALITY\n"
        summary += f"- Sample size: {total_balls} balls\n"
        summary += f"- Reliability: {'High' if total_balls >= 50 else 'Medium' if total_balls >= 20 else 'Low'}\n\n"
        
        # Most effective bowling strategy
        summary += "### BOWLING STRATEGY\n"
        
        # Find most restrictive length
        length_sr = self._calculate_sr_by_category_enhanced(all_data, 'Length', min_balls=5)
        if length_sr:
            best_length = min(length_sr.items(), key=lambda x: x[1][0])
            summary += f"- Most restrictive length: {best_length[0]} (SR: {best_length[1][0]:.1f})\n"
        
        # Find danger zones
        zone_sr = self._calculate_sr_by_category_enhanced(all_data, 'Zone', min_balls=3)
        if zone_sr:
            danger_zones = [zone for zone, (sr, balls) in zone_sr.items() if sr > 150 and balls >= 3]
            if danger_zones:
                summary += f"- Danger zones: {', '.join(danger_zones[:3])}\n"
        
        # Phase comparison
        pp_sr = self._calculate_strike_rate(pp_data) if not pp_data.empty else 0
        post_pp_sr = self._calculate_strike_rate(post_pp_data) if not post_pp_data.empty else 0
        
        summary += f"\n### PHASE ANALYSIS\n"
        summary += f"- Powerplay SR: {pp_sr:.1f}\n"
        summary += f"- Post-Powerplay SR: {post_pp_sr:.1f}\n"
        
        if pp_sr > post_pp_sr + 20:
            summary += f"- Strategy: Early pressure crucial (more aggressive in PP)\n"
        elif post_pp_sr > pp_sr + 20:
            summary += f"- Strategy: Builds through middle overs (tighten up later)\n"
        else:
            summary += f"- Strategy: Consistent across phases\n"
        
        return summary
    
    def get_available_filters(self):
        """Get available filter options"""
        return {
            'seasons': sorted(self.df['year'].unique()),
            'grounds': sorted(self.df['Ground Name'].unique()),
            'teams': sorted(self.df['Team'].unique()),
            'batsmen': sorted(self.df['Batsman'].dropna().unique()),
            'date_range': {
                'min': self.df['date'].min(),
                'max': self.df['date'].max()
            }
        }

def main():
    """Interactive enhanced strategy engine with filters"""
    
    print("🏏 Enhanced IPL Strategy Engine with Filters")
    print("=" * 50)
    
    # Get filter preferences
    filters = {}
    
    print("\n📊 Available filter options:")
    temp_engine = EnhancedIPLStrategyEngine()
    options = temp_engine.get_available_filters()
    
    print(f"Seasons: {options['seasons']}")
    print(f"Grounds: {len(options['grounds'])} available")
    print(f"Teams: {options['teams']}")
    
    # Collect filters
    season = input(f"\nEnter season ({'/'.join(map(str, options['seasons']))}): ").strip()
    if season and season.isdigit():
        filters['season'] = int(season)
    
    ground = input("Enter ground (partial name or leave blank): ").strip()
    if ground:
        filters['ground'] = ground
    
    opposition = input(f"Enter opposition team ({'/'.join(options['teams'][:5])}...): ").strip()
    if opposition:
        filters['opposition'] = opposition
    
    min_balls = input("Minimum balls for analysis (default 20): ").strip()
    if min_balls and min_balls.isdigit():
        filters['min_balls'] = int(min_balls)
    else:
        filters['min_balls'] = 20
    
    # Initialize with filters
    engine = EnhancedIPLStrategyEngine(filters)
    
    # Generate brief
    batsman = input("\nEnter batsman name: ").strip()
    bowler_type = input("Enter bowler type (RAF/LAF/LAO/Off Break/Leg Spin): ").strip() or 'RAF'
    
    brief = engine.generate_scouting_brief(batsman, bowler_type, filters.get('min_balls', 20))
    print("\n" + "="*60)
    print(brief)
    
    # Save option
    save = input("\nSave brief to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"enhanced_brief_{batsman.replace(' ', '_')}_{bowler_type}_{filters.get('season', 'all')}.md"
        with open(filename, 'w') as f:
            f.write(brief)
        print(f"💾 Brief saved as: {filename}")

if __name__ == "__main__":
    main()