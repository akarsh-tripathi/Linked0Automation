import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import subprocess
import time
import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import signal
import sys
from bot.scraper import run_bot
from bot.decision import DecisionEngine
from bot_manager import bot_manager

# Configure page
st.set_page_config(
    page_title="LinkedIn Bot Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def read_log_file(log_file_path="bot_logs.log", max_lines=1000):
    """Read and parse log file"""
    try:
        if not os.path.exists(log_file_path):
            return pd.DataFrame(columns=['timestamp', 'level', 'message'])
        
        logs = []
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Get last max_lines
            lines = lines[-max_lines:] if len(lines) > max_lines else lines
            
            for line in lines:
                line = line.strip()
                if line:
                    try:
                        # Parse log format: timestamp - level - message
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp_str = parts[0]
                            level = parts[1]
                            message = parts[2]
                            
                            # Parse timestamp
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                            
                            logs.append({
                                'timestamp': timestamp,
                                'level': level,
                                'message': message,
                                'raw': line
                            })
                    except Exception as e:
                        # If parsing fails, add as raw message
                        logs.append({
                            'timestamp': datetime.now(),
                            'level': 'UNKNOWN',
                            'message': line,
                            'raw': line
                        })
        
        return pd.DataFrame(logs)
    except Exception as e:
        st.error(f"Error reading log file: {e}")
        return pd.DataFrame(columns=['timestamp', 'level', 'message', 'raw'])

def get_posts_from_sheets():
    """Get posts data from Google Sheets"""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        
        if not os.path.exists("config/credentials.json"):
            return pd.DataFrame(columns=['timestamp', 'name', 'content', 'decision'])
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "config/credentials.json", scope
        )
        client = gspread.authorize(creds)
        sheet = client.open("LinkedIn Auto Connect").sheet1
        
        # Get all records
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        
        if not df.empty and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except Exception as e:
        st.warning(f"Could not connect to Google Sheets: {e}")
        return pd.DataFrame(columns=['timestamp', 'name', 'content', 'decision'])

# Main dashboard
def main():
    st.title("🤖 LinkedIn Bot Dashboard")
    st.markdown("Monitor and control your LinkedIn automation bot")
    
    # Get bot status
    bot_status = bot_manager.get_status()
    next_run = bot_manager.get_next_run_time()
    
    # Sidebar controls
    st.sidebar.header("🎛️ Bot Controls")
    
    # Status display
    status_emoji = "🟢 Running" if bot_status['is_running'] else "🔴 Stopped"
    st.sidebar.markdown(f"**Status:** {status_emoji}")
    
    if bot_status['last_run_time']:
        st.sidebar.markdown(f"**Last Run:** {bot_status['last_run_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    if next_run:
        st.sidebar.markdown(f"**Next Run:** {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.sidebar.markdown(f"**Total Runs:** {bot_status['run_count']}")
    st.sidebar.markdown(f"**Errors:** {bot_status['error_count']}")
    
    # Interval setting
    interval_minutes = st.sidebar.slider("Interval (minutes):", 1, 60, 5)
    
    # Control buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("▶️ Start Scheduled", key="start_scheduled"):
            if bot_manager.start_scheduled_bot(interval_minutes):
                st.success("Scheduled bot started!")
                st.rerun()
            else:
                st.error("Failed to start bot or already running")
    
    with col2:
        if st.button("⏹️ Stop Scheduled", key="stop_scheduled"):
            if bot_manager.stop_scheduled_bot():
                st.success("Scheduled bot stopped!")
                st.rerun()
            else:
                st.error("Failed to stop bot or not running")
    
    if st.sidebar.button("🔄 Run Once", key="run_once"):
        with st.spinner("Running bot..."):
            if bot_manager.run_once():
                st.success("Bot run completed!")
                st.rerun()
            else:
                st.error("Bot run failed!")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=True)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📝 Logs", "📄 Posts", "⚙️ Settings"])
    
    with tab1:
        st.header("📊 Overview")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        # Read recent logs for metrics
        logs_df = read_log_file(max_lines=100)
        posts_df = get_posts_from_sheets()
        
        with col1:
            st.metric("Bot Status", "Running" if bot_status['is_running'] else "Stopped")
        
        with col2:
            recent_logs = len(logs_df[logs_df['timestamp'] > datetime.now() - timedelta(hours=24)]) if not logs_df.empty else 0
            st.metric("Log Entries (24h)", recent_logs)
        
        with col3:
            if not posts_df.empty:
                connected_today = len(posts_df[
                    (posts_df['decision'] == 'Connected') & 
                    (posts_df['timestamp'] > datetime.now() - timedelta(days=1))
                ]) if 'timestamp' in posts_df.columns else 0
            else:
                connected_today = 0
            st.metric("Connections Today", connected_today)
        
        with col4:
            if not posts_df.empty:
                total_posts = len(posts_df)
            else:
                total_posts = 0
            st.metric("Total Posts Processed", total_posts)
        
        # Bot performance metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Bot Runs", bot_status['run_count'])
        with col2:
            st.metric("Bot Errors", bot_status['error_count'])
        with col3:
            success_rate = ((bot_status['run_count'] - bot_status['error_count']) / bot_status['run_count'] * 100) if bot_status['run_count'] > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Recent activity chart
        if not logs_df.empty:
            st.subheader("📈 Recent Activity")
            
            # Group logs by hour
            logs_df['hour'] = logs_df['timestamp'].dt.floor('H')
            hourly_logs = logs_df.groupby(['hour', 'level']).size().reset_index(name='count')
            
            fig = px.bar(hourly_logs, x='hour', y='count', color='level',
                        title="Log Activity by Hour",
                        color_discrete_map={
                            'INFO': '#2E8B57',
                            'WARNING': '#FF8C00',
                            'ERROR': '#DC143C'
                        })
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("📝 Recent Logs")
        
        # Log level filter
        log_levels = ['ALL', 'INFO', 'WARNING', 'ERROR']
        selected_level = st.selectbox("Filter by level:", log_levels)
        
        # Number of logs to show
        max_logs = st.slider("Max logs to display:", 10, 1000, 100)
        
        # Read and display logs
        logs_df = read_log_file(max_lines=max_logs)
        
        if not logs_df.empty:
            if selected_level != 'ALL':
                logs_df = logs_df[logs_df['level'] == selected_level]
            
            # Sort by timestamp descending
            logs_df = logs_df.sort_values('timestamp', ascending=False)
            
            # Display logs with color coding
            for _, log in logs_df.iterrows():
                level_color = {
                    'INFO': '🟢',
                    'WARNING': '🟡',
                    'ERROR': '🔴'
                }.get(log['level'], '⚪')
                
                timestamp_str = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                st.markdown(f"{level_color} **{timestamp_str}** [{log['level']}] {log['message']}")
        else:
            st.info("No logs found. The bot may not have run yet.")
    
    with tab3:
        st.header("📄 Posts Analysis")
        
        posts_df = get_posts_from_sheets()
        
        if not posts_df.empty:
            # Decision distribution
            col1, col2 = st.columns(2)
            
            with col1:
                if 'decision' in posts_df.columns:
                    decision_counts = posts_df['decision'].value_counts()
                    fig = px.pie(values=decision_counts.values, names=decision_counts.index,
                               title="Decision Distribution")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'timestamp' in posts_df.columns:
                    posts_df['date'] = pd.to_datetime(posts_df['timestamp']).dt.date
                    daily_posts = posts_df.groupby('date').size().reset_index(name='count')
                    fig = px.line(daily_posts, x='date', y='count',
                                title="Posts Processed Daily")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recent posts table
            st.subheader("Recent Posts")
            
            # Filter options
            decision_filter = st.selectbox("Filter by decision:", 
                                         ['All'] + list(posts_df['decision'].unique()) if 'decision' in posts_df.columns else ['All'])
            
            display_df = posts_df.copy()
            if decision_filter != 'All':
                display_df = display_df[display_df['decision'] == decision_filter]
            
            # Sort by timestamp if available
            if 'timestamp' in display_df.columns:
                display_df = display_df.sort_values('timestamp', ascending=False)
            
            # Display top 50 posts
            st.dataframe(display_df.head(50), use_container_width=True)
            
        else:
            st.info("No posts data found. Make sure Google Sheets integration is configured or run the bot first.")
    
    with tab4:
        st.header("⚙️ Settings")
        
        # Bot configuration
        st.subheader("🤖 Bot Configuration")
        
        # Display current prompt
        current_prompt = "I want to connect to people who are hiring for Software Engineer roles with experience of more than 1 year"
        st.text_area("Current Search Prompt:", value=current_prompt, disabled=True, height=100)
        
        # File status
        st.subheader("📁 File Status")
        
        files_to_check = [
            ("Log File", "bot_logs.log"),
            ("Cookies", "config/cookies.pkl"),
            ("Credentials", "config/credentials.json")
        ]
        
        for name, path in files_to_check:
            exists = os.path.exists(path)
            status = "✅ Found" if exists else "❌ Missing"
            size = os.path.getsize(path) if exists else 0
            st.markdown(f"**{name}:** {status} ({size} bytes)")
        
        # System info
        st.subheader("💻 System Information")
        st.markdown(f"**Python:** {sys.version}")
        st.markdown(f"**Working Directory:** {os.getcwd()}")
        st.markdown(f"**Process ID:** {os.getpid()}")
        
        # Bot manager status
        st.subheader("🔧 Bot Manager Status")
        st.json(bot_status)

if __name__ == "__main__":
    main() 