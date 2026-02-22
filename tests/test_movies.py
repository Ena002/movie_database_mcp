import os
import sys
import tempfile

# Dodaj root folder projekta da pytest može importovati movie_mcp.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Koristi privremenu bazu za testove
_tmp = tempfile.NamedTemporaryFile(delete=False)
os.environ["MOVIE_DB_PATH"] = _tmp.name

from movie_mcp import init_db, add_movie, find_movies, update_rating, delete_movie


def setup_module():
    init_db()


def test_add_movie():
    res = add_movie(
        title="Test Movie",
        director="Test Director",
        year=2024,
        rating=8.5,
        genre="TestGenre",
    )
    assert res["ok"] is True

    movies = find_movies(title="Test Movie")
    assert len(movies) == 1
    assert movies[0]["title"] == "Test Movie"


def test_update_rating():
    res = update_rating("Test Movie", 9.0)
    assert res["ok"] is True

    movies = find_movies(title="Test Movie")
    assert movies[0]["rating"] == 9.0


def test_delete_movie():
    res = delete_movie("Test Movie")
    assert res["ok"] is True

    movies = find_movies(title="Test Movie")
    assert len(movies) == 0
