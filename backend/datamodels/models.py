from sqlmodel import Field, SQLModel


class Character(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    href: int | None = Field(default=None, index=True)
    image_url: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    background: str | None = Field(default=None)
    personality: str | None = Field(default=None)
    appearance: str | None = Field(default=None)
    abilities: str | None = Field(default=None)
    part_i: str | None = Field(default=None)
    interlude: str | None = Field(default=None)
    part_ii: str | None = Field(default=None)
    blank_period: str | None = Field(default=None)
    new_era_part_i: str | None = Field(default=None)
    new_era_part_ii: str | None = Field(default=None)
    flashforward: str | None = Field(default=None)
