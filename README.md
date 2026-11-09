# Reading Log (MCP workshop project)

A personal book-report site powered by an MCP server. Claude searches Open Library
for covers and descriptions, saves books and reviews to `data/library.json`, and the
website shows them in a **Library view** (shelf of covers) and a **Card view**
(description, rating, review).

![Demo](docs/demo.png)

## How the pieces map to MCP
| MCP concept | In this repo |
|---|---|
| Tools | `search_books`, `get_book_details`, `add_to_library`, `save_review` |
| Resources | `library://books`, `library://books/{work_id}` |
| Prompts | `book_report` |

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Try the server in the MCP Inspector
```bash
mcp dev server/server.py
```
Open the printed URL, then call `search_books` with `{"query": "Parable of the Sower"}`.

## 2. Connect it to Claude Desktop
Add this to `claude_desktop_config.json` (use the absolute path to this repo):
```json
{
  "mcpServers": {
    "reading-log": {
      "command": "/ABSOLUTE/PATH/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/reading-log/server/server.py"]
    }
  }
}
```
Restart Claude Desktop, then try: *"Search for Klara and the Sun, add it to my library, then give it 4 stars with a short review."*

## 3. View the site
```bash
python -m http.server 8000
```
Open http://localhost:8000/web/ and refresh after Claude updates your library.

## Workshop exercises
1. Add a `remove_from_library` tool.
2. Add a `reading_stats` resource (books finished, average rating).
3. Add a `recommend_next` prompt that reads `library://books`.
4. Hackathon stretch: swap Open Library for any free API and keep the same tool shape.
