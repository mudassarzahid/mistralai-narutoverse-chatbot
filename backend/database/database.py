from http import HTTPStatus
from typing import Any, Type

from fastapi import HTTPException
from sqlalchemy import Row
from sqlmodel import SQLModel, create_engine
from sqlmodel import Session, select

from datamodels.models import Character
from datamodels.models import QueryParams
from scraper.scraper import NarutoWikiScraper


class Database:
    def __init__(self):
        sqlite_file_name = "database/database.db"
        sqlite_url = f"sqlite:///{sqlite_file_name}"
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=connect_args)
        self.session = Session(self.engine)

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)

    async def scrape_all_characters(self):
        character_count = self.session.exec(select(Character)).all()
        if len(character_count) == 0:
            scraper = NarutoWikiScraper()
            characters = await scraper.fetch_all_characters()
            self.session.bulk_save_objects(characters)
            self.session.commit()

    def get(self, params: QueryParams) -> list[dict[str, Any]]:
        result = self.session.exec(
            select(*params.columns)
            .order_by(*params.order_by)
            .offset(params.offset)
            .limit(params.limit)
        ).all()

        rows = []
        for row in result:
            if isinstance(row, Row):
                rows.append(row._asdict())
            else:
                # If only one column is selected the row does not contain column information
                rows.append({params.columns[0].key: row})

        return rows

    def get_by_id(self, entity_id: int, model: Type[SQLModel]) -> SQLModel:
        entity = self.session.exec(
            select(model).where(model.id == entity_id)
        ).first()
        if not entity:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"{model.__name__} with {entity_id=} not found.",
            )
        return entity

    def create(self, model: Type[SQLModel]) -> Type[SQLModel]:
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def delete_by_id(self, entity_id: int, model: Type[SQLModel]):
        entity = self.session.exec(
            select(model).where(model.id == entity_id)
        ).first()
        if not entity:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"{model.__name__} with {entity_id=} not found.",
            )
        self.session.delete(entity)
        self.session.commit()
