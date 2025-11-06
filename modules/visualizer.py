"""
WhatsApp Chat Visualizer Module
Creates interactive visualizations using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class Visualizer:
    """Visualizer for WhatsApp chat analytics"""

    def __init__(self):
        self.color_scheme = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'background': '#f8f9fa'
        }

    def plot_daily_activity(self, daily_data):
        """
        Plot daily activity timeline

        Args:
            daily_data (list): List of dicts with 'date' and 'count'

        Returns:
            plotly.graph_objects.Figure
        """
        if not daily_data:
            return self._empty_figure("No data available")

        df = pd.DataFrame(daily_data)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['count'],
            mode='lines+markers',
            line=dict(color=self.color_scheme['primary'], width=2),
            marker=dict(size=6, color=self.color_scheme['secondary']),
            fill='tozeroy',
            fillcolor=f"rgba(102, 126, 234, 0.1)",
            name='Messages'
        ))

        fig.update_layout(
            title="Daily Activity (Last 30 Days)",
            xaxis_title="Date",
            yaxis_title="Messages",
            hovermode='x unified',
            plot_bgcolor='white',
            height=400
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def plot_hourly_activity(self, hourly_data):
        """
        Plot hourly activity distribution

        Args:
            hourly_data (list): List of 24 message counts

        Returns:
            plotly.graph_objects.Figure
        """
        hours = [f"{h:02d}:00" for h in range(24)]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=hours,
            y=hourly_data,
            marker=dict(
                color=hourly_data,
                colorscale='Viridis',
                showscale=False
            ),
            name='Messages'
        ))

        fig.update_layout(
            title="Hourly Activity Distribution",
            xaxis_title="Hour",
            yaxis_title="Messages",
            plot_bgcolor='white',
            height=400
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def plot_weekday_activity(self, weekday_data):
        """
        Plot weekday activity distribution

        Args:
            weekday_data (list): List of 7 message counts (Sunday-Saturday)

        Returns:
            plotly.graph_objects.Figure
        """
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=days,
            y=weekday_data,
            marker=dict(
                color=weekday_data,
                colorscale='Purples',
                showscale=False
            ),
            name='Messages'
        ))

        fig.update_layout(
            title="Weekday Activity",
            xaxis_title="Day",
            yaxis_title="Messages",
            plot_bgcolor='white',
            height=400
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def plot_user_radar(self, users_data):
        """
        Plot radar chart comparing users

        Args:
            users_data (dict): User statistics

        Returns:
            plotly.graph_objects.Figure
        """
        if not users_data:
            return self._empty_figure("No user data available")

        fig = go.Figure()

        categories = ['Messages', 'Words', 'Emojis', 'Media', 'Questions']

        for username, stats in users_data.items():
            # Normalize values to 0-100 scale for better comparison
            max_messages = max(u['message_count'] for u in users_data.values())
            max_words = max(u['word_count'] for u in users_data.values())
            max_emojis = max(u['emoji_count'] for u in users_data.values())
            max_media = max(u['media_count'] for u in users_data.values()) or 1
            max_questions = max(u['question_count'] for u in users_data.values()) or 1

            values = [
                (stats['message_count'] / max_messages * 100) if max_messages > 0 else 0,
                (stats['word_count'] / max_words * 100) if max_words > 0 else 0,
                (stats['emoji_count'] / max_emojis * 100) if max_emojis > 0 else 0,
                (stats['media_count'] / max_media * 100) if max_media > 0 else 0,
                (stats['question_count'] / max_questions * 100) if max_questions > 0 else 0,
            ]

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=username
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title="User Comparison",
            height=500
        )

        return fig

    def plot_sentiment(self, users_data):
        """
        Plot sentiment analysis

        Args:
            users_data (dict): User statistics

        Returns:
            plotly.graph_objects.Figure
        """
        if not users_data:
            return self._empty_figure("No sentiment data available")

        usernames = list(users_data.keys())
        sentiments = [stats['sentiment_score'] for stats in users_data.values()]

        # Color based on sentiment
        colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiments]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=usernames,
            y=sentiments,
            marker=dict(color=colors),
            text=sentiments,
            textposition='auto',
            name='Sentiment Score'
        ))

        fig.update_layout(
            title="Sentiment Analysis by User",
            xaxis_title="User",
            yaxis_title="Sentiment Score",
            plot_bgcolor='white',
            height=400
        )

        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def plot_message_distribution(self, users_data):
        """
        Plot message distribution pie chart

        Args:
            users_data (dict): User statistics

        Returns:
            plotly.graph_objects.Figure
        """
        if not users_data:
            return self._empty_figure("No user data available")

        usernames = list(users_data.keys())
        message_counts = [stats['message_count'] for stats in users_data.values()]

        fig = go.Figure(data=[go.Pie(
            labels=usernames,
            values=message_counts,
            hole=0.3,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])

        fig.update_layout(
            title="Message Distribution",
            height=400
        )

        return fig

    def plot_emoji_timeline(self, emoji_data):
        """
        Plot emoji usage over time

        Args:
            emoji_data (list): Emoji usage data

        Returns:
            plotly.graph_objects.Figure
        """
        if not emoji_data:
            return self._empty_figure("No emoji data available")

        # This is a placeholder - would need time-series emoji data
        return self._empty_figure("Emoji timeline visualization")

    def _empty_figure(self, message):
        """Create an empty figure with a message"""
        fig = go.Figure()

        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )

        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='white',
            height=400
        )

        return fig
