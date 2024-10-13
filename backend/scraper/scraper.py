import re
import string

import httpx
from bs4 import BeautifulSoup, SoupStrainer
from tqdm import tqdm

from datamodels.models import Character


async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    """Fetch page content for a given URL and return the text."""
    response = await client.get(url)
    response.raise_for_status()
    return response.text


def parse_character_list(page_content: str, wiki_url: str) -> list[str]:
    """Extract character URLs from the category page."""
    soup = BeautifulSoup(
        page_content,
        "html.parser",
        parse_only=SoupStrainer("a", class_="category-page__member-link"),
    )
    return [f'{wiki_url}{a["href"]}' for a in soup if "href" in a.attrs]


def extract_character_data(character_page: str) -> dict:
    """Parse character page to extract relevant data like summary, image URL, etc."""
    soup = BeautifulSoup(character_page, "html.parser", parse_only=SoupStrainer("div"))
    container = soup.find_all("div", {"class": "mw-parser-output"})

    chunks = []
    summary = None
    img = None

    for content in container:
        parsed_content = BeautifulSoup(
            str(content),
            "html.parser",
            parse_only=SoupStrainer(["p", "h2", "h3", "h4", "td"]),
        )
        td = parsed_content.find("td", {"class": "imagecell"})
        if td:
            img = td.find("img")["src"]  # Extract image URL

        curr = []
        for element in parsed_content:
            if (text := element.text.strip()) and not (
                text.startswith("See also: ") or text.startswith("Main article: ")
            ):
                if element.name == "h2":
                    if len(curr) > 1:
                        chunks.append(curr)
                    clean = (
                        text.replace("[]", "")
                        .replace(":", "")
                        .replace(" ", "_")
                        .lower()
                    )
                    if clean == "in_other_media":  # Stop parsing at irrelevant sections
                        break
                    curr = [clean]
                elif element.name in ["h3", "h4", "p"]:
                    if element.name in ["h3", "h4"]:
                        clean = f'<{text.replace("[]", "")}>'
                    else:
                        clean = re.sub(r"\[\d+]", "", text)  # Remove reference marks
                    if not summary:
                        summary = clean
                    curr.append(clean)

    data = {chunk[0]: " ".join(chunk[1:]) for chunk in chunks}
    data["summary"] = summary
    data["image_url"] = img
    return data


async def fetch_character_details(
    client: httpx.AsyncClient, url: str, name: str
) -> Character:
    """Fetch and parse character details from the individual character page."""
    character_page = await fetch_page(client, url)
    character_data = extract_character_data(character_page)
    character_data.update({"name": name, "href": url})
    return Character(**character_data)


async def fetch_characters_by_letter(
    client: httpx.AsyncClient, wiki_url: str, letter: str, seen_character_urls: set
) -> list[Character]:
    """Fetch and parse all characters for a specific letter category."""
    base_url = f"{wiki_url}/wiki/Category:Characters?from={letter}"
    category_page = await fetch_page(client, base_url)

    character_urls = parse_character_list(category_page, wiki_url)

    characters = []
    for url in character_urls:
        if url not in seen_character_urls:
            name = url.split("/")[-1].replace("_", " ")  # Extract name from URL
            character = await fetch_character_details(client, url, name)
            characters.append(character)
            seen_character_urls.add(url)
            return characters

    return characters


async def fetch_all_characters() -> list[Character]:
    """Main function to fetch all characters from the Naruto wiki."""
    wiki_url = "https://naruto.fandom.com"
    all_characters = []
    seen_character_urls = set()
    letters = list(string.ascii_uppercase) + ["%C2%A1"]

    async with httpx.AsyncClient() as client:
        for letter in tqdm(letters[:1]):
            characters = await fetch_characters_by_letter(
                client, wiki_url, letter, seen_character_urls
            )
            all_characters.extend(characters)

    return all_characters
