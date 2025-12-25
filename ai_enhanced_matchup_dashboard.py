"""
AI-Enhanced Matchup Dashboard
Interactive Streamlit dashboard with Gemini AI insights for cricket matchup analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from simple_matchup_stats import SimpleMatchupStats
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI-Powered Cricket Analytics",
    page_icon="🤖",
    layout="wide"
)

# Initialize stats calculator and AI backend (cached for performance)
@st.cache_resource
def load_stats_with_filters(filters=None):
    """Load and cache the statistics calculator with filters."""
    filter_dict = filters if filters else {}
    return SimpleMatchupStats('ipl_data.csv', filters=filter_dict)


@st.cache_resource
def get_filter_options():
    """Get available filter options from the data."""
    temp_stats = SimpleMatchupStats('ipl_data.csv')
    return temp_stats.get_available_filters()


@st.cache_resource
def load_ai_backend(_filters=None):
    """Load and cache the AI analytics backend with filter support."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    try:
        backend = EnhancedGeminiIPLAnalytics('ipl_data.csv', api_key=api_key)
        
        # Apply filters to the backend's dataframe if provided
        if _filters:
            if 'seasons' in _filters:
                backend.df['Year'] = pd.to_datetime(backend.df['Date⬆']).dt.year
                backend.df = backend.df[backend.df['Year'].isin(_filters['seasons'])]
            
            if 'grounds' in _filters:
                backend.df = backend.df[backend.df['Ground Name'].isin(_filters['grounds'])]
            
            if 'teams' in _filters:
                backend.df = backend.df[
                    (backend.df['Team'].isin(_filters['teams'])) | 
                    (backend.df['Team.1'].isin(_filters['teams']))
                ]
            
            if 'venue_type' in _filters:
                if _filters['venue_type'] == 'Homeground':
                    backend.df = backend.df[backend.df['H/A'] == 'H']
                elif _filters['venue_type'] == 'Away':
                    backend.df = backend.df[backend.df['H/A'] == 'A']
            
            if 'innings' in _filters:
                backend.df = backend.df[backend.df['I#'] == _filters['innings']]
            
            # Rebuild dataset context after filtering
            backend.dataset_context = backend._build_dataset_context()
        
        return backend
    except Exception as e:
        st.error(f"Failed to initialize AI: {str(e)}")
        return None


def get_performance_assessment(strike_rate, dot_percentage):
    """Assess batsman performance based on strike rate and dot percentage."""
    if strike_rate >= 150 and dot_percentage < 35:
        return "🔥 Dominant", "success"
    elif strike_rate >= 120 and dot_percentage < 40:
        return "✅ Solid", "success"
    elif strike_rate >= 100:
        return "⚠️ Cautious", "warning"
    else:
        return "❌ Struggles", "error"


def get_effectiveness_rating(economy, dot_percentage):
    """Rate bowler effectiveness."""
    if economy < 6.0 and dot_percentage > 40:
        return "🌟 Excellent", "success"
    elif economy < 7.5 and dot_percentage > 35:
        return "✅ Good", "success"
    elif economy < 9.0:
        return "⚠️ Average", "warning"
    else:
        return "❌ Expensive", "error"


def get_filter_context_string(filters):
    """Convert filter dictionary to readable context string."""
    if not filters:
        return "No filters applied (analyzing entire dataset)"
    
    context_parts = []
    if 'seasons' in filters:
        context_parts.append(f"Seasons: {', '.join(map(str, filters['seasons']))}")
    if 'grounds' in filters:
        context_parts.append(f"Grounds: {', '.join(filters['grounds'])}")
    if 'teams' in filters:
        context_parts.append(f"Teams: {', '.join(filters['teams'])}")
    if 'venue_type' in filters:
        context_parts.append(f"Venue: {filters['venue_type']}")
    if 'innings' in filters:
        context_parts.append(f"Innings: {filters['innings']}")
    
    return "ACTIVE FILTERS:\n" + "\n".join(context_parts)


def get_ai_insights(ai_backend, query, context_data=None, filters=None):
    """Get AI-powered insights for the matchup with filter awareness."""
    if ai_backend is None:
        return None
    
    try:
        # Build comprehensive query with context
        full_query = query
        
        # Add filter context
        if filters:
            filter_context = get_filter_context_string(filters)
            full_query = f"{query}\n\n{filter_context}"
        
        # Add regular context data
        if context_data:
            full_query = f"{full_query}\n\nContext Data:\n{context_data}"
        
        # Add instruction for filter-aware analysis
        if filters:
            full_query += "\n\nIMPORTANT: Analyze how the active filters affect performance. Provide insights specific to the filtered conditions (e.g., 'on this ground', 'in this season', 'at this venue type'). Compare performance under these specific conditions."
        
        result = ai_backend.smart_analyze(full_query)
        return result['gemini_response']
    except Exception as e:
        st.warning(f"AI analysis unavailable: {str(e)}")
        return None


def display_ai_insight_box(ai_backend, query, context_data=None, filters=None):
    """Display AI insights in an expandable section."""
    if ai_backend:
        with st.expander("🤖 AI-Powered Insights", expanded=False):
            with st.spinner("Generating AI insights..."):
                insights = get_ai_insights(ai_backend, query, context_data, filters)
                if insights:
                    st.markdown(insights)
                else:
                    st.info("AI insights not available for this analysis.")


def display_batsman_vs_bowling_type(stats, ai_backend, filters=None):
    """Display analysis for batsman vs bowling type with AI insights."""
    st.header("🏏 Batsman vs Bowling Type")
    st.markdown("Analyze how a batsman performs against different bowling styles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        batsmen = sorted(stats.df['Batsman'].unique())
        batsman = st.selectbox("Select Batsman", batsmen, key="bt_batsman")
    
    with col2:
        bowling_types = sorted(stats.df['Technique'].unique())
        bowling_types = [bt for bt in bowling_types if bt not in ['-', '']]
        bowling_type = st.selectbox("Select Bowling Type", bowling_types, key="bt_type")
    
    if st.button("Analyze", key="bt_analyze"):
        with st.spinner("Analyzing..."):
            result = stats.batsman_vs_bowling_type(batsman, bowling_type)
            
            if 'error' in result:
                st.error(result['error'])
            else:
                # Display metrics
                st.subheader(f"📊 {result['batsman']} vs {result['bowling_type']}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Balls Faced", result['balls'])
                    st.metric("Dismissals", result['dismissals'])
                
                with col2:
                    st.metric("Runs Scored", result['runs'])
                    st.metric("Average", result['average'])
                
                with col3:
                    st.metric("Strike Rate", f"{result['strike_rate']}")
                    st.metric("Boundaries", result['boundaries'])
                
                with col4:
                    st.metric("Dot Ball %", f"{result['dot_percentage']}%")
                    st.metric("Boundary %", f"{result['boundary_percentage']}%")
                
                # Performance assessment
                assessment, level = get_performance_assessment(result['strike_rate'], result['dot_percentage'])
                if level == "success":
                    st.success(f"Performance Assessment: {assessment}")
                elif level == "warning":
                    st.warning(f"Performance Assessment: {assessment}")
                else:
                    st.error(f"Performance Assessment: {assessment}")
                
                # AI Insights
                context = f"""
                Batsman: {result['batsman']}
                Bowling Type: {result['bowling_type']}
                Balls Faced: {result['balls']}
                Runs: {result['runs']}
                Strike Rate: {result['strike_rate']}
                Dismissals: {result['dismissals']}
                Dot %: {result['dot_percentage']}%
                Boundaries: {result['boundaries']}
                """
                
                display_ai_insight_box(
                    ai_backend,
                    f"Provide detailed strategic insights for {batsman} batting against {bowling_type} bowling. Analyze strengths, weaknesses, and tactical recommendations based on the statistics.",
                    context,
                    filters
                )
                
                # Visualization
                st.subheader("📈 Ball Distribution")
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Dot Balls', 'Singles/Doubles', 'Boundaries'],
                        y=[result['dots'], result['balls'] - result['dots'] - result['boundaries'], result['boundaries']],
                        marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1'],
                        text=[result['dots'], result['balls'] - result['dots'] - result['boundaries'], result['boundaries']],
                        textposition='auto',
                    )
                ])
                
                fig.update_layout(
                    title=f"Ball Type Distribution",
                    xaxis_title="Ball Type",
                    yaxis_title="Count",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)


def display_head_to_head(stats, ai_backend, filters=None):
    """Display head-to-head analysis between batsman and bowler with AI insights."""
    st.header("⚔️ Head-to-Head: Batsman vs Bowler")
    st.markdown("Analyze individual matchups between batsman and bowler")
    
    col1, col2 = st.columns(2)
    
    with col1:
        batsmen = sorted(stats.df['Batsman'].unique())
        batsman = st.selectbox("Select Batsman", batsmen, key="h2h_batsman")
    
    with col2:
        bowlers = sorted(stats.df['Player'].unique())
        bowler = st.selectbox("Select Bowler", bowlers, key="h2h_bowler")
    
    if st.button("Analyze", key="h2h_analyze"):
        with st.spinner("Analyzing..."):
            result = stats.batsman_vs_bowler(batsman, bowler)
            
            if 'error' in result:
                st.error(result['error'])
            else:
                # Dominance indicator
                st.subheader(f"🎯 {result['batsman']} vs {result['bowler']}")
                
                if 'Batsman' in result['dominance']:
                    st.success(f"**Dominance:** {result['dominance']} ✅")
                elif 'Bowler' in result['dominance']:
                    st.error(f"**Dominance:** {result['dominance']} 🎳")
                else:
                    st.info(f"**Dominance:** {result['dominance']} ⚖️")
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Balls Faced", result['balls'])
                
                with col2:
                    st.metric("Runs Scored", result['runs'])
                
                with col3:
                    st.metric("Strike Rate", f"{result['strike_rate']}")
                
                with col4:
                    st.metric("Dismissals", result['dismissals'])
                
                # Additional details
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Fours", result['fours'])
                
                with col2:
                    st.metric("Sixes", result['sixes'])
                
                with col3:
                    st.metric("Average", result['average'])
                
                # AI Insights for matchup
                context = f"""
                Batsman: {result['batsman']}
                Bowler: {result['bowler']}
                Balls: {result['balls']}
                Runs: {result['runs']}
                Strike Rate: {result['strike_rate']}
                Dismissals: {result['dismissals']}
                Dominance: {result['dominance']}
                Fours: {result['fours']}
                Sixes: {result['sixes']}
                """
                
                display_ai_insight_box(
                    ai_backend,
                    f"Analyze the head-to-head matchup between {batsman} and {bowler}. Who has the advantage and why? What are the key factors in this matchup? Provide strategic recommendations.",
                    context,
                    filters
                )


def display_bowler_vs_batting_hand(stats, ai_backend, filters=None):
    """Display bowler performance vs left/right-handed batsmen with AI insights."""
    st.header("🎳 Bowler vs Batting Hand")
    st.markdown("Analyze bowler performance against right and left-handed batsmen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bowlers = sorted(stats.df['Player'].unique())
        bowler = st.selectbox("Select Bowler", bowlers, key="bh_bowler")
    
    with col2:
        batting_hand = st.selectbox(
            "Select Batting Hand",
            ['R', 'L'],
            format_func=lambda x: 'Right-handed' if x == 'R' else 'Left-handed',
            key="bh_hand"
        )
    
    if st.button("Analyze", key="bh_analyze"):
        with st.spinner("Analyzing..."):
            result = stats.bowler_vs_batting_hand(bowler, batting_hand)
            
            if 'error' in result:
                st.error(result['error'])
            else:
                # Display metrics
                st.subheader(f"📊 {result['bowler']} vs {result['batting_hand']} Batsmen")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Balls Bowled", result['balls'])
                    st.metric("Wickets", result['wickets'])
                
                with col2:
                    st.metric("Runs Conceded", result['runs'])
                    st.metric("Economy Rate", f"{result['economy']}")
                
                with col3:
                    if result['wickets'] > 0:
                        st.metric("Bowling Average", result['average'])
                        st.metric("Bowling SR", result['bowling_strike_rate'])
                    else:
                        st.metric("Bowling Average", "N/A")
                        st.metric("Bowling SR", "N/A")
                
                with col4:
                    st.metric("Dot Balls", result['dots'])
                    st.metric("Dot %", f"{result['dot_percentage']}%")
                
                # Effectiveness rating
                assessment, level = get_effectiveness_rating(result['economy'], result['dot_percentage'])
                if level == "success":
                    st.success(f"Effectiveness Rating: {assessment}")
                elif level == "warning":
                    st.warning(f"Effectiveness Rating: {assessment}")
                else:
                    st.error(f"Effectiveness Rating: {assessment}")
                
                # AI Insights
                context = f"""
                Bowler: {result['bowler']}
                Batting Hand: {result['batting_hand']}
                Balls: {result['balls']}
                Runs: {result['runs']}
                Economy: {result['economy']}
                Wickets: {result['wickets']}
                Dot %: {result['dot_percentage']}%
                """
                
                hand_name = "right-handed" if batting_hand == 'R' else "left-handed"
                display_ai_insight_box(
                    ai_backend,
                    f"Analyze {bowler}'s effectiveness against {hand_name} batsmen. What makes them effective or ineffective? Provide tactical insights and recommendations.",
                    context,
                    filters
                )


def display_bowler_economy_by_phase(stats, ai_backend, filters=None):
    """Display bowler economy comparison across phases with AI insights."""
    st.header("⏱️ Bowler Economy by Phase")
    st.markdown("Compare bowler performance in powerplay vs post-powerplay")
    
    bowlers = sorted(stats.df['Player'].unique())
    bowler = st.selectbox("Select Bowler", bowlers, key="phase_bowler")
    
    if st.button("Analyze", key="phase_analyze"):
        with st.spinner("Analyzing..."):
            result = stats.bowler_economy_by_phase(bowler)
            
            if 'error' in result:
                st.error(result['error'])
            else:
                st.subheader(f"📊 {result['bowler']} - Phase Analysis")
                
                # Side-by-side comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🌅 Powerplay (Overs 1-6)")
                    pp = result['powerplay']
                    st.metric("Balls Bowled", pp['balls'])
                    st.metric("Runs Conceded", pp['runs'])
                    st.metric("Economy Rate", pp['economy'])
                    st.metric("Wickets", pp['wickets'])
                    st.metric("Dot %", f"{pp['dot_percentage']}%")
                
                with col2:
                    st.markdown("### 🌇 Post-Powerplay (Overs 7-20)")
                    post = result['post_powerplay']
                    st.metric("Balls Bowled", post['balls'])
                    st.metric("Runs Conceded", post['runs'])
                    st.metric("Economy Rate", post['economy'])
                    st.metric("Wickets", post['wickets'])
                    st.metric("Dot %", f"{post['dot_percentage']}%")
                
                # Analysis insight
                st.info(f"**Analysis:** {result['analysis']}")
                
                # AI Insights
                context = f"""
                Bowler: {result['bowler']}
                Powerplay: {pp['balls']} balls, {pp['runs']} runs, {pp['economy']} economy, {pp['wickets']} wickets
                Post-Powerplay: {post['balls']} balls, {post['runs']} runs, {post['economy']} economy, {post['wickets']} wickets
                Analysis: {result['analysis']}
                """
                
                display_ai_insight_box(
                    ai_backend,
                    f"Analyze {bowler}'s performance across different match phases. What are their strengths in each phase? When should they be used strategically?",
                    context,
                    filters
                )
                
                # Visualization
                if result['powerplay']['balls'] > 0 and result['post_powerplay']['balls'] > 0:
                    st.subheader("📈 Economy Rate Comparison")
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=['Powerplay', 'Post-Powerplay'],
                            y=[result['powerplay']['economy'], result['post_powerplay']['economy']],
                            marker_color=['#ff6b6b', '#4ecdc4'],
                            text=[result['powerplay']['economy'], result['post_powerplay']['economy']],
                            textposition='auto',
                        )
                    ])
                    
                    fig.update_layout(
                        title="Economy Rate by Phase",
                        xaxis_title="Phase",
                        yaxis_title="Economy Rate",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)


def display_team_matchup(stats, ai_backend, filters=None):
    """Display team vs team matchup analysis with AI insights."""
    st.header("🏆 Team Matchup")
    st.markdown("Analyze batting performance of teams against each other")
    
    teams = list(stats.team_name_map.keys())
    team_display = stats.team_name_map
    
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = st.selectbox(
            "Select Team 1",
            teams,
            format_func=lambda x: team_display.get(x, x),
            key="tm_team1"
        )
    
    with col2:
        team2 = st.selectbox(
            "Select Team 2",
            teams,
            format_func=lambda x: team_display.get(x, x),
            key="tm_team2"
        )
    
    if st.button("Analyze", key="tm_analyze"):
        if team1 == team2:
            st.error("Please select two different teams")
        else:
            with st.spinner("Analyzing..."):
                result = stats.team_matchup(team1, team2)
                
                # Display metrics
                st.subheader(f"⚔️ {result['team1_batting']['team']} vs {result['team2_batting']['team']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"### 🏏 {result['team1_batting']['team']}")
                    st.markdown(f"*Batting against {result['team1_batting']['opponent']}*")
                    t1 = result['team1_batting']
                    st.metric("Balls Faced", t1['balls'])
                    st.metric("Runs Scored", t1['runs'])
                    st.metric("Run Rate", t1['run_rate'])
                    st.metric("Boundaries", t1['boundaries'])
                
                with col2:
                    st.markdown(f"### 🏏 {result['team2_batting']['team']}")
                    st.markdown(f"*Batting against {result['team2_batting']['opponent']}*")
                    t2 = result['team2_batting']
                    st.metric("Balls Faced", t2['balls'])
                    st.metric("Runs Scored", t2['runs'])
                    st.metric("Run Rate", t2['run_rate'])
                    st.metric("Boundaries", t2['boundaries'])
                
                # Advantage indicator
                st.markdown("---")
                if "insufficient" in result['advantage'].lower():
                    st.warning(result['advantage'])
                else:
                    st.success(f"**{result['advantage']}**")
                
                # AI Insights
                context = f"""
                Team 1: {result['team1_batting']['team']}
                Team 1 Stats: {t1['balls']} balls, {t1['runs']} runs, {t1['run_rate']} run rate, {t1['boundaries']} boundaries
                Team 2: {result['team2_batting']['team']}
                Team 2 Stats: {t2['balls']} balls, {t2['runs']} runs, {t2['run_rate']} run rate, {t2['boundaries']} boundaries
                Advantage: {result['advantage']}
                """
                
                display_ai_insight_box(
                    ai_backend,
                    f"Analyze the matchup between {result['team1_batting']['team']} and {result['team2_batting']['team']}. What are the key strengths and weaknesses? Provide strategic predictions and recommendations.",
                    context,
                    filters
                )
                
                # Visualization
                if result['team1_batting']['balls'] > 0 and result['team2_batting']['balls'] > 0:
                    st.subheader("📈 Run Rate Comparison")
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=[result['team1_batting']['team'], result['team2_batting']['team']],
                            y=[result['team1_batting']['run_rate'], result['team2_batting']['run_rate']],
                            marker_color=['#ff6b6b', '#4ecdc4'],
                            text=[result['team1_batting']['run_rate'], result['team2_batting']['run_rate']],
                            textposition='auto',
                        )
                    ])
                    
                    fig.update_layout(
                        title="Run Rate Comparison",
                        xaxis_title="Team",
                        yaxis_title="Run Rate",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)


def display_ai_chat(ai_backend):
    """Display AI chat interface for custom queries."""
    st.header("💬 AI Cricket Assistant")
    st.markdown("Ask any cricket analytics question!")
    
    if ai_backend is None:
        st.warning("⚠️ AI features require GEMINI_API_KEY in your .env file")
        st.info("To enable AI features:\n1. Get an API key from Google AI Studio\n2. Add it to your .env file as GEMINI_API_KEY=your_key")
        return
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for i, (query, response) in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(f"**You:** {query}")
            st.markdown(f"**AI:** {response}")
            st.markdown("---")
    
    # Query input
    with st.form(key='ai_query_form'):
        query = st.text_area(
            "Ask a question:",
            placeholder="Example: Which bowlers are most effective in powerplay? Who are the best death overs batsmen?",
            height=100
        )
        submit = st.form_submit_button("Ask AI 🤖")
    
    if submit and query:
        with st.spinner("AI is analyzing..."):
            result = ai_backend.smart_analyze(query)
            response = result['gemini_response']
            
            # Add to history
            st.session_state.chat_history.append((query, response))
            
            # Display latest response
            st.markdown(f"**You:** {query}")
            st.markdown(f"**AI:** {response}")
            
            # Rerun to update chat history display
            st.rerun()


def main():
    """Main application."""
    st.title("🤖 AI-Powered Cricket Matchup Analytics")
    st.markdown("*Accurate statistics with intelligent AI insights powered by Google Gemini*")
    
    # Sidebar - Filters Section
    st.sidebar.title("🔍 Filters")
    st.sidebar.markdown("Filter data by season, ground, team, etc.")
    
    # Get available filter options
    filter_options = get_filter_options()
    
    # Initialize session state for filters
    if 'apply_filters' not in st.session_state:
        st.session_state.apply_filters = False
    
    # Season filter
    seasons = ['All'] + [str(s) for s in filter_options['seasons']]
    selected_seasons = st.sidebar.multiselect(
        "📅 Season(s)",
        seasons,
        default=['All'],
        help="Select one or more seasons"
    )
    
    # Ground filter
    grounds = ['All'] + filter_options['grounds']
    selected_grounds = st.sidebar.multiselect(
        "🏟️ Ground(s)",
        grounds,
        default=['All'],
        help="Select specific venues"
    )
    
    # Team filter
    teams = ['All'] + filter_options['teams']
    selected_teams = st.sidebar.multiselect(
        "🏏 Team(s)",
        teams,
        default=['All'],
        help="Filter by opposition team"
    )
    
    # Venue type filter
    venue_type = st.sidebar.selectbox(
        "🏠 Venue Type",
        filter_options['venue_types'],
        help="Home, Away, or Neutral venue"
    )
    
    # Innings filter
    innings = st.sidebar.selectbox(
        "🎯 Innings",
        filter_options['innings'],
        help="Filter by innings (1st or 2nd)"
    )
    
    # Build filter dictionary
    filters = {}
    
    if 'All' not in selected_seasons:
        filters['seasons'] = [int(s) for s in selected_seasons]
    
    if 'All' not in selected_grounds:
        filters['grounds'] = selected_grounds
    
    if 'All' not in selected_teams:
        filters['teams'] = selected_teams
    
    if venue_type != 'All':
        filters['venue_type'] = venue_type
    
    if innings != 'All':
        filters['innings'] = innings
    
    # Apply filters button
    if st.sidebar.button("🔄 Apply Filters", key="apply_filters_btn"):
        st.session_state.apply_filters = True
        st.cache_resource.clear()
    
    # Load statistics and AI backend
    with st.spinner("Loading data and AI models..."):
        if filters and st.session_state.apply_filters:
            stats = load_stats_with_filters(filters)
            ai_backend = load_ai_backend(filters)  # Load AI with filters
            # Show active filters
            st.sidebar.success(f"✅ Filters applied! {len(stats.df)} records")
        else:
            stats = load_stats_with_filters(None)
            ai_backend = load_ai_backend(None)  # Load AI without filters
            if filters:
                st.sidebar.info("Click 'Apply Filters' to activate")
    
    # Display AI status
    col1, col2 = st.columns([3, 1])
    with col1:
        if ai_backend:
            st.success("✅ AI Assistant Ready")
        else:
            st.warning("⚠️ AI features disabled (no API key found)")
    
    with col2:
        st.metric("📊 Records", f"{len(stats.df):,}")
    
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.markdown("---")
    st.sidebar.title("📊 Analysis Type")
    analysis_type = st.sidebar.radio(
        "Select Analysis:",
        [
            "Batsman vs Bowling Type",
            "Head-to-Head (Batsman vs Bowler)",
            "Bowler vs Batting Hand",
            "Bowler Economy by Phase",
            "Team Matchup",
            "AI Cricket Assistant"
        ]
    )
    
    # Display selected analysis
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 AI Features")
    st.sidebar.info(
        "AI-powered insights provide:\n"
        "• Strategic recommendations\n"
        "• Pattern recognition\n"
        "• Tactical analysis\n"
        "• Performance predictions\n"
        "• Custom queries"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 About")
    st.sidebar.info(
        "This dashboard combines accurate ball-by-ball "
        "statistics with AI-powered insights from Google Gemini "
        "to provide comprehensive cricket analytics."
    )
    
    # Main content area
    # Determine active filters for AI context
    active_filters = filters if (filters and st.session_state.apply_filters) else None
    
    if analysis_type == "Batsman vs Bowling Type":
        display_batsman_vs_bowling_type(stats, ai_backend, active_filters)
    elif analysis_type == "Head-to-Head (Batsman vs Bowler)":
        display_head_to_head(stats, ai_backend, active_filters)
    elif analysis_type == "Bowler vs Batting Hand":
        display_bowler_vs_batting_hand(stats, ai_backend, active_filters)
    elif analysis_type == "Bowler Economy by Phase":
        display_bowler_economy_by_phase(stats, ai_backend, active_filters)
    elif analysis_type == "Team Matchup":
        display_team_matchup(stats, ai_backend, active_filters)
    elif analysis_type == "AI Cricket Assistant":
        display_ai_chat(ai_backend)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Data Source:** IPL Ball-by-Ball Data | "
        "**AI Model:** Google Gemini 2.5 Flash | "
        "**Calculations:** Per-ball runs from cumulative data (R.1 column) | "
        "**Cricket Stats:** Strike Rate = (Runs/Balls) × 100, "
        "Economy = Runs/(Balls/6)"
    )


if __name__ == "__main__":
    main()
