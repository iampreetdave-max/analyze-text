"""
WhatsApp Chat Parser Module
Parses WhatsApp chat export files into structured data
"""

import re
from datetime import datetime
import pandas as pd


class ChatParser:
    """Parser for WhatsApp chat export files"""

    def __init__(self):
        # Multiple date patterns to support different WhatsApp export formats
        self.patterns = [
            # Pattern 1: [DD/MM/YY, HH:MM:SS] Name: Message
            r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)',
            # Pattern 2: DD/MM/YYYY, HH:MM - Name: Message
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)',
            # Pattern 3: [DD/MM/YYYY HH:MM:SS] Name: Message
            r'\[(\d{1,2}/\d{1,2}/\d{2,4})\s(\d{1,2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)',
            # Pattern 4: DD/MM/YY, HH:MM AM/PM - Name: Message
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)',
        ]

    def parse(self, content):
        """
        Parse WhatsApp chat content into a pandas DataFrame

        Args:
            content (str): Raw chat export content

        Returns:
            pd.DataFrame: Parsed messages with columns: timestamp, user, message
        """
        messages = []
        lines = content.split('\n')

        for line in lines:
            if not line.strip():
                continue

            parsed = self._parse_line(line)
            if parsed:
                messages.append(parsed)

        if not messages:
            return pd.DataFrame(columns=['timestamp', 'user', 'message'])

        df = pd.DataFrame(messages)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def _parse_line(self, line):
        """
        Parse a single line of chat

        Args:
            line (str): Single line from chat export

        Returns:
            dict: Parsed message data or None if parsing fails
        """
        for pattern in self.patterns:
            match = re.match(pattern, line)
            if match:
                date_str, time_str, user, message = match.groups()

                # Combine date and time
                timestamp = self._parse_timestamp(date_str, time_str)

                if timestamp:
                    return {
                        'timestamp': timestamp,
                        'user': user.strip(),
                        'message': message.strip()
                    }

        return None

    def _parse_timestamp(self, date_str, time_str):
        """
        Parse date and time strings into datetime object

        Args:
            date_str (str): Date string
            time_str (str): Time string

        Returns:
            datetime: Parsed timestamp or None if parsing fails
        """
        # Try different date/time format combinations
        formats = [
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%y %H:%M',
            '%d/%m/%Y %I:%M %p',
            '%d/%m/%y %I:%M %p',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%y %H:%M',
        ]

        datetime_str = f"{date_str} {time_str}"

        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue

        return None
