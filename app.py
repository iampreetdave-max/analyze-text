"""
WhatsApp Chat Analyzer - Streamlit Application
Main application file
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from modules.parser import ChatParser
from modules.analyzer import ChatAnalyzer
from modules.visualizer import Visualizer
from modules.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="ChatLyze - WhatsApp Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 300;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 0.875rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_data' not in st.session_state:
        st.session_state.chat_data = None
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'messages_df' not in st.session_state:
        st.session_state.messages_df = None

def main():
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 💬 ChatLyze")
        st.markdown("**Advanced WhatsApp Analytics Engine**")
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "Upload WhatsApp Chat Export",
            type=['txt'],
            help="Export your chat without media from WhatsApp"
        )
        
        if uploaded_file is not None:
            if st.button("🔍 Analyze Chat", type="primary", use_container_width=True):
                with st.spinner("Parsing chat data..."):
                    # Read and parse the file
                    content = uploaded_file.read().decode('utf-8')
                    parser = ChatParser()
                    messages = parser.parse(content)
                    
                    if not messages:
                        st.error("❌ Could not parse chat. Please check the file format.")
                        return
                    
                    st.session_state.messages_df = messages
                    
                with st.spinner("Analyzing patterns..."):
                    analyzer = ChatAnalyzer()
                    st.session_state.analysis = analyzer.analyze(messages)
                
                st.success(f"✅ Analyzed {len(messages)} messages!")
        
        st.markdown("---")
        
        # Export options
        if st.session_state.analysis is not None:
            st.markdown("### 📥 Export Reports")
            
            report_gen = ReportGenerator()
            
            # JSON Export
            json_data = report_gen.generate_json(
                st.session_state.analysis,
                uploaded_file.name if uploaded_file else "chat.txt"
            )
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            
            # CSV Export
            csv_data = report_gen.generate_csv(st.session_state.analysis)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # PDF Export
            if st.button("📑 Generate PDF Report", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_data = report_gen.generate_pdf(
                        st.session_state.analysis,
                        uploaded_file.name if uploaded_file else "chat.txt"
                    )
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_data,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        st.markdown("---")
        st.markdown("""
        <small>
        **How to Export Chat:**
        1. Open WhatsApp
        2. Select chat → Menu (⋮)
        3. More → Export chat
        4. Choose "Without Media"
        5. Upload .txt file here
        
        🔒 All data processed locally
        </small>
        """, unsafe_allow_html=True)
    
    # Main content
    if st.session_state.analysis is None:
        # Landing page
        st.markdown('<h1 class="main-header">CHAT<strong>LYZE</strong></h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Advanced Analytics Engine for WhatsApp Chats</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### ⚡ Instant Analysis")
            st.write("Real-time processing of your chat data with advanced algorithms")
        
        with col2:
            st.markdown("### 🧠 Deep Insights")
            st.write("Sentiment analysis, patterns, and behavioral analytics")
        
        with col3:
            st.markdown("### 🔒 100% Private")
            st.write("All processing happens locally - no data sent to servers")
        
        st.markdown("---")
        
        with st.expander("📋 Features", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                - 📊 **Message Statistics** - Count, frequency, patterns
                - 👥 **User Analytics** - Individual performance metrics
                - 😊 **Emoji Analysis** - Most used emojis and trends
                - ⏰ **Time Patterns** - Hourly and daily activity
                - 📈 **Activity Timeline** - Visual chat history
                """)
            
            with col2:
                st.markdown("""
                - 💭 **Sentiment Analysis** - Positive/negative detection
                - 🏆 **Champions** - Top performers in various categories
                - 📱 **Media Tracking** - Files, links, and media count
                - 💬 **Best Quotes** - Highest rated messages
                - 📥 **Export Reports** - JSON, CSV, and PDF formats
                """)
    
    else:
        # Analysis results
        analysis = st.session_state.analysis
        
        st.markdown(f'<h1 class="main-header">Analysis Complete</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-header">{uploaded_file.name if uploaded_file else "Chat Analysis"}</p>', unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📨 Total Messages", f"{analysis['total_messages']:,}")
        
        with col2:
            st.metric("👥 Participants", len(analysis['users']))
        
        with col3:
            st.metric("😊 Total Emojis", f"{sum([e[1] for e in analysis['top_emojis']]):,}")
        
        with col4:
            st.metric("📷 Media Shared", f"{analysis['media_count']:,}")
        
        st.markdown("---")
        
        # Tabs for different views
        tabs = st.tabs(["📊 Overview", "👥 Users", "📈 Insights", "💬 Best Lines", "🏆 Champions"])
        
        with tabs[0]:  # Overview
            show_overview(analysis)
        
        with tabs[1]:  # Users
            show_users(analysis)
        
        with tabs[2]:  # Insights
            show_insights(analysis)
        
        with tabs[3]:  # Best Lines
            show_best_lines(analysis)
        
        with tabs[4]:  # Champions
            show_champions(analysis)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.875rem;'>
        <p>🔒 ALL DATA PROCESSED LOCALLY • NO SERVER COMMUNICATION • 100% PRIVATE</p>
        <p>Analyzed {total} messages from {users} participants</p>
        </div>
        """.format(
            total=f"{analysis['total_messages']:,}",
            users=len(analysis['users'])
        ), unsafe_allow_html=True)

def show_overview(analysis):
    """Display overview analytics"""
    visualizer = Visualizer()
    
    # Activity Timeline
    st.markdown("### 📅 Activity Timeline (Last 30 Days)")
    fig = visualizer.plot_daily_activity(analysis['daily_activity'])
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Hourly Distribution")
        fig = visualizer.plot_hourly_activity(analysis['hourly_activity'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📆 Weekday Activity")
        fig = visualizer.plot_weekday_activity(analysis['weekday_activity'])
        st.plotly_chart(fig, use_container_width=True)
    
    # User comparison radar
    st.markdown("### 🎯 User Comparison Matrix")
    fig = visualizer.plot_user_radar(analysis['users'])
    st.plotly_chart(fig, use_container_width=True)

def show_users(analysis):
    """Display user-specific analytics"""
    users = sorted(analysis['users'].items(), key=lambda x: x[1]['message_count'], reverse=True)
    
    for idx, (username, stats) in enumerate(users):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {username}")
                st.caption(f"Rank #{idx + 1}")
            
            with col2:
                st.metric("Messages", f"{stats['message_count']:,}")
            
            # Stats grid
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.metric("Words", f"{stats['word_count']:,}")
            
            with col2:
                st.metric("Avg Length", f"{stats['avg_message_length']:.1f}")
            
            with col3:
                st.metric("Emojis", f"{stats['emoji_count']:,}")
            
            with col4:
                st.metric("Media", f"{stats['media_count']:,}")
            
            with col5:
                st.metric("Questions", f"{stats['question_count']:,}")
            
            with col6:
                sentiment = stats['sentiment_score']
                st.metric("Sentiment", f"{'+' if sentiment > 0 else ''}{sentiment}")
            
            # Top emojis
            if stats['emojis']:
                st.markdown("**Top Emojis:**")
                emoji_cols = st.columns(min(10, len(stats['emojis'])))
                top_emojis = sorted(stats['emojis'].items(), key=lambda x: x[1], reverse=True)[:10]
                
                for idx, (emoji, count) in enumerate(top_emojis):
                    with emoji_cols[idx]:
                        st.markdown(f"<div style='text-align: center; font-size: 2rem;'>{emoji}</div>", unsafe_allow_html=True)
                        st.caption(f"{count}")
            
            st.markdown("---")

def show_insights(analysis):
    """Display insights and patterns"""
    visualizer = Visualizer()
    
    # Sentiment analysis
    st.markdown("### 💭 Sentiment Analysis")
    fig = visualizer.plot_sentiment(analysis['users'])
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚡ Fastest Responders")
        users_with_response = [(name, stats) for name, stats in analysis['users'].items() 
                               if stats.get('avg_response_time') is not None]
        users_sorted = sorted(users_with_response, key=lambda x: x[1]['avg_response_time'])[:5]
        
        for idx, (name, stats) in enumerate(users_sorted):
            st.write(f"**#{idx+1}** {name} - {stats['avg_response_time']:.1f} minutes")
    
    with col2:
        st.markdown("### 🔥 Conversation Starters")
        users_sorted = sorted(analysis['users'].items(), 
                            key=lambda x: x[1]['conversation_starters'], reverse=True)[:5]
        
        for idx, (name, stats) in enumerate(users_sorted):
            st.write(f"**#{idx+1}** {name} - {stats['conversation_starters']} times")
    
    # Peak activity hours
    st.markdown("### 📊 Peak Activity Hours")
    hourly_sorted = sorted(enumerate(analysis['hourly_activity']), key=lambda x: x[1], reverse=True)[:5]
    
    cols = st.columns(5)
    for idx, (hour, count) in enumerate(hourly_sorted):
        with cols[idx]:
            st.metric(f"{hour:02d}:00", f"{count:,}", "messages")
    
    # Emoji frequency
    st.markdown("### 😊 Most Used Emojis")
    emoji_cols = st.columns(min(10, len(analysis['top_emojis'])))
    
    for idx, (emoji, count) in enumerate(analysis['top_emojis'][:10]):
        with emoji_cols[idx]:
            st.markdown(f"<div style='text-align: center; font-size: 3rem;'>{emoji}</div>", unsafe_allow_html=True)
            st.caption(f"{count:,} uses")

def show_best_lines(analysis):
    """Display best rated messages"""
    for username, stats in sorted(analysis['users'].items(), 
                                  key=lambda x: x[1]['message_count'], reverse=True):
        if stats['best_lines']:
            st.markdown(f"### {username}")
            st.caption("Top Rated Messages")
            
            for idx, line in enumerate(stats['best_lines']):
                with st.container():
                    st.markdown(f"**⭐ Quality Score: {line['score']}**")
                    st.info(line['message'])
                    st.caption(f"{line['timestamp'].strftime('%b %d, %Y at %I:%M %p')}")
                    st.markdown("---")

def show_champions(analysis):
    """Display champion categories"""
    users = analysis['users']
    
    # Create champion cards
    champions = [
        {
            'icon': '🏆',
            'title': 'Message Champion',
            'user': max(users.items(), key=lambda x: x[1]['message_count']),
            'metric': 'message_count',
            'label': 'Messages Sent'
        },
        {
            'icon': '📝',
            'title': 'Word Master',
            'user': max(users.items(), key=lambda x: x[1]['word_count']),
            'metric': 'word_count',
            'label': 'Total Words'
        },
        {
            'icon': '😊',
            'title': 'Emoji King/Queen',
            'user': max(users.items(), key=lambda x: x[1]['emoji_count']),
            'metric': 'emoji_count',
            'label': 'Emojis Used'
        },
        {
            'icon': '📷',
            'title': 'Media Sharer',
            'user': max(users.items(), key=lambda x: x[1]['media_count']),
            'metric': 'media_count',
            'label': 'Media Shared'
        },
        {
            'icon': '❓',
            'title': 'Curious Mind',
            'user': max(users.items(), key=lambda x: x[1]['question_count']),
            'metric': 'question_count',
            'label': 'Questions Asked'
        },
        {
            'icon': '🌙',
            'title': 'Night Owl',
            'user': max(users.items(), key=lambda x: x[1]['night_owl_score']),
            'metric': 'night_owl_score',
            'label': 'Late Messages'
        },
        {
            'icon': '🌅',
            'title': 'Early Bird',
            'user': max(users.items(), key=lambda x: x[1]['morning_score']),
            'metric': 'morning_score',
            'label': 'Morning Messages'
        },
        {
            'icon': '💬',
            'title': 'Conversation Starter',
            'user': max(users.items(), key=lambda x: x[1]['conversation_starters']),
            'metric': 'conversation_starters',
            'label': 'Convos Started'
        },
        {
            'icon': '😄',
            'title': 'Positive Vibes',
            'user': max(users.items(), key=lambda x: x[1]['sentiment_score']),
            'metric': 'sentiment_score',
            'label': 'Sentiment Score'
        }
    ]
    
    # Display in 3 columns
    for i in range(0, len(champions), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(champions):
                champion = champions[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 2rem; 
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                border-radius: 10px; color: white; margin-bottom: 1rem;'>
                        <div style='font-size: 3rem;'>{champion['icon']}</div>
                        <h4 style='margin: 1rem 0;'>{champion['title']}</h4>
                        <h2 style='margin: 0.5rem 0;'>{champion['user'][0]}</h2>
                        <h1 style='margin: 0.5rem 0;'>{champion['user'][1][champion['metric']]:,}</h1>
                        <p style='opacity: 0.9; font-size: 0.875rem;'>{champion['label']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Fun facts
    st.markdown("### 🎯 Fun Facts")
    
    total_msgs = analysis['total_messages']
    total_users = len(users)
    total_words = analysis['total_words']
    media_count = analysis['media_count']
    deleted_count = analysis.get('deleted_messages', 0)
    
    peak_hour = max(enumerate(analysis['hourly_activity']), key=lambda x: x[1])[0]
    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    peak_day = weekdays[max(enumerate(analysis['weekday_activity']), key=lambda x: x[1])[0]]
    
    facts = [
        f"📊 Average {total_msgs // total_users:,} messages per person",
        f"⚡ Most active hour: {peak_hour:02d}:00",
        f"📅 Most active day: {peak_day}",
        f"💭 Average message length: {total_words / total_msgs:.1f} words",
        f"🎯 {(media_count / total_msgs * 100):.1f}% of messages contain media",
        f"🗑️ {(deleted_count / total_msgs * 100):.1f}% of messages were deleted"
    ]
    
    for fact in facts:
        st.info(fact)

if __name__ == "__main__":
    main()
