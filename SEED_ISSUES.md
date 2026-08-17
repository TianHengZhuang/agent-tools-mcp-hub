# 🎯 30 Seed Issues Ready for GitHub

To get 20 unique external contributors fast, create these issues on your GitHub repository.
Label each with: `good first issue`, `help wanted`, `hacktoberfest-friendly`.

---

### 🌐 Category 1: Search & Web Tools
1. **`[Feature]: Add Open-Meteo Weather Tool (Python)`**
   - *Description*: Add a zero-auth weather tool querying current weather and 7-day forecast using Open-Meteo API.
2. **`[Feature]: Add Wikipedia Summary Fetcher (Python)`**
   - *Description*: Tool to search Wikipedia and return summary paragraphs and links for agent knowledge retrieval.
3. **`[Feature]: Add HackerNews Top Stories Tool (TypeScript)`**
   - *Description*: Fetch top/trending stories from Hacker News Firebase API with points and comments count.
4. **`[Feature]: Add ArXiv Paper Search Tool (Python)`**
   - *Description*: Query arXiv API by query/topic and return title, authors, abstract, and PDF link.
5. **`[Feature]: Add RSS/Atom Feed Reader Tool (Python)`**
   - *Description*: Parse any given RSS feed URL and return the latest 5 articles.

---

### 💻 Category 2: Developer & Productivity Tools
6. **`[Feature]: Add GitHub Repository Stargazer & Stats Tool (TypeScript)`**
   - *Description*: Fetch repository stargazers, fork count, and latest release information.
7. **`[Feature]: Add Notion Page Creator Tool (Python)`**
   - *Description*: Create a new page or append bullet items in a Notion database using Notion API.
8. **`[Feature]: Add Linear Issue Creator Tool (TypeScript)`**
   - *Description*: Create or update issues in Linear workspace using Linear GraphQL API.
9. **`[Feature]: Add Jira Ticket Fetcher (Python)`**
   - *Description*: Fetch ticket status and description from Jira REST API.
10. **`[Feature]: Add Trello Card Creator (Python)`**
    - *Description*: Add task cards to specified Trello lists.
11. **`[Feature]: Add Docker Container Status Checker (Python)`**
    - *Description*: Tool that queries local Docker daemon to report running container stats.

---

### 🗄️ Category 3: Database & Storage Tools
12. **`[Feature]: Add SQLite Query Runner (Python)`**
    - *Description*: Safely execute read-only SELECT queries on a local SQLite database file and return rows.
13. **`[Feature]: Add Supabase Table Query Tool (TypeScript)`**
    - *Description*: Query rows from a Supabase Postgres table using `@supabase/supabase-js`.
14. **`[Feature]: Add Redis Key-Value Store Tool (Python)`**
    - *Description*: Set and get cached values from a Redis instance.
15. **`[Feature]: Add ChromaDB / Vector Store Query Tool (Python)`**
    - *Description*: Query a local Chroma vector database for semantic similarity matches.
16. **`[Feature]: Add Airtable Record Appender (Python)`**
    - *Description*: Append records to an Airtable base via Airtable REST API.

---

### 💬 Category 4: Communication & Social
17. **`[Feature]: Add Telegram Bot Message Sender (Python)`**
    - *Description*: Send agent alert messages to a Telegram chat ID via Telegram Bot API.
18. **`[Feature]: Add Discord Webhook Announcer (TypeScript)`**
    - *Description*: Send rich Discord embeds and notifications via webhook URL.
19. **`[Feature]: Add SendGrid / SMTP Email Dispatcher (Python)`**
    - *Description*: Send plain-text or HTML emails to recipients.
20. **`[Feature]: Add Twilio SMS Alert Tool (Python)`**
    - *Description*: Trigger an SMS alert for critical agent notifications.
21. **`[Feature]: Add Twitter/X Post Creator (TypeScript)`**
    - *Description*: Post automated status tweets using Twitter API v2.

---

### 📊 Category 5: Finance & Data Utilities
22. **`[Feature]: Add CoinGecko Crypto Price Checker (Python)`**
    - *Description*: Fetch live crypto token prices (BTC, ETH, SOL) using free CoinGecko public API.
23. **`[Feature]: Add Exchange Rate / Currency Converter (Python)`**
    - *Description*: Fetch currency conversion rates using open exchange rates.
24. **`[Feature]: Add Yahoo Finance Stock Quote Tool (Python)`**
    - *Description*: Fetch real-time market data for stock tickers using `yfinance`.
25. **`[Feature]: Add Stripe Invoice Fetcher (TypeScript)`**
    - *Description*: Retrieve customer invoices and payment statuses via Stripe SDK.

---

### 🛠️ Category 6: Utilities & Documentation
26. **`[Docs]: Add LangChain Tool Wrapper Example`**
    - *Description*: Add an example in `examples/` showing how to wrap any tool from this repo into a LangChain StructuredTool.
27. **`[Docs]: Add CrewAI Custom Tool Integration Guide`**
    - *Description*: Add a step-by-step example on connecting these tools into CrewAI agents.
28. **`[Feature]: Add PDF Text Extractor Tool (Python)`**
    - *Description*: Extract plain text from local PDF files using `pypdf`.
29. **`[Feature]: Add QR Code Generator Tool (Python)`**
    - *Description*: Generate QR code images for URLs or strings.
30. **`[Feature]: Add Base64 / JWT Decoder Tool (TypeScript)`**
    - *Description*: Decode JWT tokens and inspect headers and payload.

---

## ⚡ Quick Auto-Creation Script (Using GitHub CLI)
If you have `gh` CLI installed, you can create all these issues automatically by running:
```bash
python scripts/create_github_issues.py
```
