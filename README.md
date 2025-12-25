# 🏏 Gemini IPL Analytics

AI-powered cricket analytics using Google's Gemini API for intelligent IPL data analysis.

## Features

### 🤖 AI-Enhanced Matchup Dashboard (NEW!)
- **Accurate Matchup Statistics**: Ball-by-ball analysis with proper cricket formulas
- **AI-Powered Insights**: Get intelligent strategic recommendations for every matchup
- **Advanced Filters**: Season, ground, team, venue type, innings filtering
- **Batsman vs Bowling Type**: Analyze performance against specific bowling styles with AI insights
- **Head-to-Head Analysis**: Detailed batsman vs bowler matchups with tactical suggestions
- **Bowler Effectiveness**: Performance analysis against left/right-handed batsmen
- **Phase Analysis**: Powerplay vs post-powerplay effectiveness with AI recommendations
- **Team Matchups**: Head-to-head team comparisons with predictive insights
- **AI Chat Assistant**: Ask any cricket question and get data-backed answers

### 📊 Classic Analytics Features
- **Smart Query**: Ask natural language questions about IPL data
- **Player Analysis**: Deep insights into individual player performance
- **Team Analysis**: Comprehensive team statistics and comparisons
- **Data Explorer**: Interactive data browsing and filtering

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 3. Configure Environment
```bash
# Copy the template
copy .env.template .env

# Edit .env and add your API key:
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Add Your Data
Place your IPL dataset as `ipl_data.csv` in the project root.

Expected columns (based on schema):
- Player, Team, O, M, R, W, Econ (bowling stats)
- Batsman, Team.1, R.1, B, RR (batting stats)
- Date↑, Ground Name, Match↑ (match info)

### 5. Run the App
```bash
streamlit run enhanced_gemini_streamlit_app.py
```

## Usage Options

### 🤖 AI-Enhanced Matchup Dashboard (NEW!)
```bash
streamlit run ai_enhanced_matchup_dashboard.py
```
- Complete matchup analysis with AI insights
- **Powerful filters**: Season, ground, team, venue type, innings
- Strategic recommendations for every scenario
- Interactive AI chat assistant
- All classic matchup features PLUS intelligent analysis

### 🌐 Classic Streamlit Interface
```bash
streamlit run enhanced_gemini_streamlit_app.py
```
- Interactive Streamlit app
- Season selection (2024/2025/All)
- Smart queries, player analysis, team reports

### 📊 Accurate Matchup Dashboard (No AI)
```bash
streamlit run accurate_matchup_dashboard.py
```
- Pure statistical analysis with filters
- Accurate cricket calculations
- No AI features (faster, no API key needed)
- Filter by season, ground, team, venue, innings

### 🛠️ Command Line Toolkit
```bash
python ipl_analytics_toolkit.py
```
- Menu-driven analysis
- Quick stats and validation
- Ball position analysis
- Season comparisons

### 💬 Smart Queries Examples
- "Who has the best economy rate in 2025?"
- "Compare Bumrah vs Starc bowling performance"
- "Which team has the strongest bowling attack?"
- "Analyze ball position performance for any player"
- "What are Virat Kohli's weaknesses against spin?"
- "Which bowlers are most effective in the death overs?"
- "Predict the outcome of CSK vs MI based on current form"

## File Structure
```
├── 🏏 MAIN FILES
│   ├── ai_enhanced_matchup_dashboard.py   # 🤖 NEW! AI-powered matchup with filters
│   ├── accurate_matchup_dashboard.py      # 📊 Statistical matchup with filters
│   ├── simple_matchup_stats.py            # Core matchup calculations + filters
│   ├── enhanced_gemini_ipl_backend.py     # Core analytics engine with AI
│   ├── enhanced_gemini_streamlit_app.py   # Classic web interface  
│   ├── ipl_analytics_toolkit.py           # Consolidated analysis toolkit
│   ├── run_app.py                         # Easy launcher
│   ├── setup.py                           # Setup script
│   ├── ipl_data.csv                       # Your IPL dataset
│   ├── .env                               # API key configuration
│   └── requirements.txt                   # Dependencies
├── 📖 DOCUMENTATION
│   ├── AI_FEATURES_GUIDE.md               # Guide to AI features
│   ├── FILTERS_GUIDE.md                   # Comprehensive filters documentation
│   ├── DASHBOARD_COMPARISON.md            # Compare dashboards
│   └── MATCHUP_STATS_README.md            # Matchup statistics details
├── 📁 scripts/                            # Individual analysis scripts (archived)
├── 📁 data/                               # Backup and seasonal data files
└── 📁 docs/                               # Documentation and schemas
```

## Troubleshooting

### API Key Issues
- Ensure your API key is valid and active
- Check the .env file format (no quotes around the key)
- Verify you have Gemini API access

### Data Issues
- Ensure your CSV has the expected column names
- Check for proper encoding (UTF-8 recommended)
- Verify data completeness

### Dependencies
Run the setup script to check everything:
```bash
python setup.py
```

## Support

For issues or questions, check:
1. Your API key is correctly set
2. Data file exists and has proper format
3. All dependencies are installed
4. Python 3.8+ is being used