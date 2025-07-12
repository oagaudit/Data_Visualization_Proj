# -*- coding: utf-8 -*-
"""
Final Project - Football Data Analysis (Summer 2025) - Interactive Streamlit Dashboard (Plotly Version)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- Data Loading and Preparation with Caching ---
@st.cache_data
def load_data():
    """Loads and preprocesses the football match data."""
    try:
        df = pd.read_csv('Matches.csv', low_memory=False)
    except FileNotFoundError:
        st.error("Error: 'Matches.csv' not found. Please make sure the dataset is in the same directory.")
        return None

    df['MatchDate'] = pd.to_datetime(df['MatchDate'], errors='coerce')
    df['Season'] = df['MatchDate'].apply(lambda x: x.year if x.month < 8 else x.year + 1)
    df['TotalGoals'] = df['FTHome'] + df['FTAway']
    df['TotalCorners'] = df['HomeCorners'] + df['AwayCorners']
    df['Form5Difference'] = df['Form5Home'] - df['Form5Away']
    return df

# --- Main App ---
st.title("Decoding the Beautiful Game: Interactive 25-Year Football Analysis")
st.markdown("Interactive Dashboard for Final Project (Summer 2025)")

df = load_data()

if df is not None:
    # --- Sidebar for Navigation ---
    st.sidebar.title("Navigation")
    visualization_option = st.sidebar.selectbox(
        "Choose a Visualization:",
        [
            "1. Evolution of Goals Over Seasons",
            "2. Top 15 High-Scoring Leagues",
            "3. Match Outcomes in Top 5 Leagues",
            "4. Distribution of Home vs. Away Goals",
            "5. Elo Rating vs. Goals Scored",
            "6. Shots vs. Goals Efficiency",
            "7. Impact of Recent Form on Outcome",
            "8. Fouls vs. Yellow Cards",
            "9. Corners vs. Goals by League",
            "10. Betting Odds vs. Reality"
        ]
    )

    # --- Visualizations (Plotly Version) ---
    
    # 1. Evolution of Goals Over Seasons
    if visualization_option == "1. Evolution of Goals Over Seasons":
        st.header("1. Evolution of Average Goals Per Game Over Seasons (Interactive)")
        avg_goals = df.groupby('Season')['TotalGoals'].mean().reset_index()
        avg_goals = avg_goals[avg_goals['Season'] < 2025]
        
        fig = px.line(
            avg_goals, x='Season', y='TotalGoals',
            markers=True, title='Average Goals Per Game (2000-2024)',
            labels={'TotalGoals': 'Avg Goals', 'Season': 'Season'}
        )
        fig.update_traces(line_color='dodgerblue', line_width=2.5)
        fig.update_layout(hovermode="x unified", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # 2. Top 15 High-Scoring Leagues
    elif visualization_option == "2. Top 15 High-Scoring Leagues":
        st.header("2. Top 15 Leagues with Highest Average Goals (Interactive)")
        leagues = df['Division'].value_counts()[df['Division'].value_counts() > 1000].index
        df_filtered = df[df['Division'].isin(leagues)]
        avg_goals = df_filtered.groupby('Division')['TotalGoals'].mean().nlargest(15).reset_index()
        
        fig = px.bar(
            avg_goals, x='Division', y='TotalGoals',
            color='TotalGoals', color_continuous_scale='Viridis',
            title='Top 15 Leagues by Average Goals',
            labels={'TotalGoals': 'Avg Goals/Game', 'Division': 'League'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # 3. Match Outcomes in Top 5 Leagues
    elif visualization_option == "3. Match Outcomes in Top 5 Leagues":
        st.header("3. Match Outcomes in Top 5 Leagues (Interactive)")
        top_leagues = ['E0', 'SP1', 'D1', 'I1', 'F1']
        df_top5 = df[df['Division'].isin(top_leagues)]
        
        fig = px.sunburst(
            df_top5, path=['Division', 'FTResult'],
            color='FTResult', color_discrete_map={'H': '#1f77b4', 'D': '#ff7f0e', 'A': '#2ca02c'},
            title='Result Distribution by League'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 4. Distribution of Home vs. Away Goals
    elif visualization_option == "4. Distribution of Home vs. Away Goals":
        st.header("4. Home vs Away Goals Distribution (Interactive)")
        
        fig = go.Figure()
        fig.add_trace(go.Violin(
            y=df['FTHome'], name='Home Goals',
            box_visible=True, line_color='blue'
        ))
        fig.add_trace(go.Violin(
            y=df['FTAway'], name='Away Goals',
            box_visible=True, line_color='red'
        ))
        fig.update_layout(
            title='Goals Distribution Comparison',
            yaxis_title='Number of Goals'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 5. Elo Rating vs. Goals Scored
    elif visualization_option == "5. Elo Rating vs. Goals Scored":
        st.header("5. Elo Rating vs Goals Scored (Interactive)")
        df_sample = df.dropna(subset=['HomeElo', 'FTHome']).sample(n=5000)
        
        fig = px.scatter(
            df_sample, x='HomeElo', y='FTHome',
            trendline="lowess", opacity=0.3,
            title='Team Strength vs Goal Production',
            labels={'HomeElo': 'Elo Rating', 'FTHome': 'Goals Scored'}
        )
        fig.update_traces(marker_color='rgba(0,100,80,0.2)')
        st.plotly_chart(fig, use_container_width=True)

    # 6. Shots vs. Goals Efficiency
    elif visualization_option == "6. Shots vs. Goals Efficiency":
        st.header("6. Shots Efficiency Analysis (Interactive)")
        df_shots = df[(df['HomeShots'] > 0) & (df['HomeTarget'] > 0) & (df['HomeShots'] < 40)]
        
        fig = px.scatter(
            df_shots, x='HomeShots', y='HomeTarget',
            color='FTHome', size='FTHome',
            color_continuous_scale='Viridis',
            title='Shots vs Shots on Target vs Goals',
            labels={'HomeShots': 'Total Shots', 'HomeTarget': 'Shots on Target', 'FTHome': 'Goals Scored'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # 7. Impact of Recent Form on Outcome
    elif visualization_option == "7. Impact of Recent Form on Outcome":
        st.header("7. Form Impact Analysis (Interactive)")
        
        fig = px.box(
            df, x='FTResult', y='Form5Difference',
            color='FTResult', color_discrete_map={'H': 'blue', 'D': 'orange', 'A': 'green'},
            category_orders={'FTResult': ['H', 'D', 'A']},
            labels={'Form5Difference': 'Form Difference (Home-Away)', 'FTResult': 'Match Result'}
        )
        fig.update_layout(
            title='Recent Form Impact on Results',
            xaxis_title_text='Match Result',
            yaxis_title_text='Form Difference (Last 5 Games)'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 8. Fouls vs. Yellow Cards
    elif visualization_option == "8. Fouls vs. Yellow Cards":
        st.header("8. Fouls vs Cards Analysis (Interactive)")
        fouls = pd.concat([df['HomeFouls'], df['AwayFouls']]).rename('Fouls')
        yellows = pd.concat([df['HomeYellow'], df['AwayYellow']]).rename('YellowCards')
        cards_df = pd.concat([fouls, yellows], axis=1).dropna()
        cards_df = cards_df[cards_df['Fouls'] < 40]
        
        fig = px.density_heatmap(
            cards_df, x='Fouls', y='YellowCards',
            nbinsx=20, nbinsy=20,
            color_continuous_scale='YlOrRd',
            title='Fouls vs Yellow Cards Density'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 9. Corners vs. Goals by League
    elif visualization_option == "9. Corners vs. Goals by League":
        st.header("9. Corners vs Goals Analysis (Interactive)")
        league_stats = df.groupby('Division').agg(
            AvgGoals=('TotalGoals', 'mean'),
            AvgCorners=('TotalCorners', 'mean'),
            MatchCount=('Division', 'size')
        ).reset_index()
        league_stats = league_stats[league_stats['MatchCount'] > 1000]
        
        fig = px.scatter(
            league_stats, x='AvgCorners', y='AvgGoals',
            size='MatchCount', color='MatchCount',
            hover_name='Division', trendline="ols",
            title='Corners vs Goals by League',
            labels={'AvgCorners': 'Avg Corners/Game', 'AvgGoals': 'Avg Goals/Game'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # 10. Betting Odds vs. Reality
    elif visualization_option == "10. Betting Odds vs. Reality":
        st.header("10. Betting Market Accuracy (Interactive)")
        df_odds = df[['OddHome', 'FTResult']].dropna().copy()
        df_odds['ImpliedProb'] = 1 / df_odds['OddHome']
        df_odds['ActualResult'] = (df_odds['FTResult'] == 'H').astype(int)
        df_odds['ProbBin'] = pd.cut(df_odds['ImpliedProb'], bins=np.arange(0, 1.1, 0.1))
        
        calibration = df_odds.groupby('ProbBin').agg(
            AvgImpliedProb=('ImpliedProb', 'mean'),
            ActualWinRate=('ActualResult', 'mean')
        ).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=calibration['AvgImpliedProb'],
            y=calibration['ActualWinRate'],
            mode='markers',
            marker=dict(size=12, color='royalblue')
        ))
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Perfect Calibration'
        ))
        fig.update_layout(
            title='Betting Odds Calibration',
            xaxis_title='Implied Probability',
            yaxis_title='Actual Win Rate',
            xaxis_range=[0,1],
            yaxis_range=[0,1]
        )
        st.plotly_chart(fig, use_container_width=True)
