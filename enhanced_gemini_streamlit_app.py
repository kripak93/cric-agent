"""
Enhanced Streamlit Frontend for Gemini IPL Analytics
Integrates with enhanced_gemini_ipl_backend.py
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics

# Force load environment variables
load_dotenv(override=True)

# Debug: Check if .env file exists and is readable
if os.path.exists('.env'):
    st.sidebar.success("✅ .env file found")
    with open('.env', 'r') as f:
        env_content = f.read()
        if 'GEMINI_API_KEY=' in env_content and 'AIzaSy' in env_content:
            st.sidebar.success("✅ API key detected in .env")
        else:
            st.sidebar.error("❌ API key not found in .env")
else:
    st.sidebar.error("❌ .env file not found")

st.set_page_config(
    page_title="Gemini IPL Analytics",
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 Gemini IPL Analytics")
st.markdown("*AI-Powered Men's IPL Intelligence with Schema-Aware Analysis*")

# Season selection
st.sidebar.header("📅 Season Selection")
season_options = {
    "All Seasons": None,
    "2024 Season": 2024,
    "2025 Season": 2025
}
selected_season_name = st.sidebar.selectbox(
    "Choose IPL Season:",
    options=list(season_options.keys()),
    index=0
)
selected_season = season_options[selected_season_name]

@st.cache_resource
def load_analytics(season_filter=None):
    """Load analytics engine"""
    # Force reload environment variables
    load_dotenv(override=True)
    
    # Try multiple ways to get the API key
    api_key = None
    
    # Method 1: Direct from environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Method 2: Read directly from .env file
    if not api_key and os.path.exists('.env'):
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except Exception as e:
            st.error(f"Error reading .env file: {e}")
    
    # Method 3: Streamlit secrets (for cloud deployment)
    if not api_key and hasattr(st, 'secrets'):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass
    
    # Debug information
    st.sidebar.write(f"🔍 Debug: API key found = {'Yes' if api_key else 'No'}")
    if api_key:
        st.sidebar.write(f"🔍 Key starts with: {api_key[:10]}...")
    
    if not api_key or api_key == 'your_gemini_api_key_here' or api_key == 'your_actual_api_key_here':
        st.error("GEMINI_API_KEY not found")
        st.info("Please add your Gemini API key in .env file")
        st.code("GEMINI_API_KEY=your_actual_api_key_here")
        
        # Show current .env content for debugging
        if os.path.exists('.env'):
            st.write("Current .env file content:")
            with open('.env', 'r') as f:
                st.code(f.read())
        
        st.stop()
    
    try:
        analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv', api_key=api_key, season_filter=season_filter)
        st.success(f"✅ Connected using model: {analytics.model_name}")
        st.info(f"📅 Analyzing: {analytics.season}")
        return analytics
    except Exception as e:
        st.error(f"Failed to initialize analytics: {str(e)}")
        st.info("Try running 'python test_api.py' to check your API setup")
        st.stop()

try:
    analytics = load_analytics(selected_season)
except Exception as e:
    st.error(f"Error loading analytics: {str(e)}")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Smart Query",
    "👤 Player Analysis", 
    "🏟️ Team Analysis",
    "🎯 Game Prep",
    "🔍 Data Explorer"
])

df = pd.read_csv('ipl_data.csv')

# TAB 1: SMART QUERY
with tab1:
    st.header("💬 Smart Query")
    st.markdown("Ask any natural language question about the IPL data")

    st.markdown("#### Example Questions:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Who has the best economy rate?"):
            st.session_state.query = "Who has the best economy rate?"
        if st.button("Top 5 wicket-takers?"):
            st.session_state.query = "Top 5 wicket-takers?"
        if st.button("Best batting strike rate?"):
            st.session_state.query = "Best batting strike rate?"
    with col2:
        if st.button("Compare CSK vs MI"):
            st.session_state.query = "Compare CSK vs MI"
        if st.button("Team strengths analysis"):
            st.session_state.query = "Team strengths analysis"
        if st.button("Bumrah analysis"):
            st.session_state.query = "Bumrah analysis"

    st.markdown("---")

    query = st.text_input(
        "Ask a cricket question:",
        value=st.session_state.get('query', ''),
        placeholder="E.g., Who is the best bowler?"
    )

    if st.button("🔍 Analyze", type="primary"):
        if query:
            with st.spinner("Analyzing with Gemini..."):
                result = analytics.smart_analyze(query)

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("### Analysis Result")
                with col2:
                    st.markdown(f"**Intent:** {', '.join(result['intent'])}")

                st.markdown("---")
                st.markdown(result['gemini_response'])
        else:
            st.warning("Please enter a question")

# TAB 2: PLAYER ANALYSIS
with tab2:
    st.header("👤 Player Analysis")

    all_players = sorted(set(
        list(df['Player'].dropna().unique()) + 
        list(df['Batsman'].dropna().unique())
    ))

    selected_player = st.selectbox("Select player:", all_players)

    if st.button("📊 Get Insights", type="primary"):
        with st.spinner(f"Analyzing {selected_player}..."):
            insights = analytics.get_player_insights(selected_player)

            if 'error' not in insights:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {selected_player}")
                    st.metric("Bowling Matches", insights['bowling_matches'])
                with col2:
                    st.markdown("###")
                    st.metric("Batting Matches", insights['batting_matches'])

                st.markdown("---")
                st.markdown(insights['gemini_insights'])
            else:
                st.error(insights['error'])

# TAB 3: TEAM ANALYSIS
with tab3:
    st.header("🏟️ Team Analysis")

    teams = sorted(df['Team'].unique())
    selected_team = st.selectbox("Select team:", teams)

    if st.button("⚡ Analyze Team", type="primary"):
        with st.spinner(f"Analyzing {selected_team}..."):
            analysis = analytics.analyze_team(selected_team)

            stats = analysis['stats']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Bowlers", stats['bowlers'])
            with col2:
                st.metric("Batsmen", stats['batsmen'])
            with col3:
                st.metric("Wickets", int(stats['total_wickets']))
            with col4:
                st.metric("Avg Economy", f"{stats['avg_economy']:.2f}")

            st.markdown("---")
            st.markdown(analysis['gemini_analysis'])

# TAB 4: GAME PREP
with tab4:
    st.header("🎯 Game Prep & Scouting")
    st.markdown("Generate tactical briefs and scouting reports")
    
    prep_type = st.radio("Analysis Type:", ["Batsman Scouting", "Team Brief"])
    
    if prep_type == "Batsman Scouting":
        col1, col2 = st.columns(2)
        
        with col1:
            # Get available batsmen
            available_batsmen = sorted(df['Batsman'].dropna().unique())
            selected_batsman = st.selectbox("Select Batsman:", available_batsmen)
        
        with col2:
            bowler_types = ["RAF", "LAF", "Off Break", "Leg Spin", "LAO"]
            selected_bowler_type = st.selectbox("Bowler Type:", bowler_types)
        
        if st.button("🎯 Generate Scouting Brief", type="primary"):
            with st.spinner(f"Analyzing {selected_batsman} vs {selected_bowler_type}..."):
                try:
                    from corrected_strategy_engine import CorrectedIPLStrategyEngine
                    
                    # Collect filters
                    filters = {}
                    if selected_season != "All Seasons":
                        filters['season'] = selected_season
                    
                    # Add ground filter option
                    ground_filter = st.text_input("Ground filter (optional):", placeholder="e.g., Mumbai, Chennai")
                    if ground_filter:
                        filters['ground'] = ground_filter
                    
                    # Add minimum balls filter
                    min_balls = st.slider("Minimum balls for analysis:", 10, 100, 30)
                    filters['min_balls'] = min_balls
                    
                    engine = CorrectedIPLStrategyEngine(filters)
                    brief = engine.generate_scouting_brief(selected_batsman, selected_bowler_type, min_balls)
                    
                    st.markdown("### Scouting Brief")
                    st.markdown(brief)
                    
                    # Download button
                    st.download_button(
                        "📥 Download Brief",
                        brief,
                        f"scouting_{selected_batsman}_{selected_bowler_type}_{filters.get('season', 'all')}.md",
                        "text/markdown"
                    )
                except Exception as e:
                    st.error(f"Error generating brief: {e}")
                    st.info("Make sure you have sufficient data for the selected filters")
    
    else:  # Team Brief
        teams = sorted(df['Team'].unique())
        selected_team = st.selectbox("Opposition Team:", teams)
        
        if st.button("🏟️ Generate Team Brief", type="primary"):
            with st.spinner(f"Analyzing vs {selected_team}..."):
                try:
                    from ipl_strategy_engine import IPLStrategyEngine
                    engine = IPLStrategyEngine()
                    brief = engine.generate_team_brief(selected_team, ["RAF", "LAF", "Off Break"])
                    
                    st.markdown("### Team Brief")
                    st.markdown(brief)
                    
                    st.download_button(
                        "📥 Download Brief",
                        brief,
                        f"team_brief_vs_{selected_team}.md",
                        "text/markdown"
                    )
                except Exception as e:
                    st.error(f"Error generating brief: {e}")

# TAB 5: DATA EXPLORER
with tab5:
    st.header("🔍 Data Explorer")

    col1, col2 = st.columns(2)
    with col1:
        view_type = st.radio("View:", ["Top Bowlers", "Top Batsmen", "Team Stats", "Raw Data"])
    with col2:
        limit = st.slider("Records:", 5, 50, 10)

    st.markdown("---")

    if view_type == "Top Bowlers":
        df_copy = df.copy()
        df_copy['Econ_num'] = pd.to_numeric(df_copy['Econ'], errors='coerce')
        df_bowl = df_copy[df_copy['Econ_num'].notna()].nsmallest(limit, 'Econ_num')
        cols = ['Player', 'Team', 'O', 'M', 'R', 'W', 'Econ']
        st.dataframe(df_bowl[cols], use_container_width=True)
        st.download_button("📥 Download CSV", df_bowl[cols].to_csv(index=False), "bowlers.csv")

    elif view_type == "Top Batsmen":
        df_bats = df.nlargest(limit, 'R.1')
        cols = ['Batsman', 'Team.1', 'R.1', 'B', 'RR', '4', '6']
        st.dataframe(df_bats[cols], use_container_width=True)
        st.download_button("📥 Download CSV", df_bats[cols].to_csv(index=False), "batsmen.csv")

    elif view_type == "Team Stats":
        team_stats = df.groupby('Team').agg({
            'W': 'sum',
            'R': 'sum',
            'R.1': 'sum',
            'Player': 'nunique'
        }).round(2)
        team_stats.columns = ['Wickets', 'Runs Conceded', 'Runs Scored', 'Unique Players']
        st.dataframe(team_stats, use_container_width=True)
        st.download_button("📥 Download CSV", team_stats.to_csv(), "teams.csv")

    else:
        filter_type = st.radio("Filter:", ["All Data", "By Team", "By Player"])

        if filter_type == "By Team":
            team = st.selectbox("Team:", sorted(df['Team'].unique()), key="data_team")
            display_df = df[df['Team'] == team].head(limit)
        elif filter_type == "By Player":
            player = st.selectbox("Player:", sorted(df['Player'].unique()), key="data_player")
            display_df = df[df['Player'] == player].head(limit)
        else:
            display_df = df.head(limit)

        st.dataframe(display_df, use_container_width=True)
        st.download_button("📥 Download CSV", display_df.to_csv(index=False), "data.csv")

st.markdown("---")
st.markdown("🏏 Gemini IPL Analytics v2.0 | Schema-Aware AI Cricket Analytics")
