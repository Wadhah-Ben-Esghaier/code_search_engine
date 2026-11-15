from sqlmodel import SQLModel, Field


class Page(SQLModel, table=True):
    __tablename__ = "page"

    id: int = Field(primary_key=True)
    title: str
    text: str

class Term(SQLModel, table=True):
    __tablename__ = "term"

    id: int | None = Field(default=None, primary_key=True)
    term: str = Field(index=True, unique=True) 

class TermFrequency(SQLModel, table=True):
    __tablename__ = "term_frequency"

    term_id: int = Field(foreign_key="term.id", primary_key=True, index=True)
    page_id: int = Field(foreign_key="page.id", primary_key=True, index=True)
    frequency: float

