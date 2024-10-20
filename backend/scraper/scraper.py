import re
import string
from typing import Any

import bs4
import httpx
from bs4 import BeautifulSoup, SoupStrainer
from sqlalchemy import select
from tqdm import tqdm

from database.database import Database
from datamodels.models import Character, CharacterData


class NarutoWikiScraper:
    def __init__(self):
        self.db = Database()
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
        hrefs = []
        tag: bs4.Tag
        for tag in soup:
            if "href" in tag.attrs:
                hrefs.append((f'{self.wiki_url}{tag["href"]}', tag["title"]))

        return hrefs

    @staticmethod
    def extract_character_data(character_page: str, name: str, url: str) -> Character:
        """Parse character page to extract character and associated data."""
        soup = BeautifulSoup(
            character_page, "html.parser", parse_only=SoupStrainer("div")
        )
        container = soup.find_all("div", {"class": "mw-parser-output"})

        summary, personality = [], []
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
            # First paragraph is always the summary
            tag_1, tag_2, tag_3 = "Summary", None, None
            curr_text: list[str] = []

            tag: bs4.Tag
            for tag in parsed_content:
                if (text := tag.text.strip()) and not (
                    text.startswith("See also: ") or text.startswith("Main article: ")
                ):
                    if tag.name == "h2":
                        # Save previous section before changing tags
                        if curr_text and tag_1:
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
                    elif tag.name == "h3":
                        tag_2 = text.replace("[]", "")
                        tag_3 = None
                    elif tag.name == "h4":
                        tag_3 = text.replace("[]", "")
                    elif tag.name == "p":
                        clean = re.sub(r"\[\d+]", "", text)  # Remove reference marks
                        curr_text.append(clean)

                        if tag_1 == "Summary":
                            clean = re.sub(r"\([^)]*\)", "", clean)
                            clean = re.sub(r"\s\s+", " ", clean)
                            summary.append(clean)
                        elif tag_1 == "Personality":
                            personality.append(clean)

            # Add remaining text after last iteration
            if curr_text:
                character_data = CharacterData(
                    text=" ".join(curr_text),
                    tag_1=tag_1,
                    tag_2=tag_2,
                    tag_3=tag_3,
                )
                character_data_list.append(character_data)

        # Create the Character instance
        character = Character(
            name=name,
            href=url,
            image_url=image_url,
            summary=" ".join(summary),
            personality=" ".join(personality),
            data=[data.model_dump() for data in character_data_list],
            data_length=sum([len(data.text) for data in character_data_list]),
        )

        return character

    async def scrape_all_characters(self) -> None:
        character_count = self.db.session.exec(select(Character)).all()
        if len(character_count) == 0:
            characters = await self.fetch_all_characters()
            self.db.session.bulk_save_objects(characters)
            self.db.session.commit()
