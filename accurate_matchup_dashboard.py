"""
Accurate Matchup Dashboard
Interactive Streamlit dashboard for cricket matchup analysis
"""

import streamlit as st
import plotly.graph_objects as go
from simple_matchup_stats import SimpleMatchupStats


# Page configuration
st.set_page_config(
    page_title="Cricket Matchup Analytics",
    page_icon="🏏",
    layout="wide"
)

# Initialize stats calculator (cached for performance)
@st.cache_resource
def load_stats():
    """Load and cache the statistics calculator."""
    return SimpleMatchupStats('ipl_data.csv')


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


def display_batsman_vs_bowling_type(stats):
    """Display analysis for batsman vs bowling type."""
    st.header("🏏 Batsman vs Bowling Type")
    st.markdown("Analyze how a batsman performs against different bowling styles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get unique batsmen
        batsmen = sorted(stats.df['Batsman'].unique())
        batsman = st.selectbox("Select Batsman", batsmen, key="bt_batsman")
    
    with col2:
        # Get unique bowling types
        bowling_types = sorted(stats.df['Technique'].unique())
        # Remove invalid entries
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
                
                # Visualization - Ball type distribution
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


def display_head_to_head(stats):
    """Display head-to-head analysis between batsman and bowler."""
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


def display_bowler_vs_batting_hand(stats):
    """Display bowler performance vs left/right-handed batsmen."""
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


def display_bowler_economy_by_phase(stats):
    """Display bowler economy comparison across phases."""
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
                
                # Visualization - Economy comparison
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


def display_team_matchup(stats):
    """Display team vs team matchup analysis."""
    st.header("🏆 Team Matchup")
    st.markdown("Analyze batting performance of teams against each other")
    
    # Get unique teams (both abbreviated and full names are supported)
    teams = ['CSK', 'RCB', 'PBKS', 'DC', 'SRH', 'KKR', 'LSG', 'RR', 'MI', 'GT']
    team_display = {
        'CSK': 'Chennai Super Kings',
        'RCB': 'Royal Challengers Bengaluru',
        'PBKS': 'Punjab Kings',
        'DC': 'Delhi Capitals',
        'SRH': 'Sunrisers Hyderabad',
        'KKR': 'Kolkata Knight Riders',
        'LSG': 'Lucknow Super Giants',
        'RR': 'Rajasthan Royals',
        'MI': 'Mumbai Indians',
        'GT': 'Gujarat Titans'
    }
    
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
                
                # Visualization - Run rate comparison
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


def main():
    """Main application."""
    st.title("🏏 Cricket Matchup Analytics")
    st.markdown("*Accurate cricket statistics from ball-by-ball data*")
    
    # Load statistics
    with st.spinner("Loading data..."):
        stats = load_stats()
    
    # Sidebar for navigation
    st.sidebar.title("📊 Analysis Type")
    analysis_type = st.sidebar.radio(
        "Select Analysis:",
        [
            "Batsman vs Bowling Type",
            "Head-to-Head (Batsman vs Bowler)",
            "Bowler vs Batting Hand",
            "Bowler Economy by Phase",
            "Team Matchup"
        ]
    )
    
    # Display selected analysis
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 About")
    st.sidebar.info(
        "This dashboard provides accurate cricket statistics "
        "calculated from ball-by-ball data. All calculations "
        "use proper cricket formulas for strike rate, economy, "
        "and other metrics."
    )
    
    # Main content area
    if analysis_type == "Batsman vs Bowling Type":
        display_batsman_vs_bowling_type(stats)
    elif analysis_type == "Head-to-Head (Batsman vs Bowler)":
        display_head_to_head(stats)
    elif analysis_type == "Bowler vs Batting Hand":
        display_bowler_vs_batting_hand(stats)
    elif analysis_type == "Bowler Economy by Phase":
        display_bowler_economy_by_phase(stats)
    elif analysis_type == "Team Matchup":
        display_team_matchup(stats)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Data Source:** IPL Ball-by-Ball Data | "
        "**Calculations:** Per-ball runs from cumulative data (R.1 column) | "
        "**Cricket Stats:** Strike Rate = (Runs/Balls) × 100, "
        "Economy = Runs/(Balls/6)"
    )


if __name__ == "__main__":
    main()
