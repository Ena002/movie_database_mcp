# Movie Database MCP Server (SQLite)

Ovaj projekat predstavlja implementaciju vlastitog MCP (Model Context Protocol) servera koristeći Python i SQLite bazu podataka.

Server je povezan sa Claude Desktop aplikacijom i omogućava upravljanje kolekcijom filmova putem prirodnog jezika.

---

## Opis projekta

Cilj projekta je izrada funkcionalnog MCP servera koji rješava realan problem – upravljanje ličnom bazom filmova.

Server omogućava:

- Dodavanje filmova
- Pretragu filmova
- Ažuriranje ocjene
- Brisanje filmova
- Brojanje filmova
- Prikaz najbolje ocijenjenih filmova
- Prikaz statistike kolekcije

Podaci se čuvaju u lokalnoj SQLite bazi.

---

## Arhitektura sistema

Claude Desktop  
        │  
        ▼  
FastMCP server (Python)  
        │  
        ▼  
SQLite baza podataka (movies.db)

Claude komunicira sa serverom putem MCP protokola, a server koristi SQLite kao relacijski datastore.

---

## Struktura baze podataka

Baza koristi relacijski model sa dvije tabele:

- `genres` – čuva nazive žanrova
- `movies` – čuva informacije o filmovima i sadrži strani ključ (genre_id) koji referencira tabelu `genres`

Jedan žanr može imati više filmova (1:N relacija).

Ovakav dizajn sprječava dupliranje podataka i prati principe relacijskih baza podataka.

---

## MCP alati (Tools)

Server implementira sljedeće alate:

- add_movie
- find_movies
- update_rating
- delete_movie
- count_movies
- get_top_movies
- get_movie_details

Svaki alat ima definisane ulazne parametre i error handling.

---

## MCP Resource

Resource:

collection://stats

Vraća:

- Ukupan broj filmova
- Prosječnu ocjenu
- Broj filmova po žanru

---

## Instalacija (macOS)

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python movie_mcp.py