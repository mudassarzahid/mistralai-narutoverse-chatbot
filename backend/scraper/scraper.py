import re
import string
from typing import Any

import httpx
from bs4 import BeautifulSoup, SoupStrainer
from tqdm import tqdm

from datamodels.models import Character, CharacterData


class NarutoWikiScraper:
    def __init__(self):
        self.wiki_url = "https://naruto.fandom.com"

    @staticmethod
    async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
        """Fetch page content for a given URL and return the text."""
        response = await client.get(url)
        response.raise_for_status()
        return response.text

    async def fetch_character_details(
        self, client: httpx.AsyncClient, url: str, name: str
    ) -> Character:
        """Fetch and parse character details from the individual character page."""
        character_page = await self.fetch_page(client, url)
        character = self.extract_character_data(character_page, name, url)
        return character

    async def fetch_characters_by_letter(
        self,
        client: httpx.AsyncClient,
        letter: str,
        seen_character_urls: set,
    ) -> list[Character]:
        """Fetch and parse all characters for a specific letter category."""
        base_url = f"{self.wiki_url}/wiki/Category:Characters?from={letter}"
        category_page = await self.fetch_page(client, base_url)
        character_hrefs = self.parse_character_list(category_page)
        characters = []

        for url, name in character_hrefs:
            if url not in seen_character_urls:
                character = await self.fetch_character_details(client, url, name)
                characters.append(character)
                seen_character_urls.add(url)

        return characters

    async def fetch_all_characters(self) -> list[Character]:
        """Main function to fetch all characters from the Naruto wiki."""
        all_characters = []
        seen_character_urls: set[str] = set()
        letters = list(string.ascii_uppercase) + ["%C2%A1"]

        async with httpx.AsyncClient() as client:
            for letter in tqdm(letters):
                characters = await self.fetch_characters_by_letter(
                    client, letter, seen_character_urls
                )
                all_characters.extend(characters)

        return all_characters

    def parse_character_list(self, page_content: str) -> list[tuple[str, Any]]:
        """Extract character URLs from the category page."""
        soup = BeautifulSoup(
            page_content,
            "html.parser",
            parse_only=SoupStrainer("a", class_="category-page__member-link"),
        )
        return [
            (f'{self.wiki_url}{a["href"]}', a["title"])
            for a in soup
            if "href" in a.attrs
        ]

    @staticmethod
    def extract_character_data(character_page: str, name: str, url: str) -> Character:
        """Parse character page to extract character and associated data."""
        soup = BeautifulSoup(
            character_page, "html.parser", parse_only=SoupStrainer("div")
        )
        container = soup.find_all("div", {"class": "mw-parser-output"})

        summary = None
        image_url = None
        character_data_list = []

        for content in container:
            parsed_content = BeautifulSoup(
                str(content),
                "html.parser",
                parse_only=SoupStrainer(["p", "h2", "h3", "h4", "td"]),
            )
            if td := parsed_content.find("td", {"class": "imagecell"}):
                # Extract image URL
                image_url = re.sub(
                    r"(?i)\.(png|jpg|jpeg).*", r".\1", td.find("img")["src"]
                )
            curr_text: list[str] = []
            tag_1, tag_2, tag_3 = "Summary", None, None

            for element in parsed_content:
                if (text := element.text.strip()) and not (
                    text.startswith("See also: ") or text.startswith("Main article: ")
                ):
                    if element.name == "h2":
                        if (
                            curr_text and tag_1
                        ):  # Save previous section before changing tags
                            character_data = CharacterData(
                                text=" ".join(curr_text),
                                tag_1=tag_1,
                                tag_2=tag_2,
                                tag_3=tag_3,
                            )
                            character_data_list.append(character_data)
                        # Start a new section
                        tag_1 = text.replace("[]", "")
                        tag_2 = None
                        tag_3 = None
                        curr_text = []
                    elif element.name == "h3":
                        tag_2 = text.replace("[]", "")
                        tag_3 = None
                    elif element.name == "h4":
                        tag_3 = text.replace("[]", "")
                    elif element.name == "p":
                        clean = re.sub(r"\[\d+]", "", text)  # Remove reference marks
                        curr_text.append(clean)
                        if not summary:
                            summary = re.sub(
                                r"\([^)]*\)", "", clean
                            )  # First paragraph as summary

            # After loop ends, add remaining text
            if curr_text:
                character_data = CharacterData(
                    text=" ".join(curr_text),
                    tag_1=tag_1,
                    tag_2=tag_2,
                    tag_3=tag_3,
                )
                character_data_list.append(character_data)

        # Create the Character instance with UUID
        character = Character(
            name=name,
            href=url,
            image_url=image_url,
            summary=summary,
            data=[data.model_dump() for data in character_data_list],
        )

        return character
