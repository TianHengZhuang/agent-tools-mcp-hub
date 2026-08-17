# 🤝 Contributing to Agent Tools & MCP Hub

First off, thank you for considering contributing to the Agent Tools Hub! 🎉

We designed this repository so that **anyone can contribute in 15–20 minutes** without dealing with complex setups or merge conflicts.

---

## ⚡ Quick Contribution Flow

### Step 1: Fork & Clone
1. Fork this repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/agent-tools-mcp-hub.git
   cd agent-tools-mcp-hub
   git checkout -b feat/add-<tool-name>
   ```

### Step 2: Create Your Tool Directory
Every tool lives in its own standalone directory inside `tools/`.

1. Copy the template folder:
   ```bash
   cp -r tools/_template tools/<your_tool_name>
   ```
2. Make sure your tool name is in `snake_case` or `kebab-case` (e.g., `tools/weather_open_meteo` or `tools/notion_page_creator`).

### Step 3: Implement Your Tool
Your folder should contain:
- `tool.py` (or `tool.ts` / `index.ts` / `main.go`) - The core tool implementation.
- `metadata.json` - Metadata describing the tool, inputs, author, and category.
- `README.md` - A brief description with setup and usage examples.
- `requirements.txt` or `package.json` - Any required dependencies.

### Step 4: Validate Your Tool
Run the built-in validation script to verify schema formatting and folder structure:
```bash
python scripts/validate_tools.py
```

### Step 5: Submit a Pull Request
1. Commit your changes:
   ```bash
   git add tools/<your_tool_name>
   git commit -m "feat(tool): add <your_tool_name> integration"
   ```
2. Push to your fork:
   ```bash
   git push origin feat/add-<tool-name>
   ```
3. Open a **Pull Request (PR)** against the `main` branch.
4. Fill out the PR template checklist.

---

## 📋 Tool Quality Guidelines

- **Simplicity**: Tools should do one task well (e.g. "Fetch Weather", "Send Telegram Message", "Query SQLite DB").
- **Error Handling**: Catch API/network errors gracefully and return descriptive error messages.
- **Environment Variables**: Use `.env` or environment variables for API keys/secrets; **NEVER hardcode secrets**.
- **Documentation**: Provide at least 1 working code snippet in your tool's `README.md`.

---

## 💡 Types of Contributions Welcome

- 🧩 **New Agent Tools**: Add integrations for popular APIs (Stripe, Spotify, Notion, Jira, Linear, Supabase, Airtable, etc.).
- 🔌 **MCP Server Adapters**: Turn tools into official Model Context Protocol (MCP) server endpoints.
- 📖 **Documentation & Guides**: Improve setup guides, translate READMEs, or add agent framework examples (CrewAI, LangChain, AutoGen).
- 🧪 **Tests & CI**: Add automated test cases or linting actions.

---

## 🏅 Contributor Recognition

All contributors will be added to the official **Contributors** section on our main `README.md` using the [All Contributors](https://allcontributors.org) bot!
