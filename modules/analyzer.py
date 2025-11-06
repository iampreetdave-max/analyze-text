"""
WhatsApp Chat Analyzer Module
Analyzes parsed chat data and generates insights
"""

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import pandas as pd


class ChatAnalyzer:
    """Analyzer for WhatsApp chat data"""

    def __init__(self):
        # Emoji pattern for detection
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FAFF"  # extended symbols
            "]+", flags=re.UNICODE
        )

        # URL pattern for link detection
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )

        # Positive and negative keywords for sentiment analysis
        self.positive_words = {
            'love', 'great', 'good', 'awesome', 'amazing', 'wonderful', 'excellent',
            'happy', 'thanks', 'thank', 'best', 'perfect', 'nice', 'beautiful',
            'fantastic', 'cool', 'yes', 'lol', 'haha', 'congratulations', 'congrats'
        }
        self.negative_words = {
            'hate', 'bad', 'terrible', 'awful', 'horrible', 'worst', 'sad',
            'angry', 'no', 'never', 'sorry', 'problem', 'issue', 'wrong',
            'error', 'sucks', 'difficult', 'hard', 'pain', 'annoying'
        }

    def analyze(self, messages_df):
        """
        Perform comprehensive analysis on chat data

        Args:
            messages_df (pd.DataFrame): Parsed messages

        Returns:
            dict: Analysis results
        """
        if messages_df.empty:
            return self._empty_analysis()

        analysis = {
            'total_messages': len(messages_df),
            'users': self._analyze_users(messages_df),
            'top_emojis': self._analyze_emojis(messages_df),
            'hourly_activity': self._analyze_hourly_activity(messages_df),
            'weekday_activity': self._analyze_weekday_activity(messages_df),
            'daily_activity': self._analyze_daily_activity(messages_df),
            'media_count': self._count_media(messages_df),
            'total_words': self._count_total_words(messages_df),
            'deleted_messages': self._count_deleted(messages_df),
            'link_count': self._count_links(messages_df),
        }

        return analysis

    def _empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'total_messages': 0,
            'users': {},
            'top_emojis': [],
            'hourly_activity': [0] * 24,
            'weekday_activity': [0] * 7,
            'daily_activity': [],
            'media_count': 0,
            'total_words': 0,
            'deleted_messages': 0,
            'link_count': 0,
        }

    def _analyze_users(self, df):
        """Analyze per-user statistics"""
        users = {}

        for username in df['user'].unique():
            user_messages = df[df['user'] == username]
            users[username] = self._analyze_single_user(user_messages, df)

        return users

    def _analyze_single_user(self, user_df, all_df):
        """Analyze statistics for a single user"""
        messages = user_df['message'].tolist()
        message_count = len(messages)

        # Word count
        words = ' '.join(messages).split()
        word_count = len(words)
        avg_message_length = word_count / message_count if message_count > 0 else 0

        # Emoji analysis
        emojis = self._extract_emojis(messages)
        emoji_count = sum(emojis.values())

        # Media count
        media_count = sum(1 for msg in messages if self._is_media(msg))

        # Question count
        question_count = sum(1 for msg in messages if '?' in msg)

        # Link count
        link_count = sum(1 for msg in messages if self.url_pattern.search(str(msg)))

        # Sentiment analysis
        sentiment_score = self._calculate_sentiment(messages)

        # Time-based analysis
        night_owl_score = sum(1 for ts in user_df['timestamp']
                              if ts.hour >= 22 or ts.hour < 4)
        morning_score = sum(1 for ts in user_df['timestamp']
                           if 5 <= ts.hour < 9)

        # Conversation starters (messages after long gaps)
        conversation_starters = self._count_conversation_starters(user_df, all_df)

        # Average response time
        avg_response_time = self._calculate_avg_response_time(user_df, all_df)

        # Best lines (quality messages)
        best_lines = self._find_best_lines(user_df)

        return {
            'message_count': message_count,
            'word_count': word_count,
            'avg_message_length': avg_message_length,
            'emojis': emojis,
            'emoji_count': emoji_count,
            'media_count': media_count,
            'question_count': question_count,
            'link_count': link_count,
            'sentiment_score': sentiment_score,
            'night_owl_score': night_owl_score,
            'morning_score': morning_score,
            'conversation_starters': conversation_starters,
            'avg_response_time': avg_response_time,
            'best_lines': best_lines,
        }

    def _extract_emojis(self, messages):
        """Extract and count emojis from messages"""
        emoji_counter = Counter()

        for message in messages:
            emojis = self.emoji_pattern.findall(message)
            for emoji in emojis:
                for char in emoji:
                    emoji_counter[char] += 1

        return dict(emoji_counter)

    def _analyze_emojis(self, df):
        """Get top emojis across all messages"""
        all_emojis = Counter()

        for message in df['message']:
            emojis = self.emoji_pattern.findall(str(message))
            for emoji in emojis:
                for char in emoji:
                    all_emojis[char] += 1

        return all_emojis.most_common(50)

    def _analyze_hourly_activity(self, df):
        """Analyze activity by hour of day"""
        hourly = [0] * 24
        for hour in df['timestamp'].dt.hour:
            hourly[hour] += 1
        return hourly

    def _analyze_weekday_activity(self, df):
        """Analyze activity by day of week (0=Sunday, 6=Saturday)"""
        weekday = [0] * 7
        for day in df['timestamp'].dt.dayofweek:
            # Convert pandas dayofweek (0=Monday) to our format (0=Sunday)
            weekday[(day + 1) % 7] += 1
        return weekday

    def _analyze_daily_activity(self, df):
        """Analyze activity for last 30 days"""
        if df.empty:
            return []

        # Get last 30 days
        end_date = df['timestamp'].max()
        start_date = end_date - timedelta(days=29)

        # Filter messages in last 30 days
        recent_df = df[df['timestamp'] >= start_date]

        # Count messages per day
        daily_counts = recent_df.groupby(recent_df['timestamp'].dt.date).size()

        # Create complete range of dates
        date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
        result = []

        for date in date_range:
            count = daily_counts.get(date.date(), 0)
            result.append({'date': date.strftime('%Y-%m-%d'), 'count': int(count)})

        return result

    def _count_media(self, df):
        """Count media messages"""
        return sum(1 for msg in df['message'] if self._is_media(msg))

    def _is_media(self, message):
        """Check if message is media"""
        media_patterns = [
            '<Media omitted>',
            'image omitted',
            'video omitted',
            'audio omitted',
            'document omitted',
            'sticker omitted',
            'GIF omitted',
        ]
        message_lower = str(message).lower()
        return any(pattern.lower() in message_lower for pattern in media_patterns)

    def _count_total_words(self, df):
        """Count total words across all messages"""
        all_text = ' '.join(df['message'].astype(str))
        return len(all_text.split())

    def _count_deleted(self, df):
        """Count deleted messages"""
        deleted_patterns = ['deleted', 'this message was deleted']
        return sum(1 for msg in df['message']
                  if any(pattern in str(msg).lower() for pattern in deleted_patterns))

    def _count_links(self, df):
        """Count messages containing links/URLs"""
        return sum(1 for msg in df['message'] if self.url_pattern.search(str(msg)))

    def _calculate_sentiment(self, messages):
        """Calculate sentiment score for messages"""
        positive_count = 0
        negative_count = 0

        for message in messages:
            words = str(message).lower().split()
            positive_count += sum(1 for word in words if word in self.positive_words)
            negative_count += sum(1 for word in words if word in self.negative_words)

        return positive_count - negative_count

    def _count_conversation_starters(self, user_df, all_df):
        """Count how many times user started a conversation"""
        # A conversation starter is a message after a gap of 2+ hours
        count = 0
        sorted_df = all_df.sort_values('timestamp')

        for idx, row in user_df.iterrows():
            # Find previous message in overall chat
            prev_messages = sorted_df[sorted_df['timestamp'] < row['timestamp']]
            if not prev_messages.empty:
                prev_time = prev_messages.iloc[-1]['timestamp']
                time_diff = (row['timestamp'] - prev_time).total_seconds() / 3600
                if time_diff >= 2:
                    count += 1
            else:
                count += 1  # First message overall

        return count

    def _calculate_avg_response_time(self, user_df, all_df):
        """Calculate average response time in minutes"""
        if len(all_df) < 2:
            return None

        response_times = []
        sorted_df = all_df.sort_values('timestamp')

        for idx, row in user_df.iterrows():
            # Find previous message from different user
            prev_messages = sorted_df[
                (sorted_df['timestamp'] < row['timestamp']) &
                (sorted_df['user'] != row['user'])
            ]

            if not prev_messages.empty:
                prev_time = prev_messages.iloc[-1]['timestamp']
                time_diff = (row['timestamp'] - prev_time).total_seconds() / 60
                if time_diff < 60:  # Only count if response within 1 hour
                    response_times.append(time_diff)

        return sum(response_times) / len(response_times) if response_times else None

    def _find_best_lines(self, user_df, top_n=5):
        """Find best/quality messages based on length, emojis, and engagement"""
        scored_messages = []

        for idx, row in user_df.iterrows():
            message = str(row['message'])

            # Skip media and system messages
            if self._is_media(message) or len(message) < 10:
                continue

            # Calculate quality score
            score = 0

            # Length score (optimal length 20-100 chars)
            length = len(message)
            if 20 <= length <= 100:
                score += 3
            elif length > 100:
                score += 2
            else:
                score += 1

            # Emoji score (1-3 emojis is good)
            emoji_count = len(self.emoji_pattern.findall(message))
            if 1 <= emoji_count <= 3:
                score += 2

            # Question or statement
            if '?' in message or '!' in message:
                score += 1

            # Positive sentiment
            words = message.lower().split()
            if any(word in self.positive_words for word in words):
                score += 2

            scored_messages.append({
                'message': message,
                'timestamp': row['timestamp'],
                'score': score
            })

        # Sort by score and return top N
        scored_messages.sort(key=lambda x: x['score'], reverse=True)
        return scored_messages[:top_n]
