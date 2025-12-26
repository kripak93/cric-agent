"""
Cricket Leaderboards
Functions to generate various cricket leaderboards from ball-by-ball data
"""

import pandas as pd
import streamlit as st


def get_best_vs_pace(stats, min_balls=50):
    """Get best batsmen against pace bowling."""
    pace_data = stats.df[stats.df['Kind'].isin(['Fast', 'Fast Medium', 'Medium Fast'])]
    
    batsman_stats = pace_data.groupby('Batsman').agg({
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


def get_best_vs_spin(stats, min_balls=50):
    """Get best batsmen against spin bowling."""
    spin_data = stats.df[stats.df['Kind'].isin(['Leg Spin', 'Off Spin', 'Slow', 'Slow Left-arm Orthodox'])]
    
    batsman_stats = spin_data.groupby('Batsman').agg({
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
    rh_data = stats.df[stats.df['B/H'] == 'Right']
    
    bowler_stats = rh_data.groupby('Player').agg({
        'runs_this_ball': 'sum',
        'Player': 'count',
        'W': 'sum',
        '0': 'sum',
        'Team': 'first'
    }).rename(columns={'Player': 'balls', 'runs_this_ball': 'runs'})
    
    bowler_stats['overs'] = (bowler_stats['balls'] / 6).round(1)
    bowler_stats = bowler_stats[bowler_stats['overs'] >= min_overs]
    bowler_stats['econ'] = ((bowler_stats['runs'] / bowler_stats['overs'])).round(2)
    bowler_stats['sr'] = (bowler_stats['balls'] / bowler_stats['W'].replace(0, 1)).round(1)
    bowler_stats['dot%'] = ((bowler_stats['0'] / bowler_stats['balls']) * 100).round(1)
    
    return bowler_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'sr', 'dot%']]


def get_best_bowlers_vs_lh(stats, min_overs=5):
    """Get best bowlers against left-handed batsmen."""
    lh_data = stats.df[stats.df['B/H'] == 'Left']
    
    bowler_stats = lh_data.groupby('Player').agg({
        'runs_this_ball': 'sum',
        'Player': 'count',
        'W': 'sum',
        '0': 'sum',
        'Team': 'first'
    }).rename(columns={'Player': 'balls', 'runs_this_ball': 'runs'})
    
    bowler_stats['overs'] = (bowler_stats['balls'] / 6).round(1)
    bowler_stats = bowler_stats[bowler_stats['overs'] >= min_overs]
    bowler_stats['econ'] = ((bowler_stats['runs'] / bowler_stats['overs'])).round(2)
    bowler_stats['sr'] = (bowler_stats['balls'] / bowler_stats['W'].replace(0, 1)).round(1)
    bowler_stats['dot%'] = ((bowler_stats['0'] / bowler_stats['balls']) * 100).round(1)
    
    return bowler_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'sr', 'dot%']]


def get_most_economical_bowlers(stats, min_overs=10):
    """Get most economical bowlers overall."""
    bowler_stats = stats.df.groupby('Player').agg({
        'runs_this_ball': 'sum',
        'Player': 'count',
        'W': 'sum',
        '0': 'sum',
        '4': 'sum',
        '6': 'sum',
        'Team': 'first'
    }).rename(columns={'Player': 'balls', 'runs_this_ball': 'runs'})
    
    bowler_stats['overs'] = (bowler_stats['balls'] / 6).round(1)
    bowler_stats = bowler_stats[bowler_stats['overs'] >= min_overs]
    bowler_stats['econ'] = ((bowler_stats['runs'] / bowler_stats['overs'])).round(2)
    bowler_stats['sr'] = (bowler_stats['balls'] / bowler_stats['W'].replace(0, 1)).round(1)
    bowler_stats['dot%'] = ((bowler_stats['0'] / bowler_stats['balls']) * 100).round(1)
    bowler_stats['boundary%'] = (((bowler_stats['4'] + bowler_stats['6']) / bowler_stats['balls']) * 100).round(1)
    
    return bowler_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'sr', 'dot%', 'boundary%']]


def get_most_wickets(stats, min_overs=10):
    """Get bowlers with most wickets."""
    bowler_stats = stats.df.groupby('Player').agg({
        'runs_this_ball': 'sum',
        'Player': 'count',
        'W': 'sum',
        '0': 'sum',
        'Team': 'first'
    }).rename(columns={'Player': 'balls', 'runs_this_ball': 'runs'})
    
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
        phase_data = stats.df[stats.df['Overs'] < 6]
        title = "Powerplay (Overs 1-6)"
    elif phase == 'middle':
        phase_data = stats.df[(stats.df['Overs'] >= 6) & (stats.df['Overs'] < 16)]
        title = "Middle Overs (7-16)"
    else:  # death
        phase_data = stats.df[stats.df['Overs'] >= 16]
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
    
    # Bowling leaders
    bowling_stats = phase_data.groupby('Player').agg({
        'runs_this_ball': 'sum',
        'Player': 'count',
        'W': 'sum',
        '0': 'sum',
        'Team': 'first'
    }).rename(columns={'Player': 'balls', 'runs_this_ball': 'runs'})
    
    bowling_stats['overs'] = (bowling_stats['balls'] / 6).round(1)
    bowling_stats = bowling_stats[bowling_stats['overs'] >= 3]
    bowling_stats['econ'] = ((bowling_stats['runs'] / bowling_stats['overs'])).round(2)
    bowling_stats['dot%'] = ((bowling_stats['0'] / bowling_stats['balls']) * 100).round(1)
    bowling_leaders = bowling_stats.sort_values('econ', ascending=True)[['Team', 'overs', 'runs', 'W', 'econ', 'dot%']].head(15)
    
    return batting_leaders, bowling_leaders, title
