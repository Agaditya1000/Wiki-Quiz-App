"""
Wikipedia article scraper using BeautifulSoup.
Fetches and parses Wikipedia pages, extracting structured content.
"""

import re
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup


@dataclass
class ScrapedArticle:
    """Structured data extracted from a Wikipedia article."""

    url: str
    title: str
    summary: str
    sections: list[str] = field(default_factory=list)
    full_text: str = ""
    raw_html: str = ""


# Section headings to skip (meta / non-content sections)
SKIP_SECTIONS = {
    "See also",
    "References",
    "External links",
    "Further reading",
    "Notes",
    "Bibliography",
    "Sources",
    "Citations",
    "Footnotes",
}

# User agent to mimic a real browser for Wikipedia requests
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _clean_text(text: str) -> str:
    """Remove extra whitespace and citation markers like [1], [2], etc."""
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def scrape_wikipedia(url: str) -> ScrapedArticle:
    """
    Scrape a Wikipedia article URL and return structured content.

    Args:
        url: Full Wikipedia article URL.

    Returns:
        ScrapedArticle with title, summary, sections, full text, and raw HTML.

    Raises:
        ValueError: If the URL is not a valid Wikipedia article.
        ConnectionError: If the page cannot be fetched.
    """
    # Validate URL format
    if "wikipedia.org/wiki/" not in url:
        raise ValueError(
            f"Invalid Wikipedia URL: {url}. "
            "URL must be in the format https://<lang>.wikipedia.org/wiki/<Article>"
        )

    # Fetch the page
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch Wikipedia page: {e}")

    raw_html = response.text
    soup = BeautifulSoup(raw_html, "html.parser")

    # Extract article title from the page heading
    title_tag = soup.find("h1", {"id": "firstHeading"})
    if not title_tag:
        title_tag = soup.find("span", {"class": "mw-page-title-main"})
    title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

    # Get the main content area
    content_div = soup.find("div", {"id": "mw-content-text"})
    if not content_div:
        raise ValueError("Could not find article content on the page.")

    # Extract summary (first paragraph with substantial text)
    summary = ""
    for p in content_div.find_all("p", recursive=True):
        text = _clean_text(p.get_text())
        if len(text) > 80:  # Skip short / empty paragraphs
            summary = text
            break

    # Extract section headings and full text content
    sections: list[str] = []
    text_parts: list[str] = [summary]

    for heading in content_div.find_all(["h2", "h3"]):
        headline = heading.find("span", class_="mw-headline")
        if not headline:
            # Newer Wikipedia markup uses a different structure
            headline_id = heading.get("id", "")
            heading_text = heading.get_text(strip=True)
            # Remove "[edit]" suffix
            heading_text = heading_text.replace("[edit]", "").strip()
        else:
            heading_text = headline.get_text(strip=True)

        if not heading_text or heading_text in SKIP_SECTIONS:
            continue

        if heading.name == "h2":
            sections.append(heading_text)

        # Collect text from the section (siblings until next heading)
        section_text_parts = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "p":
                clean = _clean_text(sibling.get_text())
                if clean:
                    section_text_parts.append(clean)

        if section_text_parts:
            text_parts.append(f"\n\n## {heading_text}\n" + " ".join(section_text_parts))

    full_text = "\n".join(text_parts)

    # Truncate to ~8000 chars to stay within LLM token limits
    if len(full_text) > 8000:
        full_text = full_text[:8000] + "\n\n[Content truncated for processing...]"

    return ScrapedArticle(
        url=url,
        title=title,
        summary=summary if summary else "No summary available.",
        sections=sections if sections else ["General"],
        full_text=full_text,
        raw_html=raw_html,
    )


def get_article_title(url: str) -> str:
    """
    Quick fetch to get just the article title for URL preview.

    Args:
        url: Wikipedia article URL.

    Returns:
        The article title string.
    """
    if "wikipedia.org/wiki/" not in url:
        raise ValueError("Not a valid Wikipedia URL")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch page: {e}")

    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("h1", {"id": "firstHeading"})
    if not title_tag:
        title_tag = soup.find("span", {"class": "mw-page-title-main"})
    return title_tag.get_text(strip=True) if title_tag else "Unknown"
