import sqlite3
from datetime import datetime
from fastmcp import FastMCP
import os

DB_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "MovieDatabaseMCP")
os.makedirs(DB_DIR, exist_ok=True)
DB_FILE = os.path.join(DB_DIR, "movies.db")
mcp = FastMCP("Movie Database (SQLite)")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        director TEXT NOT NULL,
        year INTEGER,
        rating REAL,
        genre_id INTEGER,
        created_at TEXT,
        FOREIGN KEY (genre_id) REFERENCES genres(id)
    )
    """)

    for g in ("Drama", "Sci-Fi", "Comedy", "Action"):
        cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (g,))

    cursor.execute("SELECT id FROM genres WHERE name='Drama'")
    drama_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM genres WHERE name='Sci-Fi'")
    scifi_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM genres WHERE name='Action'")
    action_id = cursor.fetchone()[0]

    seed = [
        ("The Shawshank Redemption", "Frank Darabont", 1994, 9.3, drama_id),
        ("Interstellar", "Christopher Nolan", 2014, 8.6, scifi_id),
        ("Inception", "Christopher Nolan", 2010, 8.8, action_id),
        ("The Dark Knight", "Christopher Nolan", 2008, 9.0, action_id),
    ]
    for title, director, year, rating, gid in seed:
        cursor.execute("""
        INSERT OR IGNORE INTO movies (title, director, year, rating, genre_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, director, year, rating, gid, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()

init_db()

@mcp.tool
def add_movie(title: str, director: str, year: int, rating: float, genre: str):
    """Create: Add a new movie (and genre if missing)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (genre,))
    cursor.execute("SELECT id FROM genres WHERE name=?", (genre,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Could not create/find genre")
    genre_id = row[0]

    cursor.execute("""
    INSERT INTO movies (title, director, year, rating, genre_id, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (title, director, year, rating, genre_id, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()
    return {"ok": True, "message": f"Movie '{title}' added successfully."}

@mcp.tool
def find_movies(title: str = None, genre: str = None, actor: str = None, year: int = None, min_rating: float = None, limit: int = 10):
    """Read/Search: Find movies with filters. (actor param kept for compatibility; not stored in SQLite schema)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    query = """
    SELECT movies.title, movies.director, movies.year, movies.rating, genres.name
    FROM movies
    LEFT JOIN genres ON movies.genre_id = genres.id
    WHERE 1=1
    """
    params = []

    if title:
        query += " AND movies.title LIKE ?"
        params.append(f"%{title}%")
    if genre:
        query += " AND genres.name = ?"
        params.append(genre)
    if year:
        query += " AND movies.year = ?"
        params.append(year)
    if min_rating is not None:
        query += " AND movies.rating >= ?"
        params.append(min_rating)

    if actor:
        query += " AND 1=0"  

    query += " ORDER BY movies.rating DESC LIMIT ?"
    params.append(int(limit))

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [
        {"title": r[0], "director": r[1], "year": r[2], "rating": r[3], "genre": r[4]}
        for r in results
    ]

@mcp.tool
def update_rating(title: str, new_rating: float):
    """Update: Update rating by exact title."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE movies SET rating=? WHERE title=?", (new_rating, title))
    conn.commit()
    changed = cursor.rowcount
    conn.close()
    if changed == 0:
        raise ValueError(f"Movie '{title}' not found.")
    return {"ok": True, "message": f"Rating updated for '{title}'."}

@mcp.tool
def delete_movie(title: str):
    """Delete: Delete movie by exact title."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE title=?", (title,))
    conn.commit()
    changed = cursor.rowcount
    conn.close()
    if changed == 0:
        raise ValueError(f"Movie '{title}' not found.")
    return {"ok": True, "message": f"Movie '{title}' deleted."}

@mcp.tool
def count_movies(genre: str = None, year: int = None, min_rating: float = None):
    """Read: Count movies matching criteria."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = """
    SELECT COUNT(*)
    FROM movies
    LEFT JOIN genres ON movies.genre_id = genres.id
    WHERE 1=1
    """
    params = []
    if genre:
        query += " AND genres.name = ?"
        params.append(genre)
    if year:
        query += " AND movies.year = ?"
        params.append(year)
    if min_rating is not None:
        query += " AND movies.rating >= ?"
        params.append(min_rating)

    cursor.execute(query, params)
    total = cursor.fetchone()[0]
    conn.close()
    return total

@mcp.tool
def get_top_movies(year: int = None, genre: str = None, limit: int = 5):
    """Read: Get top-rated movies with optional filters."""
    return find_movies(genre=genre, year=year, min_rating=None, limit=limit)

@mcp.tool
def get_movie_details(title: str):
    """Read: Get full details for a specific movie (by exact title)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT movies.title, movies.director, movies.year, movies.rating, genres.name, movies.created_at
    FROM movies
    LEFT JOIN genres ON movies.genre_id = genres.id
    WHERE movies.title = ?
    """, (title,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "title": row[0],
        "director": row[1],
        "year": row[2],
        "rating": row[3],
        "genre": row[4],
        "created_at": row[5],
    }

@mcp.resource("collection://stats")
def collection_stats():
    """Resource: quick stats for Claude to read."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM movies")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT ROUND(AVG(rating), 2) FROM movies")
    avg = cursor.fetchone()[0]

    cursor.execute("""
    SELECT g.name, COUNT(*) as c
    FROM movies m
    LEFT JOIN genres g ON m.genre_id = g.id
    GROUP BY g.name
    ORDER BY c DESC
    """)
    by_genre = [{"genre": r[0], "count": r[1]} for r in cursor.fetchall()]

    conn.close()
    return {"total_movies": total, "average_rating": avg, "by_genre": by_genre}

@mcp.prompt("movie_assistant")
def movie_assistant_prompt():
    return """
You are a Movie Database assistant.

Your role is to help users manage their movie collection using available MCP tools.

Available actions:
- Add a movie (title, director, year, rating, genre)
- Search movies by title, genre, year or rating
- Update movie rating
- Delete a movie
- Count movies by filters
- Show collection statistics

Examples of valid requests:
- Add a movie Interstellar directed by Christopher Nolan, year 2014, rating 8.6, genre Sci-Fi
- Find movies with rating above 8
- Update rating of Inception to 9.0
- Delete movie The Dark Knight
- Show collection stats

Always use the appropriate MCP tool to perform actions.
"""

if __name__ == "__main__":
    mcp.run()


