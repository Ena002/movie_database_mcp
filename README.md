# Movie Database MCP (SQLite)

Relational (SQLite) MCP server for managing a movie collection.

## Requirements satisfied (per assignment)
- ✅ 3+ MCP tools (CRUD + search)
- ✅ 1 MCP resource: `collection://stats`
- ✅ External integration: SQLite (`movies.db`) with PK/FK relational model
- ✅ Ready for Claude Desktop integration

## Relational model
- `genres(id PK, name UNIQUE)`
- `movies(id PK, title, director, year, rating, genre_id FK -> genres.id, created_at)`

## Run (macOS)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python movie-mcp.py
```

## Claude Desktop config (example)
Set `command` to your venv python path.

```json
{
  "mcpServers": {
    "Movie Database": {
      "command": "/ABS/PATH/movie-database-mcp-sqlite/venv/bin/python",
      "args": ["movie-mcp.py"],
      "cwd": "/ABS/PATH/movie-database-mcp-sqlite"
    }
  }
}
```
