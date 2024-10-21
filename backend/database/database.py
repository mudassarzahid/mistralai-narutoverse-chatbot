from http import HTTPStatus
from typing import Any, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import Row
from sqlmodel import Session, SQLModel, create_engine, select

from datamodels.models import QueryParams
from utils.consts import NARUTO_WIKI_DB_FILE
from utils.exceptions import NotFoundError

IsAnSQLModel = TypeVar("IsAnSQLModel", bound=SQLModel)
IsAQueryParams = TypeVar("IsAQueryParams", bound=QueryParams)


class Database:
    def __init__(self, db_file: str = NARUTO_WIKI_DB_FILE) -> None:
        sqlite_url = f"sqlite:///{db_file}"
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=connect_args)
        self.session = Session(self.engine)
        self.create_db_and_tables()

    def create_db_and_tables(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    def get(self, params: IsAQueryParams) -> list[dict[str, Any]]:
        result = self.session.exec(
            select(*params.columns)
            .order_by(*params.order_by)
            .offset(params.offset)
            .limit(params.limit)
        ).all()

        # If only one column is selected the row does not contain column information
        return [
            row._asdict() if isinstance(row, Row) else {params.columns[0].key: row}
            for row in result
        ]

    def get_by_id(
        self,
        entity_id: int,
        model: Type[IsAnSQLModel],
        id_key="id",
    ) -> IsAnSQLModel:
        entity = self.session.exec(
            select(model).where(getattr(model, id_key) == entity_id)
        ).first()
        if not entity:
            raise NotFoundError(
                detail=f"{model.__name__} with {entity_id=} not found.",
            )
        return entity

    def create(self, model: IsAnSQLModel) -> IsAnSQLModel:
        with self.session as session:
            session.add(model)
            session.commit()
            session.refresh(model)

        return model

    def update(
        self, model: IsAnSQLModel, updated_fields: dict[str, Any]
    ) -> IsAnSQLModel:
        with self.session as session:
            for key, value in updated_fields.items():
                setattr(model, key, value)
            session.add(model)
            session.commit()
            session.refresh(model)
        return model

    def delete_by_id(
        self, entity_id: int, model: Type[IsAnSQLModel], id_key="id"
    ) -> None:
        entity = self.session.exec(
            select(model).where(getattr(model, id_key) == entity_id)
        ).first()
        if not entity:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"{model.__name__} with {entity_id=} not found.",
            )
        self.session.delete(entity)
        self.session.commit()
