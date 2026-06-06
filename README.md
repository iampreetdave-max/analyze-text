# ChatLyze — WhatsApp Chat Analyzer

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

> A Streamlit web app that turns an exported WhatsApp chat into rich analytics, visualizations, and downloadable reports — entirely on your own machine.

## Overview

ChatLyze parses a WhatsApp chat export (`.txt`) and produces per-user and per-group statistics, activity patterns, sentiment scores, and "champion" leaderboards. All processing happens locally in the Streamlit session; the chat content is never sent to an external server. The app is organized as a thin UI layer (`app.py`) over four focused modules that handle parsing, analysis, visualization, and report export.

## Key Features

- **Multi-format parsing** — supports several WhatsApp export timestamp formats (bracketed and dashed, 12/24-hour, with or without seconds).
- **Message statistics** — total messages, words, media count, and per-user breakdowns.
- **User analytics** — message count, word count, average message length, emoji count, questions, links, and sentiment score per participant.
- **Activity patterns** — daily timeline (last 30 days), hourly distribution, and weekday activity.
- **Sentiment analysis** — per-user sentiment scoring surfaced in charts and metrics.
- **Insights** — fastest responders, conversation starters, peak activity hours, and most-used emojis.
- **Best lines** — highest-scored messages per user.
- **Champions** — leaderboards across categories such as Message Champion, Word Master, Emoji King/Queen, Night Owl, Early Bird, and more.
- **Exports** — download results as JSON, CSV, or a generated PDF report.

## How It Works

```
chat.txt ── ChatParser ──► messages DataFrame ── ChatAnalyzer ──► analysis dict
                                                                       │
                                          ┌────────────────────────────┼──────────────────────┐
                                          ▼                            ▼                      ▼
                                     Visualizer                 Streamlit UI           ReportGenerator
                                   (Plotly charts)          (tabs, metrics)        (JSON / CSV / PDF)
```

1. `ChatParser` reads the raw export, matches each line against known timestamp patterns, and returns a pandas DataFrame of `timestamp`, `user`, and `message`.
2. `ChatAnalyzer` computes aggregate and per-user statistics from that DataFrame.
3. `Visualizer` renders Plotly charts; `app.py` lays them out across Overview, Users, Insights, Best Lines, and Champions tabs.
4. `ReportGenerator` serializes the analysis to JSON, CSV, or PDF for download.

## Tech Stack

- **Language:** Python 3
- **UI:** Streamlit
- **Data:** pandas, numpy
- **Charts:** Plotly
- **PDF export:** ReportLab
- **Spreadsheet support:** openpyxl

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
git clone https://github.com/iampreetdave-max/analyze-text.git
cd analyze-text
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints, upload a WhatsApp chat export (exported **without media** as a `.txt` file), and click **Analyze Chat**.

## Project Structure

```
analyze-text/
├── app.py                       # Streamlit UI and tab layout
├── modules/
│   ├── __init__.py
│   ├── parser.py                # ChatParser — export parsing
│   ├── analyzer.py              # ChatAnalyzer — statistics & sentiment
│   ├── visualizer.py            # Visualizer — Plotly charts
│   └── report_generator.py      # ReportGenerator — JSON/CSV/PDF export
├── requirements.txt
└── README.md
```

## Privacy

All parsing and analysis run locally within the Streamlit process. No chat data is transmitted to any external service.
