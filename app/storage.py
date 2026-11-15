from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session, create_engine, select, func
from .models import Page, Term, TermFrequency
import math
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "search.db"

engine = create_engine(
    "sqlite:///" + DB_PATH.as_posix(),
    connect_args={"check_same_thread": False},
)

def create_tables() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)

def fetch_page(page_id: int) -> Page | None:
    with Session(engine) as session:
        return session.get(Page, page_id)

@dataclass
class SearchHit:
    id: int
    title: str
    score: float


def search(term: str, limit: int = 10) -> list[SearchHit]:
    term = term.strip().lower()

    if not term or limit <= 0:
        return []

    with Session(engine) as session:
        num_pages = session.exec(select(func.count()).select_from(Page)).one()

        count_statement = select(func.count()).select_from(TermFrequency)
        count_statement = count_statement.join(Term, Term.id == TermFrequency.term_id)
        count_statement = count_statement.where(Term.term == term, TermFrequency.frequency > 0)
        num_matches = session.exec(count_statement).one()

        if num_matches == 0:
            return []

        idf = math.log10(num_pages / num_matches)

        statement = select(Page.id, Page.title, TermFrequency.frequency)
        statement = statement.select_from(TermFrequency)
        statement = statement.join(Page, Page.id == TermFrequency.page_id)
        statement = statement.join(Term, Term.id == TermFrequency.term_id)
        statement = statement.where(Term.term == term, TermFrequency.frequency > 0)
        statement = statement.order_by(TermFrequency.frequency.desc(), Page.id)
        statement = statement.limit(limit)

        rows = session.exec(statement).all()

        return [SearchHit(id=page_id, title=title, score=frequency * idf) for page_id, title, frequency in rows]
