"""
WhatsApp Chat Report Generator Module
Generates reports in various formats (JSON, CSV, PDF)
"""

import json
import csv
from io import StringIO, BytesIO
from datetime import datetime


class ReportGenerator:
    """Generator for chat analysis reports"""

    def __init__(self):
        pass

    def generate_json(self, analysis, filename="chat.txt"):
        """
        Generate JSON report

        Args:
            analysis (dict): Analysis results
            filename (str): Original chat filename

        Returns:
            str: JSON string
        """
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source_file': filename,
                'analyzer_version': '1.0.0'
            },
            'summary': {
                'total_messages': analysis['total_messages'],
                'total_users': len(analysis['users']),
                'total_words': analysis['total_words'],
                'media_count': analysis['media_count'],
                'deleted_messages': analysis.get('deleted_messages', 0)
            },
            'users': {}
        }

        # Add user statistics
        for username, stats in analysis['users'].items():
            report['users'][username] = {
                'message_count': stats['message_count'],
                'word_count': stats['word_count'],
                'avg_message_length': round(stats['avg_message_length'], 2),
                'emoji_count': stats['emoji_count'],
                'media_count': stats['media_count'],
                'question_count': stats['question_count'],
                'sentiment_score': stats['sentiment_score'],
                'night_owl_score': stats['night_owl_score'],
                'morning_score': stats['morning_score'],
                'conversation_starters': stats['conversation_starters'],
                'avg_response_time': round(stats['avg_response_time'], 2) if stats['avg_response_time'] else None,
                'top_emojis': dict(list(stats['emojis'].items())[:10]) if stats['emojis'] else {}
            }

        # Add top emojis overall
        report['top_emojis'] = [
            {'emoji': emoji, 'count': count}
            for emoji, count in analysis['top_emojis'][:20]
        ]

        # Add activity patterns
        report['activity_patterns'] = {
            'hourly': analysis['hourly_activity'],
            'weekday': analysis['weekday_activity'],
            'daily': analysis['daily_activity']
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    def generate_csv(self, analysis):
        """
        Generate CSV report with user statistics

        Args:
            analysis (dict): Analysis results

        Returns:
            str: CSV string
        """
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Username',
            'Messages',
            'Words',
            'Avg Message Length',
            'Emojis',
            'Media',
            'Questions',
            'Sentiment Score',
            'Night Owl Score',
            'Morning Score',
            'Conversation Starters',
            'Avg Response Time (min)'
        ])

        # User rows
        for username, stats in sorted(analysis['users'].items(),
                                      key=lambda x: x[1]['message_count'],
                                      reverse=True):
            writer.writerow([
                username,
                stats['message_count'],
                stats['word_count'],
                round(stats['avg_message_length'], 2),
                stats['emoji_count'],
                stats['media_count'],
                stats['question_count'],
                stats['sentiment_score'],
                stats['night_owl_score'],
                stats['morning_score'],
                stats['conversation_starters'],
                round(stats['avg_response_time'], 2) if stats['avg_response_time'] else 'N/A'
            ])

        # Summary section
        writer.writerow([])
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Messages', analysis['total_messages']])
        writer.writerow(['Total Users', len(analysis['users'])])
        writer.writerow(['Total Words', analysis['total_words']])
        writer.writerow(['Media Count', analysis['media_count']])
        writer.writerow(['Deleted Messages', analysis.get('deleted_messages', 0)])

        # Emoji section
        writer.writerow([])
        writer.writerow(['TOP EMOJIS'])
        writer.writerow(['Emoji', 'Count'])
        for emoji, count in analysis['top_emojis'][:20]:
            writer.writerow([emoji, count])

        return output.getvalue()

    def generate_pdf(self, analysis, filename="chat.txt"):
        """
        Generate PDF report

        Args:
            analysis (dict): Analysis results
            filename (str): Original chat filename

        Returns:
            bytes: PDF file content
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            # If reportlab is not installed, return a simple text-based PDF alternative
            return self._generate_text_pdf_fallback(analysis, filename)

        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        # Container for PDF elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12
        )

        # Title
        elements.append(Paragraph("ChatLyze Analysis Report", title_style))
        elements.append(Paragraph(f"<b>Source:</b> {filename}", styles['Normal']))
        elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Summary section
        elements.append(Paragraph("Summary Statistics", heading_style))

        summary_data = [
            ['Metric', 'Value'],
            ['Total Messages', f"{analysis['total_messages']:,}"],
            ['Total Users', str(len(analysis['users']))],
            ['Total Words', f"{analysis['total_words']:,}"],
            ['Media Shared', f"{analysis['media_count']:,}"],
            ['Deleted Messages', f"{analysis.get('deleted_messages', 0):,}"]
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # User statistics
        elements.append(Paragraph("User Statistics", heading_style))

        user_data = [['User', 'Messages', 'Words', 'Emojis', 'Sentiment']]
        for username, stats in sorted(analysis['users'].items(),
                                      key=lambda x: x[1]['message_count'],
                                      reverse=True):
            user_data.append([
                username,
                f"{stats['message_count']:,}",
                f"{stats['word_count']:,}",
                f"{stats['emoji_count']:,}",
                str(stats['sentiment_score'])
            ])

        user_table = Table(user_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        elements.append(user_table)
        elements.append(Spacer(1, 20))

        # Top emojis
        elements.append(Paragraph("Top Emojis", heading_style))

        emoji_data = [['Rank', 'Emoji', 'Count']]
        for idx, (emoji, count) in enumerate(analysis['top_emojis'][:10], 1):
            emoji_data.append([
                str(idx),
                emoji,
                f"{count:,}"
            ])

        emoji_table = Table(emoji_data, colWidths=[1*inch, 2*inch, 2*inch])
        emoji_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(emoji_table)

        # Build PDF
        doc.build(elements)

        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()

        return pdf_content

    def _generate_text_pdf_fallback(self, analysis, filename):
        """
        Fallback for PDF generation when reportlab is not available
        Returns a simple text file formatted as PDF content
        """
        content = f"""
CHATLYZE ANALYSIS REPORT
========================

Source: {filename}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY STATISTICS
------------------
Total Messages: {analysis['total_messages']:,}
Total Users: {len(analysis['users'])}
Total Words: {analysis['total_words']:,}
Media Shared: {analysis['media_count']:,}
Deleted Messages: {analysis.get('deleted_messages', 0):,}

USER STATISTICS
---------------
"""

        for username, stats in sorted(analysis['users'].items(),
                                      key=lambda x: x[1]['message_count'],
                                      reverse=True):
            content += f"""
{username}:
  Messages: {stats['message_count']:,}
  Words: {stats['word_count']:,}
  Avg Length: {stats['avg_message_length']:.1f}
  Emojis: {stats['emoji_count']:,}
  Media: {stats['media_count']:,}
  Sentiment: {stats['sentiment_score']}
"""

        content += "\nTOP EMOJIS\n----------\n"
        for idx, (emoji, count) in enumerate(analysis['top_emojis'][:10], 1):
            content += f"{idx}. {emoji} - {count:,} times\n"

        return content.encode('utf-8')
