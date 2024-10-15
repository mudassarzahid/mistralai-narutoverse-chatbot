from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute
from sqlmodel import Session, SQLModel, create_engine, select

from datamodels.models import Character, CharacterData

sqlite_file_name = "database/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def bulk_insert_characters(characters: list[Character]) -> None:
    session = get_session()
    session.bulk_save_objects(characters)
    session.commit()


def search_characters(
    filters: dict[str, str],
    model: SQLModel,
) -> list[dict[str, Any]]:
    session = get_session()
    # Start the query
    statement = select(model)

    # List of dynamic filters to apply
    filter_conditions = []
    get_details = False
    limit = 100
    offset = 0

    # TODO use pydantic validation
    for column_filter, value in filters.items():
        if column_filter == "get_details":
            if value.lower() == "true":
                get_details = True
            continue
        if column_filter == "limit":
            limit = int(value)
            continue
        if column_filter == "offset":
            offset = int(value)
            continue

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

    if offset:
        statement = statement.offset(offset)

    # Execute the query to get characters
    characters = session.exec(statement).all()

    result = []
    for character in characters:
        if get_details:
            # Query the CharacterData table for related data
            data_statement = select(CharacterData).where(
                CharacterData.character_id == character.id
            )
            character_data = session.exec(data_statement).all()

            # Add character and related details (if any) to the result
            result.append({"character": character, "details": character_data})
        else:
            result.append(character)

    return result


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def is_db_empty():
    session = get_session()
    character_count = session.exec(select(Character)).all()

    return len(character_count) == 0


def get_session():
    return Session(engine)
