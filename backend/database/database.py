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
    """Database handler for managing interactions with an SQLite database using SQLModel.

    Args:
        db_file (str): The path to the SQLite db file.
            Defaults to `NARUTO_WIKI_DB_FILE`.
    """

    def __init__(self, db_file: str = NARUTO_WIKI_DB_FILE) -> None:
        """Initializes the Database class with an SQLite engine and session.

        Args:
            db_file (str, optional): The path to the SQLite database file.
                Defaults to NARUTO_WIKI_DB_FILE.
        """
        sqlite_url = f"sqlite:///{db_file}"
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=connect_args)
        self.session = Session(self.engine)
        self.create_db_and_tables()

    def create_db_and_tables(self) -> None:
        """Creates the database and all necessary tables."""
        SQLModel.metadata.create_all(self.engine)

    def get(self, params: IsAQueryParams) -> list[dict[str, Any]]:
        """Fetches records from the database based on query parameters.

        Args:
            params (IsAQueryParams): An instance of QueryParams that defines
                the columns, order, offset, and limit for the query.

        Returns:
            list[dict[str, Any]]: A list of dictionaries representing the fetched rows.
        """
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
        id_key: str = "id",
    ) -> IsAnSQLModel:
        """Fetches a single entity from the database by its ID.

        Args:
            entity_id (int): The ID of the entity to fetch.
            model (Type[IsAnSQLModel]): The SQLModel class to query.
            id_key (str, optional): The column name to filter by. Defaults to 'id'.

        Raises:
            NotFoundError: If the entity is not found.

        Returns:
            IsAnSQLModel: The fetched entity model instance.
        """
        entity = self.session.exec(
            select(model).where(getattr(model, id_key) == entity_id)
        ).first()

        if not entity:
            raise NotFoundError(
                detail=f"{model.__name__} with {entity_id=} not found.",
            )

        return entity  # type:ignore

    def create(self, model: IsAnSQLModel) -> IsAnSQLModel:
        """Creates a new entity in the database.

        Args:
            model (IsAnSQLModel): The model class to instantiate.

        Returns:
            IsAnSQLModel: The created model instance.
        """
        with self.session as session:
            session.add(model)
            session.commit()
            session.refresh(model)

        return model

    def update(
        self, model: IsAnSQLModel, updated_fields: dict[str, Any]
    ) -> IsAnSQLModel:
        """Updates an existing entity in the database.

        Args:
            model (IsAnSQLModel): The model instance to update.
            updated_fields (dict[str, Any]): A dictionary containing fields to update.

        Returns:
            IsAnSQLModel: The updated model instance with refreshed data.
        """
        with self.session as session:
            for key, value in updated_fields.items():
                setattr(model, key, value)
            session.add(model)
            session.commit()
            session.refresh(model)

        return model

    def delete_by_id(
        self, entity_id: int, model: Type[IsAnSQLModel], id_key: str = "id"
    ) -> None:
        """Deletes an entity from the database by its ID.

        Args:
            entity_id (int): The ID of the entity to delete.
            model (Type[IsAnSQLModel]): The SQLModel class to query.
            id_key (str, optional): The column name to filter by. Defaults to 'id'.

        Raises:
            HTTPException: If the entity is not found.
        """
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
