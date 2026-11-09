"""Reading Log MCP server: search books, keep a library, write reviews."""
import json
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("reading-log")
DATA = Path(__file__).resolve().parent.parent / "data" / "library.json"
OL = "https://openlibrary.org"


def load() -> list[dict]:
    return json.loads(DATA.read_text()) if DATA.exists() else []


def save(books: list[dict]) -> None:
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(books, indent=2))


def text_of(desc) -> str:
    # Open Library descriptions are either a string or {"value": "..."}
    return desc.get("value", "") if isinstance(desc, dict) else (desc or "")


# ---------- TOOLS: actions Claude can take ----------
@mcp.tool()
def search_books(query: str, limit: int = 5) -> list[dict]:
    """Search Open Library for books by title or author."""
    r = httpx.get(
        f"{OL}/search.json",
        params={"q": query, "limit": limit,
                "fields": "key,title,author_name,first_publish_year,cover_i"},
        timeout=15,
    )
    r.raise_for_status()
    return [
        {"id": d["key"].split("/")[-1], "title": d.get("title"),
         "author": ", ".join(d.get("author_name", [])),
         "year": d.get("first_publish_year"), "cover_id": d.get("cover_i")}
        for d in r.json()["docs"]
    ]


@mcp.tool()
def get_book_details(work_id: str) -> dict:
    """Get the description and subjects for an Open Library work id (e.g. OL45883W)."""
    r = httpx.get(f"{OL}/works/{work_id}.json", timeout=15)
    r.raise_for_status()
    w = r.json()
    return {"id": work_id, "title": w.get("title"),
            "description": text_of(w.get("description")),
            "subjects": w.get("subjects", [])[:8],
            "cover_id": (w.get("covers") or [None])[0]}


@mcp.tool()
def add_to_library(work_id: str, title: str, author: str,
                   cover_id: int | None = None, description: str = "") -> str:
    """Add a book to the reading log."""
    books = load()
    if any(b["id"] == work_id for b in books):
        return f"'{title}' is already in your library."
    books.append({"id": work_id, "title": title, "author": author,
                  "cover_id": cover_id, "description": description,
                  "status": "want to read", "rating": None, "review": ""})
    save(books)
    return f"Added '{title}'."


@mcp.tool()
def save_review(work_id: str, rating: int, review: str,
                status: str = "finished") -> str:
    """Save a 1-5 rating and a short review for a book in the library."""
    if not 1 <= rating <= 5:
        return "Rating must be between 1 and 5."
    books = load()
    for b in books:
        if b["id"] == work_id:
            b.update(rating=rating, review=review, status=status)
            save(books)
            return f"Saved review for '{b['title']}'."
    return "Book not found. Add it to the library first."


# ---------- RESOURCES: data Claude can read ----------
@mcp.resource("library://books")
def all_books() -> str:
    """Every book in the reading log."""
    return json.dumps(load(), indent=2)


@mcp.resource("library://books/{work_id}")
def one_book(work_id: str) -> str:
    """A single book, including your review."""
    return json.dumps(next((b for b in load() if b["id"] == work_id), {}), indent=2)


# ---------- PROMPTS: reusable templates ----------
@mcp.prompt()
def book_report(work_id: str) -> str:
    """Draft a short book report for a book in the library."""
    return (f"Read the resource library://books/{work_id}. Write a one-page book "
            "report with a two-sentence summary, my rating, and three questions "
            "for discussion. Keep my own review wording where possible.")


if __name__ == "__main__":
    mcp.run()  # stdio transport
