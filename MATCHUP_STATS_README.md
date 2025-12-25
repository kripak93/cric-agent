# Cricket Matchup Statistics

Accurate cricket statistics calculator and interactive dashboard for IPL ball-by-ball data analysis.

## Files

### `simple_matchup_stats.py`
Core statistics module that calculates accurate cricket metrics from ball-by-ball data.

**Features:**
- Calculates per-ball runs from cumulative R.1 column
- Accurate Strike Rate, Economy Rate, and other cricket metrics
- 5 analysis methods for different matchup scenarios
- Handles team name mapping (abbreviated ↔ full names)

**Usage:**
```python
from simple_matchup_stats import SimpleMatchupStats

# Initialize
stats = SimpleMatchupStats('ipl_data.csv')

# Batsman vs bowling type
result = stats.batsman_vs_bowling_type('V Kohli', 'right pace')
print(f"Strike Rate: {result['strike_rate']}")

# Head-to-head
result = stats.batsman_vs_bowler('V Kohli', 'DL Chahar')
print(f"Dominance: {result['dominance']}")

# Bowler vs batting hand
result = stats.bowler_vs_batting_hand('DL Chahar', 'R')
print(f"Economy: {result['economy']}")

# Bowler economy by phase
result = stats.bowler_economy_by_phase('DL Chahar')
print(f"Powerplay: {result['powerplay']['economy']}")
print(f"Post-Powerplay: {result['post_powerplay']['economy']}")

# Team matchup
result = stats.team_matchup('CSK', 'RCB')
print(f"Advantage: {result['advantage']}")
```

### `accurate_matchup_dashboard.py`
Interactive Streamlit dashboard for exploring cricket matchup statistics.

**Features:**
- 5 analysis types with sidebar navigation
- Interactive player/team selection
- Plotly visualizations
- Performance ratings and assessments
- Color-coded metrics

**Run:**
```bash
streamlit run accurate_matchup_dashboard.py
```

## Analysis Types

### 1. Batsman vs Bowling Type
Analyze how a batsman performs against different bowling styles (right pace, off break, leg break, etc.).

**Metrics:** Balls, Runs, Strike Rate, Dismissals, Boundaries, Dot %, Boundary %

**Assessment:** Dominant (SR≥150, Dot%<35), Solid (SR≥120, Dot%<40), Cautious (SR≥100), Struggles (SR<100)

### 2. Head-to-Head (Batsman vs Bowler)
Individual matchup statistics between a batsman and bowler.

**Metrics:** Balls, Runs, Strike Rate, Dismissals, Fours, Sixes

**Dominance Indicator:** Batsman/Bowler/Neutral based on SR and dismissals

### 3. Bowler vs Batting Hand
Bowler performance against right-handed and left-handed batsmen.

**Metrics:** Balls, Runs, Economy, Wickets, Average, Bowling SR, Dot %

**Effectiveness:** Excellent (Econ<6, Dot%>40), Good (Econ<7.5, Dot%>35), Average (Econ<9), Expensive (Econ≥9)

### 4. Bowler Economy by Phase
Compare bowler economy in powerplay (overs 1-6) vs post-powerplay (overs 7-20).

**Metrics:** Balls, Runs, Economy, Wickets, Dots for each phase

**Visualization:** Side-by-side comparison with bar chart

### 5. Team Matchup
Team vs team batting statistics.

**Metrics:** Balls, Runs, Run Rate, Boundaries for each team

**Visualization:** Run rate comparison chart

## Cricket Statistics Formulas

All calculations use standard cricket formulas:

- **Strike Rate (Batting):** (Total Runs / Total Balls) × 100
- **Economy Rate (Bowling):** Total Runs / (Total Balls / 6)
- **Bowling Average:** Runs Conceded / Wickets
- **Bowling Strike Rate:** Balls Bowled / Wickets
- **Run Rate:** (Total Runs / Total Balls) × 6
- **Dot Ball %:** (Dot Balls / Total Balls) × 100
- **Boundary %:** (Boundaries / Total Balls) × 100

## Data Format

The module expects IPL ball-by-ball data in CSV format with these key columns:

- `Match⬆` - Match identifier
- `I#` - Innings number
- `Batsman` - Batsman name
- `Player` - Bowler name
- `Team` - Bowling team (abbreviated: CSK, RCB, etc.)
- `Opposition` - Batting team (full name)
- `Technique` - Bowling type (right pace, off break, etc.)
- `RL` - Batting hand (R/L)
- `R.1` - Cumulative runs for batsman
- `Overs` - Over number (e.g., 5.3)
- `Wkt` - Dismissal indicator

## Team Names

The module handles both abbreviated and full team names:

| Abbreviation | Full Name |
|--------------|-----------|
| CSK | Chennai Super Kings |
| RCB | Royal Chal Bengaluru |
| PBKS | Punjab Kings |
| DC | Delhi Capitals |
| SRH | Sunrisers Hyderabad |
| KKR | Kolkata Knight Riders |
| LSG | Lucknow Super Giants |
| RR | Rajasthan Royals |
| MI | Mumbai Indians |
| GT | Gujarat Titans |

## Requirements

```
streamlit==1.31.0
pandas==2.0.3
numpy==1.24.3
plotly==5.18.0
```

Install with:
```bash
pip install -r requirements.txt
```

## Testing

Run the example usage:
```bash
python simple_matchup_stats.py
```

Expected output includes statistics for:
- V Kohli vs right pace
- V Kohli vs DL Chahar
- DL Chahar vs R-handed batsmen
- DL Chahar economy by phase
- CSK vs RCB team matchup
