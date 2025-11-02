"""
WhatsApp Chat Parser Module
Handles parsing of WhatsApp chat export files in various formats
"""

import re
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

class ChatParser:
    """Parse WhatsApp chat export files"""
    
    # Multiple date/time patterns to support different WhatsApp formats
    PATTERNS = [
        # Pattern 1: DD/MM/YYYY, HH:MM - Author: Message
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\s*-\s*([^:]+):\s*(.*)$',
        
        # Pattern 2: [DD/MM/YYYY, HH:MM:SS] Author: Message
        r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\]\s*([^:]+):\s*(.*)$',
        
        # Pattern 3: DD/MM/YY, HH:MM - Author: Message (no AM/PM)
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.*)$',
        
        # Pattern 4: MM/DD/YY, HH:MM AM/PM - Author: Message (US format)
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))\s*-\s*([^:]+):\s*(.*)$',
        
        # Pattern 5: DD.MM.YY, HH:MM - Author: Message (European format)
        r'^(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s+(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.*)$',
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern) for pattern in self.PATTERNS]
    
    def parse(self, content: str) -> pd.DataFrame:
        """
        Parse WhatsApp chat content and return DataFrame
        
        Args:
            content: String content of WhatsApp chat export
            
        Returns:
            DataFrame with columns: timestamp, author, message
        """
        lines = content.split('\n')
        messages = []
        current_message = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to match with any pattern
            matched = False
            for pattern in self.compiled_patterns:
                match = pattern.match(line)
                if match:
                    # Save previous message if exists
                    if current_message:
                        messages.append(current_message)
                    
                    date_str, time_str, author, message = match.groups()
                    
                    # Parse timestamp
                    timestamp = self._parse_timestamp(date_str, time_str)
                    
                    current_message = {
                        'timestamp': timestamp,
                        'author': author.strip(),
                        'message': message.strip()
                    }
                    matched = True
                    break
            
            # If not matched and we have a current message, it's a continuation
            if not matched and current_message:
                current_message['message'] += '\n' + line
        
        # Don't forget the last message
        if current_message:
            messages.append(current_message)
        
        # Create DataFrame
        df = pd.DataFrame(messages)
        
        # Sort by timestamp
        if not df.empty:
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def _parse_timestamp(self, date_str: str, time_str: str) -> datetime:
        """
        Parse date and time strings into datetime object
        
        Args:
            date_str: Date string (e.g., "12/31/2023" or "31.12.2023")
            time_str: Time string (e.g., "14:30" or "2:30 PM")
            
        Returns:
            datetime object
        """
        # Normalize date separator to /
        date_str = date_str.replace('.', '/')
        
        # Parse date parts
        date_parts = date_str.split('/')
        
        # Determine date format (DD/MM/YYYY vs MM/DD/YYYY)
        # Heuristic: if first part > 12, it's DD/MM/YYYY
        if int(date_parts[0]) > 12:
            day, month, year = date_parts
        elif int(date_parts[1]) > 12:
            month, day, year = date_parts
        else:
            # Ambiguous, assume DD/MM/YYYY (common in most countries)
            day, month, year = date_parts
        
        # Handle 2-digit years
        year = int(year)
        if year < 100:
            year += 2000
        
        day = int(day)
        month = int(month)
        
        # Parse time
        time_str = time_str.strip()
        
        # Check for AM/PM
        is_pm = 'pm' in time_str.lower()
        is_am = 'am' in time_str.lower()
        
        # Remove AM/PM
        time_str = re.sub(r'\s*[AaPp][Mm]\s*', '', time_str)
        
        # Parse time parts
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        # Convert to 24-hour format if AM/PM present
        if is_pm and hour != 12:
            hour += 12
        elif is_am and hour == 12:
            hour = 0
        
        try:
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            # Fallback to current time if parsing fails
            return datetime.now()
    
    def get_chat_info(self, df: pd.DataFrame) -> Dict:
        """
        Get basic information about the chat
        
        Args:
            df: DataFrame with parsed messages
            
        Returns:
            Dictionary with chat info
        """
        if df.empty:
            return {}
        
        return {
            'total_messages': len(df),
            'participants': df['author'].nunique(),
            'participant_names': df['author'].unique().tolist(),
            'start_date': df['timestamp'].min(),
            'end_date': df['timestamp'].max(),
            'duration_days': (df['timestamp'].max() - df['timestamp'].min()).days
        }
