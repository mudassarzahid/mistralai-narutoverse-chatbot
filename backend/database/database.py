import re
import string
from typing import Optional

import httpx
from bs4 import BeautifulSoup, SoupStrainer
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute
from sqlmodel import Session, SQLModel, create_engine, select
from tqdm import tqdm

from datamodels.models import Character

sqlite_file_name = "database/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def bulk_insert_characters(characters: list[Character]):
    session = get_session()
    session.bulk_save_objects(characters)
    session.commit()


def get_characters(
    filters: dict[str, str], model: SQLModel, limit: Optional[int] = None
) -> list[Character]:
    session = get_session()
    # Start the query
    statement = select(model)

    # List of dynamic filters to apply
    filter_conditions = []

    for column_filter, value in filters.items():
        if "." in column_filter:
            column_name, operation = column_filter.split(".")
        else:
            column_name, operation = column_filter, None

        # Get the column from the model dynamically
        column = getattr(model, column_name, None)
        if not isinstance(column, InstrumentedAttribute):
            raise ValueError(
                f"Column '{column_name}' does not exist on the model {model.__name__}."
            )

        # Handle different operations dynamically
        if operation == "length-eq" or operation == "length":
            filter_conditions.append(func.length(column) == int(value))  # Length equals
        elif operation == "length-gt":
            filter_conditions.append(
                func.length(column) > int(value)
            )  # Length greater than
        elif operation == "length-lt":
            filter_conditions.append(
                func.length(column) < int(value)
            )  # Length less than
        elif operation == "contains":
            filter_conditions.append(column.contains(value))  # Partial match
        elif operation == "startswith":
            filter_conditions.append(column.startswith(value))  # Starts with
        elif operation == "!":
            filter_conditions.append(column.is_not(None))  # Non-null check
        else:
            # Default is exact match (e.g., name=Sasuke)
            filter_conditions.append(column == value)

    # Apply all filter conditions
    if filter_conditions:
        statement = statement.where(*filter_conditions)

    # Apply limit if provided
    if limit:
        statement = statement.limit(limit)

    # Execute query and return results
    return session.exec(statement).all()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
