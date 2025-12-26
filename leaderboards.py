"""
Cricket Leaderboards
Functions to generate various cricket leaderboards from ball-by-ball data
"""

import pandas as pd
import streamlit as st


def get_best_vs_pace(stats, min_balls=50):
    """Get best batsmen overall (bowling type not available in data)."""
    
    batsman_stats = stats.df.groupby('Batsman').agg({
        'runs_this_ball': 'sum',
        'Batsman': 'count',
        '4': 'sum',
        '6': 'sum',
        'W': 'max',
        'Team.1': 'first'
    }).rename(columns={'Batsman': 'balls', 'runs_this_ball': 'runs', 'Team.1': 'Team'})
    
    batsman_stats = batsman_stats[batsman_stats['balls'] >= min_balls]
    batsman_stats['avg'] = (batsman_stats['runs'] / batsman_stats['W'].replace(0, 1)).round(2)
    batsman_stats['sr'] = ((batsman_stats['runs'] / batsman_stats['balls']) * 100).round(2)
    batsman_stats['boundary%'] = (((batsman_stats['4'] + batsman_stats['6']) / batsman_stats['balls']) * 100).round(1)
    
    return batsman_stats.sort_values('runs', ascending=False)[['Team', 'runs', 'balls', 'avg', 'sr', '4', '6', 'boundary%']]


def get_best_vs_spin(stats, min_balls=50):
    """Get best batsmen by strike rate (bowling type not available in data)."""
    
    batsman_stats = stats.df.groupby('Batsman').agg({
        'runs_this_ball': 'sum',
        'Batsman': 'count',
        '4': 'sum',
        '6': 'sum',
        'W': 'max',
        'Team.1': 'first'
    }).rename(columns={'Batsman': 'balls', 'runs_this_ball': 'runs', 'Team.1': 'Team'})
    
    batsman_stats = batsman_stats[batsman_stats['balls'] >= min_balls]
    batsman_stats['avg'] = (batsman_stats['runs'] / batsman_stats['W'].replace(0, 1)).round(2)
    batsman_stats['sr'] = ((batsman_stats['runs'] / batsman_stats['balls']) * 100).round(2)
    batsman_stats['boundary%'] = (((batsman_stats['4'] + batsman_stats['6']) / batsman_stats['balls']) * 100).round(1)
    
    return batsman_stats.sort_values('sr', ascending=False)[['Team', 'runs', 'balls', 'avg', 'sr', '4', '6', 'boundary%']]


def get_best_bowlers_vs_rh(stats, min_overs=5):
    """Get best bowlers against right-handed batsmen."""
    rh_data = stats.df[stats.df['B/H'] == 'Right'].copy()
    
    # Create match-player ID to avoid cumulative wicket counting
    rh_data['Match_Player'] = rh_data['Match⬆'] + '_' + rh_data['Player']
    
    # Get max wickets per match (cumulative), then sum across matches
    match_stats = rh_data.groupby('Match_Player').agg({
        'Player': 'first',
        'Team': 'first',
        'runs_this_ball': 'sum',
        'Match⬆': 'count',  # Count balls
        'W': 'max',  # Max wickets in this match
        '0': 'sum'
    }).rename(columns={'Match⬆': 'balls'})
    
    # Now aggregate by player
    bowler_stats = match_stats.groupby('Player').agg({
        'Team': 'first',
        'runs_this_ball': 'sum',
        'balls': 'sum',
        'W': 'sum',  # Sum of max wickets across matches
        '0': 'sum'
    }).rename(columns={'runs_this_ball': 'runs'})
    
    bowler_stats['overs'] = (bowler_stats['balls'] / 6).round(1)
    bowler_stats = bowler_stats[bowler_stats['overs'] >= min_overs]
    bowler_stats['econ'] = ((bowler_stats['runs'] / bowler_stats['overs'])).round(2)
    bowler_stats['sr'] = (bowler_stats['balls'] / bowler_stats['W'].replace(0, 1)).round(1)
    bowler_stats['dot%'] = ((bowler_stats['0'] / bowler_stats['balls']) * 100).round(1)
    
    return bowler_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'sr', 'dot%']]


def get_best_bowlers_vs_lh(stats, min_overs=5):
    """Get best bowlers against left-handed batsmen."""
    lh_data = stats.df[stats.df['B/H'] == 'Left'].copy()
    
    # Create match-player ID to avoid cumulative wicket counting
    lh_data['Match_Player'] = lh_data['Match⬆'] + '_' + lh_data['Player']
    
    # Get max wickets per match (cumulative), then sum across matches
    match_stats = lh_data.groupby('Match_Player').agg({
        'Player': 'first',
        'Team': 'first',
        'runs_this_ball': 'sum',
        'Match⬆': 'count',  # Count balls
        'W': 'max',  # Max wickets in this match
        '0': 'sum'
    }).rename(columns={'Match⬆': 'balls'})
    
    # Now aggregate by player
    bowler_stats = match_stats.groupby('Player').agg({
        'Team': 'first',
        'runs_this_ball': 'sum',
        'balls': 'sum',
        'W': 'sum',  # Sum of max wickets across matches
        '0': 'sum'
    }).rename(columns={'runs_this_ball': 'runs'})
    
    bowler_stats['overs'] = (bowler_stats['balls'] / 6).round(1)
    bowler_stats = bowler_stats[bowler_stats['overs'] >= min_overs]
    bowler_stats['econ'] = ((bowler_stats['runs'] / bowler_stats['overs'])).round(2)
    bowler_stats['sr'] = (bowler_stats['balls'] / bowler_stats['W'].replace(0, 1)).round(1)
    bowler_stats['dot%'] = ((bowler_stats['0'] / bowler_stats['balls']) * 100).round(1)
    
    return bowler_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'sr', 'dot%']]


def get_most_economical_bowlers(stats, min_overs=10):
    """Get most economical bowlers overall."""
    df_copy = stats.df.copy()
    
    # Create match-player ID
    df_copy['Match_Player'] = df_copy['Match⬆'] + '_' + df_copy['Player']
    
    # Get stats per match first
    match_stats = df_copy.groupby('Match_Player').agg({
        'Player': 'first',
        'Team': 'first',
        'runs_this_ball': 'sum',
        'Match⬆': 'count',  # Count balls
        'W': 'max',  # Max wickets in this match (cumulative)
        '0': 'sum',
        '4': 'sum',
        '6': 'sum'
    }).rename(columns={'Match⬆': 'balls'})
    
    # Aggregate by player
    bowler_stats = match_stats.groupby('Player').agg({
        'Team': 'first',
        'runs_this_ball': 'sum',
        'balls': 'sum',
        'W': 'sum',  # Sum of max wickets across matches
        '0': 'sum',
        '4': 'sum',
        '6': 'sum'
    }).rename(columns={'runs_this_ball': 'runs'})
    
    bowler_stats['overs'] = (bowler_stats['balls'] / 6).round(1)
    bowler_stats = bowler_stats[bowler_stats['overs'] >= min_overs]
    bowler_stats['econ'] = ((bowler_stats['runs'] / bowler_stats['overs'])).round(2)
    bowler_stats['sr'] = (bowler_stats['balls'] / bowler_stats['W'].replace(0, 1)).round(1)
    bowler_stats['dot%'] = ((bowler_stats['0'] / bowler_stats['balls']) * 100).round(1)
    bowler_stats['boundary%'] = (((bowler_stats['4'] + bowler_stats['6']) / bowler_stats['balls']) * 100).round(1)
    
    return bowler_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'sr', 'dot%', 'boundary%']]


def get_most_wickets(stats, min_overs=10):
    """Get bowlers with most wickets."""
    df_copy = stats.df.copy()
    
    # Create match-player ID
    df_copy['Match_Player'] = df_copy['Match⬆'] + '_' + df_copy['Player']
    
    # Get stats per match first
    match_stats = df_copy.groupby('Match_Player').agg({
        'Player': 'first',
        'Team': 'first',
        'runs_this_ball': 'sum',
        'Match⬆': 'count',  # Count balls using different column
        'W': 'max',  # Max wickets in this match (cumulative)
        '0': 'sum'
    }).rename(columns={'Match⬆': 'balls'})
    
    # Aggregate by player
    bowler_stats = match_stats.groupby('Player').agg({
        'Team': 'first',
        'runs_this_ball': 'sum',
        'balls': 'sum',
        'W': 'sum',  # Sum of max wickets across matches
        '0': 'sum'
    }).rename(columns={'runs_this_ball': 'runs'})
    
    bowler_stats['overs'] = (bowler_stats['balls'] / 6).round(1)
    bowler_stats = bowler_stats[bowler_stats['overs'] >= min_overs]
    bowler_stats['econ'] = ((bowler_stats['runs'] / bowler_stats['overs'])).round(2)
    bowler_stats['sr'] = (bowler_stats['balls'] / bowler_stats['W'].replace(0, 1)).round(1)
    bowler_stats['avg'] = (bowler_stats['runs'] / bowler_stats['W'].replace(0, 1)).round(2)
    
    return bowler_stats.sort_values('W', ascending=False)[['Team', 'overs', 'W', 'avg', 'econ', 'sr']]


def get_best_by_ground(stats, top_n=5):
    """Get best performers at each ground."""
    results = []
    
    for ground in stats.df['Ground Name'].unique():
        ground_data = stats.df[stats.df['Ground Name'] == ground]
        
        # Best batsmen at this ground
        batsman_stats = ground_data.groupby('Batsman').agg({
            'runs_this_ball': 'sum',
            'Batsman': 'count',
            'Team.1': 'first'
        }).rename(columns={'Batsman': 'balls', 'runs_this_ball': 'runs', 'Team.1': 'Team'})
        
        batsman_stats = batsman_stats[batsman_stats['balls'] >= 30]
        batsman_stats['sr'] = ((batsman_stats['runs'] / batsman_stats['balls']) * 100).round(2)
        
        top_batsmen = batsman_stats.nlargest(top_n, 'runs')
        
        for idx, row in top_batsmen.iterrows():
            results.append({
                'Ground': ground,
                'Player': idx,
                'Type': 'Batsman',
                'Team': row['Team'],
                'Runs': int(row['runs']),
                'Balls': int(row['balls']),
                'SR': row['sr']
            })
    
    return pd.DataFrame(results)


def get_phase_leaders(stats, phase='powerplay'):
    """Get best performers in specific phase (powerplay, middle, death)."""
    if phase == 'powerplay':
        phase_data = stats.df[stats.df['Overs'] < 6].copy()
        title = "Powerplay (Overs 1-6)"
    elif phase == 'middle':
        phase_data = stats.df[(stats.df['Overs'] >= 6) & (stats.df['Overs'] < 16)].copy()
        title = "Middle Overs (7-16)"
    else:  # death
        phase_data = stats.df[stats.df['Overs'] >= 16].copy()
        title = "Death Overs (17-20)"
    
    # Batting leaders
    batting_stats = phase_data.groupby('Batsman').agg({
        'runs_this_ball': 'sum',
        'Batsman': 'count',
        '4': 'sum',
        '6': 'sum',
        'Team.1': 'first'
    }).rename(columns={'Batsman': 'balls', 'runs_this_ball': 'runs', 'Team.1': 'Team'})
    
    batting_stats = batting_stats[batting_stats['balls'] >= 20]
    batting_stats['sr'] = ((batting_stats['runs'] / batting_stats['balls']) * 100).round(2)
    batting_leaders = batting_stats.sort_values('runs', ascending=False)[['Team', 'runs', 'balls', 'sr', '4', '6']].head(15)
    
    # Bowling leaders - need to handle cumulative wickets correctly
    phase_data['Match_Player'] = phase_data['Match⬆'] + '_' + phase_data['Player']
    
    match_stats = phase_data.groupby('Match_Player').agg({
        'Player': 'first',
        'Team': 'first',
        'runs_this_ball': 'sum',
        'Match⬆': 'count',  # Count balls
        'W': 'max',  # Max wickets in this phase of this match
        '0': 'sum'
    }).rename(columns={'Match⬆': 'balls'})
    
    bowling_stats = match_stats.groupby('Player').agg({
        'Team': 'first',
        'runs_this_ball': 'sum',
        'balls': 'sum',
        'W': 'sum',  # Sum of max wickets across matches
        '0': 'sum'
    }).rename(columns={'runs_this_ball': 'runs'})
    
    bowling_stats['overs'] = (bowling_stats['balls'] / 6).round(1)
    bowling_stats = bowling_stats[bowling_stats['overs'] >= 3]
    bowling_stats['econ'] = ((bowling_stats['runs'] / bowling_stats['overs'])).round(2)
    bowling_stats['dot%'] = ((bowling_stats['0'] / bowling_stats['balls']) * 100).round(1)
    bowling_leaders = bowling_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'dot%']].head(15)
    
    return batting_leaders, bowling_leaders, title
