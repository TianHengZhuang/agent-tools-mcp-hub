#!/usr/bin/env python3
"""
Automates creating 30 'good first issue' tasks on your GitHub repository using GitHub CLI (`gh`).
Usage:
    gh auth login
    python scripts/create_github_issues.py
"""
import subprocess
import sys

ISSUES = [
    ("Add Open-Meteo Weather Tool (Python)", "Add a zero-auth weather tool querying current weather and 7-day forecast using Open-Meteo API.", "Search & Web"),
    ("Add Wikipedia Summary Fetcher (Python)", "Tool to search Wikipedia and return summary paragraphs and links for agent knowledge retrieval.", "Search & Web"),
    ("Add HackerNews Top Stories Tool (TypeScript)", "Fetch top/trending stories from Hacker News Firebase API with points and comments count.", "Search & Web"),
    ("Add ArXiv Paper Search Tool (Python)", "Query arXiv API by query/topic and return title, authors, abstract, and PDF link.", "Search & Web"),
    ("Add RSS/Atom Feed Reader Tool (Python)", "Parse any given RSS feed URL and return the latest 5 articles.", "Search & Web"),
    ("Add GitHub Repository Stats Tool (TypeScript)", "Fetch repository stargazers, fork count, and latest release information.", "Developer Tools"),
    ("Add Notion Page Creator Tool (Python)", "Create a new page or append bullet items in a Notion database using Notion API.", "Developer Tools"),
    ("Add Linear Issue Creator Tool (TypeScript)", "Create or update issues in Linear workspace using Linear GraphQL API.", "Developer Tools"),
    ("Add Jira Ticket Fetcher (Python)", "Fetch ticket status and description from Jira REST API.", "Developer Tools"),
    ("Add Trello Card Creator (Python)", "Add task cards to specified Trello lists.", "Developer Tools"),
    ("Add SQLite Query Runner (Python)", "Safely execute read-only SELECT queries on a local SQLite database file and return rows.", "Database"),
    ("Add Supabase Table Query Tool (TypeScript)", "Query rows from a Supabase Postgres table using @supabase/supabase-js.", "Database"),
    ("Add Redis Key-Value Store Tool (Python)", "Set and get cached values from a Redis instance.", "Database"),
    ("Add ChromaDB Vector Store Query Tool (Python)", "Query a local Chroma vector database for semantic similarity matches.", "Database"),
    ("Add Airtable Record Appender (Python)", "Append records to an Airtable base via Airtable REST API.", "Database"),
    ("Add Telegram Bot Message Sender (Python)", "Send agent alert messages to a Telegram chat ID via Telegram Bot API.", "Communication"),
    ("Add Discord Webhook Announcer (TypeScript)", "Send rich Discord embeds and notifications via webhook URL.", "Communication"),
    ("Add SendGrid Email Dispatcher (Python)", "Send plain-text or HTML emails to recipients via SendGrid API.", "Communication"),
    ("Add Twilio SMS Alert Tool (Python)", "Trigger an SMS alert for critical agent notifications.", "Communication"),
    ("Add Twitter/X Post Creator (TypeScript)", "Post automated status tweets using Twitter API v2.", "Communication"),
    ("Add CoinGecko Crypto Price Checker (Python)", "Fetch live crypto token prices (BTC, ETH, SOL) using free CoinGecko public API.", "Finance"),
    ("Add Currency Exchange Rate Converter (Python)", "Fetch currency conversion rates using open exchange rates.", "Finance"),
    ("Add Yahoo Finance Stock Quote Tool (Python)", "Fetch real-time market data for stock tickers using yfinance.", "Finance"),
    ("Add Stripe Invoice Fetcher (TypeScript)", "Retrieve customer invoices and payment statuses via Stripe SDK.", "Finance"),
    ("Add LangChain Tool Wrapper Example (Docs)", "Add an example in examples/ showing how to wrap any tool from this repo into a LangChain StructuredTool.", "Documentation"),
    ("Add CrewAI Custom Tool Integration Guide (Docs)", "Add a step-by-step example on connecting these tools into CrewAI agents.", "Documentation"),
    ("Add PDF Text Extractor Tool (Python)", "Extract plain text from local PDF files using pypdf.", "Utilities"),
    ("Add QR Code Generator Tool (Python)", "Generate QR code images for URLs or strings.", "Utilities"),
    ("Add Base64 / JWT Decoder Tool (TypeScript)", "Decode JWT tokens and inspect headers and payload.", "Utilities"),
    ("Add Docker Container Status Checker (Python)", "Query local Docker daemon to report running container stats.", "Developer Tools"),
]

def check_gh_installed():
    try:
        subprocess.run(["gh", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False

def create_issues():
    if not check_gh_installed():
        print("❌ GitHub CLI (`gh`) is not installed. Please install it (`brew install gh`) and run `gh auth login` first.")
        sys.exit(1)

    print(f"🚀 Creating {len(ISSUES)} issues on current GitHub repository...\n")
    
    for idx, (title, desc, cat) in enumerate(ISSUES, 1):
        full_title = f"[Feature]: {title}"
        body = f"""### 📌 Description\n{desc}\n\n### 🏷️ Category\n{cat}\n\n### 🤝 How to contribute\n1. Fork the repo\n2. Copy `tools/_template/` into `tools/<your_tool_name>/`\n3. Implement the tool and run `python scripts/validate_tools.py`\n4. Submit a Pull Request!\n\n*Comment below to get assigned to this issue!*"""
        
        cmd = [
            "gh", "issue", "create",
            "--title", full_title,
            "--body", body,
            "--label", "good first issue,help wanted,enhancement"
        ]
        
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                print(f"[{idx}/{len(ISSUES)}] ✅ Created: {full_title} -> {res.stdout.strip()}")
            else:
                print(f"[{idx}/{len(ISSUES)}] ⚠️ Error: {res.stderr.strip()}")
        except Exception as e:
            print(f"Error executing gh: {e}")

if __name__ == "__main__":
    create_issues()
